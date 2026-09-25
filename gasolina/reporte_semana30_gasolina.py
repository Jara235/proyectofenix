import psycopg2
from psycopg2.extras import DictCursor
import openpyxl

def generate_report():
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

    print(f"Total registros Semana 30: {len(db_rows)}")

    # Load authorizations from official Excel
    wb = openpyxl.load_workbook(r'c:\Users\JOSE\Desktop\Control_Gasolina_Semana_30_Oficial.xlsx', data_only=True)
    ws = wb['SEMANA 30 GASOLINA']

    auth_records = []
    for r in range(4, 200):
        resp = ws.cell(r, 1).value
        centro = ws.cell(r, 2).value
        veh = ws.cell(r, 3).value
        placa = str(ws.cell(r, 4).value or '').strip().upper()
        monto_auth = ws.cell(r, 5).value
        if resp and (monto_auth is not None):
            auth_records.append({
                'responsable': str(resp).strip(),
                'centro': str(centro or 'N/A').strip(),
                'vehiculo': str(veh or 'N/A').strip(),
                'placa': placa if placa else 'S/P',
                'importe_autorizado': float(monto_auth or 0)
            })

    # Group consumos by Placa
    consumos_by_placa = {}
    for r in db_rows:
        plc = (r['placa'] or 'S/P').strip().upper()
        veh = (r['vehiculo'] or 'N/A').strip()
        if plc not in consumos_by_placa:
            consumos_by_placa[plc] = {
                'vehiculo': veh,
                'litros': 0.0,
                'importe': 0.0,
                'cargas': 0,
                'conductores': set(),
                'obras': set()
            }
        consumos_by_placa[plc]['litros'] += float(r['litros'] or 0)
        consumos_by_placa[plc]['importe'] += float(r['importe_total'] or 0)
        consumos_by_placa[plc]['cargas'] += 1
        if r['conductor']: consumos_by_placa[plc]['conductores'].add(r['conductor'].strip())
        if r['obra_destino']: consumos_by_placa[plc]['obras'].add(r['obra_destino'].strip())

    # Map authorizations by Placa and Responsable
    auth_by_placa = {}
    for a in auth_records:
        plc = a['placa']
        if plc not in auth_by_placa:
            auth_by_placa[plc] = {
                'responsable': a['responsable'],
                'centro': a['centro'],
                'vehiculo': a['vehiculo'],
                'importe_autorizado': 0.0
            }
        auth_by_placa[plc]['importe_autorizado'] += a['importe_autorizado']

    # Combine all unique placas
    all_placas = sorted(list(set(consumos_by_placa.keys()) | set(auth_by_placa.keys())))

    # Format Markdown Report
    report = []
    report.append("# ⛽ Reporte Oficial de Gasolina - Semana 30\n")

    # SECTION 1: DETALLE DE REGISTROS (36 CONSUMOS)
    report.append("## 1. Detalle de Registros de Consumo (Base de Datos - Semana 30)")
    report.append(f"Total de registros capturados en sistema: **{len(db_rows)}**\n")
    report.append("| # | Folio | Fecha | Obra Destino | Vehículo | Placa | Conductor / Responsable | Litros | P.U. | Importe Total |")
    report.append("|---|-------|-------|--------------|----------|-------|-------------------------|-------:|------|---------------|")

    tot_litros_db = 0.0
    tot_importe_db = 0.0

    for idx, r in enumerate(db_rows, 1):
        folio = r['folio_conciliacion'] or ''
        fecha = str(r['fecha'] or '')
        obra = r['obra_destino'] or 'SIN OBRA'
        veh = r['vehiculo'] or 'N/A'
        placa = r['placa'] or 'S/P'
        cond = r['conductor'] or 'No Identificado'
        litros = float(r['litros'] or 0)
        costo = float(r['costo_por_litro'] or 0)
        importe = float(r['importe_total'] or 0)

        tot_litros_db += litros
        tot_importe_db += importe

        report.append(f"| {idx} | `{folio}` | {fecha} | {obra} | {veh} | **{placa}** | {cond} | {litros:,.2f} L | ${costo:,.2f} | **${importe:,.2f}** |")

    report.append(f"| **TOTAL** | | | | | | | **{tot_litros_db:,.2f} L** | | **${tot_importe_db:,.2f}** |\n")

    # SECTION 2: SUMA DE CONSUMOS POR PLACA
    report.append("## 2. Consumo Total Agrupado por Placa / Vehículo")
    report.append("| Placa | Vehículo | Cargas | Conductor(es) | Obra(s) | Total Litros | Total Importe ($) |")
    report.append("|-------|----------|-------:|---------------|---------|-------------:|------------------:|")

    for plc in sorted(consumos_by_placa.keys()):
        c = consumos_by_placa[plc]
        cond_str = ", ".join(c['conductores']) if c['conductores'] else "N/I"
        obra_str = ", ".join(c['obras']) if c['obras'] else "SIN OBRA"
        report.append(f"| **{plc}** | {c['vehiculo']} | {c['cargas']} | {cond_str} | {obra_str} | {c['litros']:,.2f} L | **${c['importe']:,.2f}** |")

    report.append(f"| **TOTAL** | | **{sum(c['cargas'] for c in consumos_by_placa.values())}** | | | **{tot_litros_db:,.2f} L** | **${tot_importe_db:,.2f}** |\n")

    # SECTION 3: COMPARATIVO VS AUTORIZACIONES
    report.append("## 3. Comparativo de Consumo vs. Monto Autorizado Semanal")
    report.append("| Placa | Responsable / Centro | Vehículo | Importe Autorizado ($) | Consumo Real ($) | Consumo Real (L) | Diferencia / Remanente ($) | Estatus |")
    report.append("|-------|----------------------|----------|-----------------------:|-----------------:|-----------------:|---------------------------:|---------|")

    tot_auth_global = 0.0
    tot_cons_global = 0.0

    for plc in all_placas:
        auth_info = auth_by_placa.get(plc, {'responsable': 'Sin Asignar', 'centro': 'N/A', 'vehiculo': 'N/A', 'importe_autorizado': 0.0})
        cons_info = consumos_by_placa.get(plc, {'vehiculo': auth_info['vehiculo'], 'litros': 0.0, 'importe': 0.0, 'cargas': 0})

        monto_auth = auth_info['importe_autorizado']
        monto_cons = cons_info['importe']
        litros_cons = cons_info['litros']
        diferencia = monto_auth - monto_cons

        tot_auth_global += monto_auth
        tot_cons_global += monto_cons

        if monto_auth == 0 and monto_cons > 0:
            estatus = "⚠️ **Sin Fondo**"
        elif diferencia < 0:
            estatus = "❌ **Excedido**"
        elif monto_cons == 0:
            estatus = "⚪ **Sin Consumo**"
        else:
            estatus = "✅ **En Regla**"

        veh_disp = cons_info['vehiculo'] if cons_info['vehiculo'] != 'N/A' else auth_info['vehiculo']
        resp_disp = f"{auth_info['responsable']} ({auth_info['centro']})" if auth_info['centro'] != 'N/A' else auth_info['responsable']

        report.append(f"| **{plc}** | {resp_disp} | {veh_disp} | ${monto_auth:,.2f} | ${monto_cons:,.2f} | {litros_cons:,.2f} L | ${diferencia:,.2f} | {estatus} |")

    tot_dif_global = tot_auth_global - tot_cons_global
    st_global = "✅ **En Regla**" if tot_dif_global >= 0 else "❌ **Excedido Global**"
    report.append(f"| **TOTAL GLOBAL** | | | **${tot_auth_global:,.2f}** | **${tot_cons_global:,.2f}** | **{tot_litros_db:,.2f} L** | **${tot_dif_global:,.2f}** | {st_global} |")

    with open(r'C:\Users\JOSE\.gemini\antigravity\brain\f3511922-47fb-4fdf-9cb3-6eae6dade26d\reporte_gasolina_semana30.md', 'w', encoding='utf-8') as f:
        f.write("\n".join(report))

    print("Report written successfully to artifact!")

if __name__ == '__main__':
    generate_report()
