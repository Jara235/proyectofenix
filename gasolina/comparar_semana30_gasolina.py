import openpyxl
import psycopg2
from psycopg2.extras import DictCursor
import datetime

def compare_semana30():
    excel_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\CONCILIACIÓN COMBUSTIBLE GASOLINERAS.xlsx'
    wb = openpyxl.load_workbook(excel_path, data_only=True)

    if 'SEMANA 30' not in wb.sheetnames:
        print("ERROR: Sheet 'SEMANA 30' not found in Excel!")
        return

    ws = wb['SEMANA 30']
    print(f"Sheet 'SEMANA 30' loaded successfully (max_row: {ws.max_row}, max_col: {ws.max_column})")

    # 1. Parse Excel Catalog and Daily Charges for Semana 30
    excel_catalog = {} # key: placa or (responsable, unidad) -> dict
    excel_charges = [] # list of daily charge dicts

    curr_resp = None
    curr_centro = None

    # Date headers from row 2
    dates = []
    for c in range(7, ws.max_column + 1, 3):
        val = ws.cell(2, c).value
        if isinstance(val, datetime.datetime) or isinstance(val, datetime.date):
            d_str = val.strftime('%Y-%m-%d')
            dates.append((c, d_str))

    print("Dates found in Excel header:", dates)

    for r in range(4, ws.max_row + 1):
        num = ws.cell(r, 1).value
        resp = ws.cell(r, 2).value
        centro = ws.cell(r, 3).value
        unidad = ws.cell(r, 4).value
        placa = ws.cell(r, 5).value
        monto_auth = ws.cell(r, 6).value

        if resp is not None and str(resp).strip() != '':
            curr_resp = str(resp).strip()
        if centro is not None and str(centro).strip() != '':
            curr_centro = str(centro).strip()

        plc_clean = str(placa).strip().upper() if placa else None
        und_str = str(unidad).strip() if unidad else None

        if plc_clean in ('NONE', 'S/P', '', 'N/A', 'PLACAS', 'AUTORIZADO') or (plc_clean and len(plc_clean) > 12):
            plc_clean = None

        if und_str and und_str.upper() in ('UNIDAD / EQUIPO', 'TOTAL', 'CONSUMO', 'NONE', 'N/A', ''):
            und_str = None

        if not und_str and not plc_clean and not resp:
            continue

        try:
            monto_num = float(monto_auth or 0)
        except (ValueError, TypeError):
            monto_num = 0.0

        item_key = plc_clean if plc_clean else (f"{curr_resp}_{und_str}" if curr_resp else und_str)

        excel_catalog[r] = {
            'row_num': r,
            'responsable': curr_resp,
            'centro_trabajo': curr_centro,
            'unidad_equipo': und_str,
            'placa': plc_clean or 'S/P',
            'monto_autorizado': monto_num
        }

        # Check daily charges (Levet = c, Mobile = c+1, Si Vale = c+2)
        for col_start, d_str in dates:
            val_levet = ws.cell(r, col_start).value
            val_mobile = ws.cell(r, col_start + 1).value
            val_sivale = ws.cell(r, col_start + 2).value

            for source_name, val in [('LEVET', val_levet), ('MOBILE', val_mobile), ('SI VALE', val_sivale)]:
                if val is not None:
                    try:
                        amt = float(val)
                        if amt > 0:
                            excel_charges.append({
                                'row_num': r,
                                'fecha': d_str,
                                'proveedor': source_name,
                                'responsable': curr_resp,
                                'centro_trabajo': curr_centro,
                                'unidad_equipo': und_str,
                                'placa': plc_clean or 'S/P',
                                'importe': amt
                            })
                    except (ValueError, TypeError):
                        pass

    print(f"Total catalog rows parsed in Excel Semana 30: {len(excel_catalog)}")
    print(f"Total daily charges parsed in Excel Semana 30: {len(excel_charges)}")

    # 2. Fetch Database Records for Semana 30
    conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
    cur = conn.cursor(cursor_factory=DictCursor)

    cur.execute('''
        SELECT id, folio_conciliacion, fecha, obra_destino, vehiculo, placa, conductor, litros, costo_por_litro, importe_total, observaciones
        FROM gasolina.consumos
        WHERE semana::text = '30'
        ORDER BY fecha, id
    ''')
    db_rows = [dict(r) for r in cur.fetchall()]
    conn.close()

    print(f"Total DB records for Semana 30: {len(db_rows)}")

    # 3. Compare DB records with Excel Semana 30 Sheet
    # Group DB by Placa
    db_by_placa = {}
    for r in db_rows:
        plc = (r['placa'] or 'S/P').strip().upper()
        if plc not in db_by_placa:
            db_by_placa[plc] = []
        db_by_placa[plc].append(r)

    # Group Excel Charges by Placa
    excel_by_placa = {}
    for c in excel_charges:
        plc = c['placa']
        if plc not in excel_by_placa:
            excel_by_placa[plc] = []
        excel_by_placa[plc].append(c)

    all_placas = sorted(list(set(db_by_placa.keys()) | set(excel_by_placa.keys())))

    # Generate Markdown Report Artifact
    md = []
    md.append("# ⛽ Comparativo Detallado de Gasolina - Semana 30")
    md.append("## Archivo Excel (`CONCILIACIÓN COMBUSTIBLE GASOLINERAS.xlsx` -> Pestaña `SEMANA 30`) vs. Base de Datos (`gasolina.consumos`)\n")

    tot_db_amt = sum(float(r['importe_total'] or 0) for r in db_rows)
    tot_excel_amt = sum(c['importe'] for c in excel_charges)

    md.append(f"- **Total Registros en Base de Datos:** `{len(db_rows)} cargas` | **Total Importe BD:** `${tot_db_amt:,.2f} MXN`")
    md.append(f"- **Total Cargas en Pestaña Excel SEMANA 30:** `{len(excel_charges)} cargas` | **Total Importe Excel:** `${tot_excel_amt:,.2f} MXN`")
    md.append(f"- **Diferencia Global de Consumo:** `${abs(tot_db_amt - tot_excel_amt):,.2f} MXN`\n")

    md.append("---")
    md.append("### 1. Resumen Comparativo por Placa / Vehículo")
    md.append("| Placa | Vehículo | Responsable / Centro Excel | Cargas BD | Importe BD ($) | Cargas Excel | Importe Excel ($) | Diferencia ($) | Estatus Conciliación |")
    md.append("|-------|----------|----------------------------|----------:|---------------:|-------------:|------------------:|---------------:|----------------------|")

    for plc in all_placas:
        db_list = db_by_placa.get(plc, [])
        ex_list = excel_by_placa.get(plc, [])

        sum_db = sum(float(r['importe_total'] or 0) for r in db_list)
        sum_ex = sum(c['importe'] for c in ex_list)
        diff = sum_db - sum_ex

        veh_str = db_list[0]['vehiculo'] if db_list else (ex_list[0]['unidad_equipo'] if ex_list else 'N/A')
        resp_str = f"{ex_list[0]['responsable']} ({ex_list[0]['centro_trabajo']})" if ex_list else 'N/I'

        if abs(diff) < 0.05:
            st = "✅ **Coincidencia Exacta**"
        elif sum_ex == 0:
            st = "🔵 **Solo en BD**"
        elif sum_db == 0:
            st = "🟡 **Solo en Excel**"
        else:
            st = f"⚠️ **Diferencia (${diff:+,.2f})**"

        md.append(f"| **`{plc}`** | {veh_str} | {resp_str} | {len(db_list)} | **${sum_db:,.2f}** | {len(ex_list)} | **${sum_ex:,.2f}** | ${diff:,.2f} | {st} |")

    md.append(f"| **TOTAL** | | | **{len(db_rows)}** | **${tot_db_amt:,.2f}** | **{len(excel_charges)}** | **${tot_excel_amt:,.2f}** | **${tot_db_amt - tot_excel_amt:,.2f}** | |")

    md.append("\n---\n")

    md.append("### 2. Detalle Registro por Registro: BD vs. Pestaña SEMANA 30 Excel")
    md.append("| # BD | Folio BD | Fecha | Placa | Vehículo | Conductor / Resp. (BD ➡️ Excel) | Obra / Centro (BD ➡️ Excel) | Importe BD ($) | Importe Excel ($) | Estatus |")
    md.append("|-----:|----------|-------|-------|----------|---------------------------------|-----------------------------|---------------:|------------------:|---------|")

    matched_db_ids = set()

    for idx, r in enumerate(db_rows, 1):
        r_id = r['id']
        folio = r['folio_conciliacion'] or ''
        fecha = str(r['fecha'] or '')
        plc = (r['placa'] or 'S/P').strip().upper()
        veh = r['vehiculo'] or 'N/A'
        cond_db = r['conductor'] or 'N/I'
        obra_db = r['obra_destino'] or 'SIN OBRA'
        imp_db = float(r['importe_total'] or 0)

        # Match with excel charges on same fecha, placa/veh, close amount
        matched_ex = None
        ex_candidates = [c for c in excel_charges if c['fecha'] == fecha and (c['placa'] == plc or (c['unidad_equipo'] and c['unidad_equipo'].upper() == veh.upper()))]

        if ex_candidates:
            # find candidate closest in amount
            ex_candidates.sort(key=lambda c: abs(c['importe'] - imp_db))
            if abs(ex_candidates[0]['importe'] - imp_db) < 5.0:
                matched_ex = ex_candidates[0]

        if matched_ex:
            imp_ex = matched_ex['importe']
            cond_ex = matched_ex['responsable'] or cond_db
            obra_ex = matched_ex['centro_trabajo'] or obra_db
            
            cond_disp = cond_db if cond_db == cond_ex else f"{cond_db} ➡️ **{cond_ex}**"
            obra_disp = obra_db if obra_db == obra_ex else f"{obra_db} ➡️ **{obra_ex}**"

            st_row = "✅ **Coincide**" if abs(imp_db - imp_ex) < 0.05 else "⚠️ **Diferencia Mínima**"
            md.append(f"| {idx} | `{folio}` | {fecha} | **`{plc}`** | {veh} | {cond_disp} | {obra_disp} | **${imp_db:,.2f}** | **${imp_ex:,.2f}** | {st_row} |")
        else:
            md.append(f"| {idx} | `{folio}` | {fecha} | **`{plc}`** | {veh} | {cond_db} | {obra_db} | **${imp_db:,.2f}** | *Sin Carga en Excel* | 🔵 **Solo en BD** |")

    art_path = r'C:\Users\JOSE\.gemini\antigravity\brain\f3511922-47fb-4fdf-9cb3-6eae6dade26d\comparativo_semana30_gasolina.md'
    with open(art_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(md))

    print(f"Report written successfully to artifact: {art_path}")

if __name__ == '__main__':
    compare_semana30()
