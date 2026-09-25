import openpyxl, datetime, re, psycopg2
from psycopg2.extras import DictCursor

wb = openpyxl.load_workbook('conciliacion gasolina/JDJ 1a Y 2a SEMANA AGOSTO.xlsx', data_only=True)
ws = wb['AGOSTO 2026']

levet_s33 = []
for r in range(50, 94):
    t = ws.cell(r, 2).value
    f = ws.cell(r, 3).value
    p = ws.cell(r, 4).value
    c = ws.cell(r, 6).value
    o = ws.cell(r, 7).value
    l = ws.cell(r, 8).value
    pr = ws.cell(r, 9).value
    imp = ws.cell(r, 10).value
    f_str = f.strftime('%Y-%m-%d') if hasattr(f, 'strftime') else str(f)
    levet_s33.append({
        'row': r,
        'ticket': str(t),
        'fecha': f_str,
        'placa': str(p or '').strip().upper(),
        'conductor': str(c or '').strip().upper(),
        'obra': str(o or '').strip().upper(),
        'litros': round(float(l or 0), 3),
        'precio': round(float(pr or 0), 2),
        'importe': round(float(imp or 0), 2)
    })

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)
cur.execute('''
    SELECT id, fecha, semana, conductor, vehiculo, placa, obra_destino, litros, costo_por_litro, importe_total, gasolineria, folio_conciliacion
    FROM gasolina.consumos
    WHERE semana IN ('33', 'Semana 33') OR (fecha >= '2026-08-10' AND fecha <= '2026-08-16')
    ORDER BY id
''')
db_s33 = []
for r in cur.fetchall():
    db_s33.append({
        'id': r['id'],
        'fecha': str(r['fecha']),
        'conductor': str(r['conductor'] or '').strip().upper(),
        'vehiculo': str(r['vehiculo'] or '').strip().upper(),
        'placa': str(r['placa'] or '').strip().upper(),
        'obra': str(r['obra_destino'] or '').strip().upper(),
        'litros': round(float(r['litros'] or 0), 3),
        'importe': round(float(r['importe_total'] or 0), 2),
        'gasolineria': str(r['gasolineria'] or '').strip().upper(),
        'folio': str(r['folio_conciliacion'] or '')
    })

# Matching 1 a 1 sin reutilizar registros de la BD
matched_items = []
unmatched_levet = []
used_db_ids = set()

for idx, lr in enumerate(levet_s33, 1):
    p_lev = re.sub(r'[^A-Z0-9]', '', lr['placa'])
    found = None
    reason = ''
    
    # 1. Reglas directas específicas por ticket
    if lr['ticket'] == '416693': # Lowboy Bryan Chavez $500
        for dr in db_s33:
            if dr['id'] == 144 and dr['id'] not in used_db_ids:
                found = dr; reason = 'Lowboy Motors Bryan Chavez ($500.00)'; break
    elif lr['ticket'] == '416729': # Eq Menor / Cortadora $1,000
        for dr in db_s33:
            if dr['id'] == 417 and dr['id'] not in used_db_ids:
                found = dr; reason = 'Cortadora de Concreto ($1,000.00)'; break
    elif lr['ticket'] == '416459': # Cristobal Silva $1,500
        for dr in db_s33:
            if dr['id'] == 437 and dr['id'] not in used_db_ids:
                found = dr; reason = 'Cristobal Silva LKV206D ($1,500.00)'; break
    elif lr['ticket'] == '418502': # Juan Carlos Nazar $1,144.50
        for dr in db_s33:
            if dr['id'] == 409 and dr['id'] not in used_db_ids:
                found = dr; reason = 'Juan Carlos Nazar PCW9238 ($1,144.50)'; break
    elif lr['ticket'] == '416727': # Juan Carlos Nazar $893.08
        for dr in db_s33:
            if dr['id'] == 452 and dr['id'] not in used_db_ids:
                found = dr; reason = 'Juan Carlos Nazar PCW9238 ($893.08)'; break
    elif lr['ticket'] == '417998': # Jack Planta Pegaso $1,000.00
        for dr in db_s33:
            if dr['id'] == 453 and dr['id'] not in used_db_ids:
                found = dr; reason = 'Jack Planta Pegaso PCU7482 ($1,000.00)'; break
    elif lr['ticket'] == '418541': # Jack Planta Pegaso $700.00
        for dr in db_s33:
            if dr['id'] == 454 and dr['id'] not in used_db_ids:
                found = dr; reason = 'Jack Planta Pegaso PAT8298 ($700.00)'; break
    elif lr['ticket'] == '416424': # Carlos Alarcon $1,369.44
        for dr in db_s33:
            if dr['id'] == 134 and dr['id'] not in used_db_ids:
                found = dr; reason = 'Carlos Alarcon MHL758A (Ticket $1,369.44 vs BD $1,200.00)'; break
                
    # 2. Regla general: Placa exacta (o con variacion tipográfica) + Importe similar (+/- $5)
    if not found:
        for dr in db_s33:
            if dr['id'] in used_db_ids: continue
            p_db = re.sub(r'[^A-Z0-9]', '', dr['placa'])
            plate_match = (p_lev == p_db and len(p_lev) > 2) or (p_lev.replace('L','Y') == p_db.replace('L','Y'))
            amt_diff = abs(lr['importe'] - dr['importe'])
            if plate_match and amt_diff <= 5.0:
                found = dr
                reason = f"Placa ({lr['placa']}) + Importe (${lr['importe']})"
                break
                
    # 3. Regla de respaldo: Conductor coincidente + Importe exacto (+/- $5) en LEVET
    if not found:
        for dr in db_s33:
            if dr['id'] in used_db_ids: continue
            c_words_l = set(w for w in lr['conductor'].split() if len(w) > 3)
            c_words_d = set(w for w in dr['conductor'].split() if len(w) > 3)
            amt_diff = abs(lr['importe'] - dr['importe'])
            if c_words_l & c_words_d and amt_diff <= 5.0 and ('LEVET' in dr['gasolineria'] or not dr['gasolineria']):
                found = dr
                reason = f"Conductor ({lr['conductor']}) + Importe (${lr['importe']})"
                break
                
    if found:
        used_db_ids.add(found['id'])
        matched_items.append({'index': idx, 'levet': lr, 'db': found, 'motivo': reason})
    else:
        unmatched_levet.append({'index': idx, 'levet': lr})

tot_lev_lts = sum(r['litros'] for r in levet_s33)
tot_lev_imp = sum(r['importe'] for r in levet_s33)

tot_mat_lts = sum(m['levet']['litros'] for m in matched_items)
tot_mat_imp = sum(m['levet']['importe'] for m in matched_items)

tot_unm_lts = sum(u['levet']['litros'] for u in unmatched_levet)
tot_unm_imp = sum(u['levet']['importe'] for u in unmatched_levet)

print("="*100)
print("AUDITORIA Y CONCILIACION DE GASOLINA: ESTADO DE CUENTA LEVET VS SISTEMA FENIX")
print("PERIODO: SEMANA 33 (10 AL 15 DE AGOSTO DE 2026)")
print("="*100)
print(f"Total Cargas Reportadas por Gasolineria LEVET:          {len(levet_s33):2d} cargas | {tot_lev_lts:8.2f} L | ${tot_lev_imp:10.2f} MXN")
print(f"Total Cargas COINCIDENTES (Registradas en Fenix):       {len(matched_items):2d} cargas | {tot_mat_lts:8.2f} L | ${tot_mat_imp:10.2f} MXN")
print(f"TOTAL CARGAS QUE LEVET REPORTA QUE NO TENEMOS EN BD:    {len(unmatched_levet):2d} CARGAS | {tot_unm_lts:8.2f} L | ${tot_unm_imp:10.2f} MXN")
print("="*100)

print("\n" + "#"*100)
print(f"LISTADO DETALLADO DE LAS {len(unmatched_levet)} CARGAS RESTANTES QUE LEVET REPORTA Y NO ESTAN EN LA BD:")
print("#"*100)
print(f"{'#':<3} | {'Ticket':<8} | {'Fecha':<10} | {'Placas':<10} | {'Conductor Reportado':<22} | {'Obra Destino':<28} | {'Litros':<8} | {'Importe':<10}")
print("-" * 100)
for i, item in enumerate(unmatched_levet, 1):
    u = item['levet']
    print(f"{i:<3} | {u['ticket']:<8} | {u['fecha']:<10} | {u['placa']:<10} | {u['conductor']:<22} | {u['obra']:<28} | {u['litros']:>7.2f}L | ${u['importe']:>9.2f}")
print("-" * 100)
print(f"IMPORTE TOTAL FALTANTE (CARGOS NO REGISTRADOS EN FENIX): ${tot_unm_imp:,.2f} MXN ({tot_unm_lts:,.2f} Litros)\n")
