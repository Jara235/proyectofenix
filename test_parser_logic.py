import os, re, datetime
import openpyxl
from app_admin import get_db

# Let's test the new parser logic against SEMANA 32 files to ensure 100% accuracy
db = get_db()

# Load catalog
cat_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\TAGS\CONTROL TAG.xlsx'
catalog_by_tag = {}
catalog_by_resp = {}
if os.path.exists(cat_path):
    wb_cat = openpyxl.load_workbook(cat_path, data_only=True)
    ws_cat = wb_cat.active
    for r in range(2, ws_cat.max_row + 1):
        raw_tag = str(ws_cat.cell(r, 1).value or '').strip()
        clean_t = re.sub(r'[^A-Za-z0-9]', '', raw_tag).upper()
        resp = str(ws_cat.cell(r, 2).value or '').strip()
        tipo = str(ws_cat.cell(r, 3).value or '').strip()
        placa = str(ws_cat.cell(r, 4).value or '').strip()
        obra = str(ws_cat.cell(r, 5).value or '').strip()
        emp = 'TRD' if ('TRD' in obra.upper() or 'ROCADURA' in obra.upper()) else 'JDJ'
        info = {
            'tag': raw_tag, 'clean_tag': clean_t, 'responsable': resp,
            'tipo_unidad': tipo, 'placas': placa, 'obra_asignada': obra,
            'empresa': emp
        }
        if clean_t: catalog_by_tag[clean_t] = info
        if resp: catalog_by_resp[resp.upper()] = info

print(f"Catalog loaded: {len(catalog_by_tag)} tags, {len(catalog_by_resp)} responsables.")

# Test parsing semana 32 JDJ file
test_file = r'c:\Users\JOSE\Desktop\Proyecto fenix\TAGS\semana32\REPORTE DE MOVIMIENTOS SEMANA 32 JDJ EYC.xlsx'
wb = openpyxl.load_workbook(test_file, data_only=True)
total_parsed = 0
for sheet in wb.sheetnames:
    ws = wb[sheet]
    rows = list(ws.iter_rows(values_only=True))
    if not rows: continue
    hdr_idx = -1
    hdr_map = {}
    for i, r in enumerate(rows[:15]):
        row_strs = [str(c or '').strip().upper() for c in r]
        if any(k in row_strs for k in ['TAG', 'NO.ECONOMICO', 'NO. ECONOMICO', 'FECHA', 'IMPORTE', 'CASETA']):
            hdr_idx = i
            for c_i, col_name in enumerate(row_strs):
                if 'TAG' in col_name and 'tag' not in hdr_map: hdr_map['tag'] = c_i
                elif ('ECONOMICO' in col_name or 'UNIDAD' in col_name) and 'no_economico' not in hdr_map: hdr_map['no_economico'] = c_i
                elif 'FECHA' in col_name and 'fecha' not in hdr_map: hdr_map['fecha'] = c_i
                elif 'HORA' in col_name and 'hora' not in hdr_map: hdr_map['hora'] = c_i
                elif 'CASETA' in col_name and 'caseta' not in hdr_map: hdr_map['caseta'] = c_i
                elif ('IMPORTE' in col_name or 'CARGO' in col_name or 'MONTO' in col_name) and 'importe' not in hdr_map: hdr_map['importe'] = c_i
                elif 'SEMANA' in col_name and 'semana' not in hdr_map: hdr_map['semana'] = c_i
                elif ('OBRA' in col_name or 'CENTRO' in col_name) and 'obra' not in hdr_map: hdr_map['obra'] = c_i
                elif ('RESPONSABLE' in col_name or 'OPERADOR' in col_name) and 'responsable' not in hdr_map: hdr_map['responsable'] = c_i
            break

    print(f"Sheet {sheet}: hdr_idx={hdr_idx}, hdr_map={hdr_map}")
    if hdr_idx == -1: continue

    for r in rows[hdr_idx+1:]:
        if not any(r): continue
        tag_val = str(r[hdr_map['tag']] or '').strip() if 'tag' in hdr_map and hdr_map['tag'] < len(r) else ''
        no_econ_val = str(r[hdr_map['no_economico']] or '').strip() if 'no_economico' in hdr_map and hdr_map['no_economico'] < len(r) else ''
        if not tag_val and not no_econ_val: continue

        raw_imp = r[hdr_map['importe']] if 'importe' in hdr_map and hdr_map['importe'] < len(r) else 0
        try: importe_val = float(raw_imp or 0)
        except: importe_val = 0.0
        if importe_val == 0.0: continue

        total_parsed += 1

print(f"Total rows parsed correctly from test file: {total_parsed}")
db.close()
