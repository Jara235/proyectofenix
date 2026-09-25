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
        'ticket': str(t).strip(),
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
    SELECT id, folio_conciliacion, fecha, semana, conductor, vehiculo, placa, obra_destino, litros, costo_por_litro, importe_total, gasolineria, estatus_revision
    FROM gasolina.consumos
    WHERE (semana IN ('33', 'Semana 33') OR (fecha >= '2026-08-10' AND fecha <= '2026-08-16'))
      AND (folio_conciliacion NOT LIKE 'GAS-S33-LEV-PEND-%%' OR folio_conciliacion IS NULL)
    ORDER BY id
''')
db_s33 = cur.fetchall()

matched = []
unmatched = []
used_db = set()

# Explicit ticket / ID matches
explicit_ticket_map = {
    '416727': 452, # Juan Carlos Nazar $893.08
    '417998': 453, # Jack PCU7482 $1,000.00
    '418541': 454, # Jack PAT8298 $700.00
    '418502': 409, # Juan Carlos Nazar $1,144.50
    '416693': 144, # Lowboys $500.00
    '416729': 417, # Cortadora $1000.00
    '416459': 437, # Cristobal Silva $1500.00
    '417001': 446, # Jesus Marin / Carlos Reyes PCU8771 combinado $2,000
    '417002': 446, # Jesus Marin / Carlos Reyes PCU8771 combinado $2,000
    '416427': 476, # Equipo Menor Mexico Toluca $500.00
}

for lr in levet_s33:
    t = lr['ticket']
    found = None
    
    if t in explicit_ticket_map:
        target_id = explicit_ticket_map[t]
        for dr in db_s33:
            if dr['id'] == target_id:
                found = dr
                break
                
    if not found:
        # Match by exact plate + amount within $5
        p_lev = re.sub(r'[^A-Z0-9]', '', lr['placa'])
        for dr in db_s33:
            if dr['id'] in used_db: continue
            p_db = re.sub(r'[^A-Z0-9]', '', str(dr['placa'] or '').upper())
            plate_match = (p_lev == p_db and len(p_lev) > 2) or (p_lev.replace('L','Y') == p_db.replace('L','Y'))
            amt_diff = abs(lr['importe'] - float(dr['importe_total']))
            if plate_match and amt_diff <= 5.0:
                found = dr
                break
                
    if not found:
        # Match by conductor name + amount within $5 in LEVET
        for dr in db_s33:
            if dr['id'] in used_db: continue
            c_words_l = set(w for w in lr['conductor'].split() if len(w) > 3)
            c_words_d = set(w for w in str(dr['conductor'] or '').upper().split() if len(w) > 3)
            amt_diff = abs(lr['importe'] - float(dr['importe_total']))
            if c_words_l & c_words_d and amt_diff <= 5.0 and ('LEVET' in str(dr['gasolineria'] or '').upper() or not dr['gasolineria']):
                found = dr
                break

    if found:
        used_db.add(found['id'])
        matched.append((lr, found))
    else:
        unmatched.append(lr)

tot_lev_lts = sum(r['litros'] for r in levet_s33)
tot_lev_imp = sum(r['importe'] for r in levet_s33)
tot_mat_lts = sum(m[0]['litros'] for m in matched)
tot_mat_imp = sum(m[0]['importe'] for m in matched)
tot_unm_lts = sum(u['litros'] for u in unmatched)
tot_unm_imp = sum(u['importe'] for u in unmatched)

print("="*105)
print(f"AUDITORIA ACTUALIZADA SEMANA 33: ESTADO DE CUENTA LEVET VS SISTEMA FENIX")
print("="*105)
print(f"Total Cargas LEVET:               {len(levet_s33)} tickets | {tot_lev_lts:8.2f} L | ${tot_lev_imp:10.2f} MXN")
print(f"Total Cargas Conciliadas:         {len(matched)} tickets | {tot_mat_lts:8.2f} L | ${tot_mat_imp:10.2f} MXN ({tot_mat_imp/tot_lev_imp*100:.1f}%)")
print(f"TOTAL CARGAS FALTANTES EN BD:     {len(unmatched)} CARGAS  | {tot_unm_lts:8.2f} L | ${tot_unm_imp:10.2f} MXN ({tot_unm_imp/tot_lev_imp*100:.1f}%)")
print("="*105)

print("\n" + "#"*105)
print(f"LISTA OFICIAL DE LAS {len(unmatched)} CARGAS PENDIENTES DE ACLARAR CON LEVET:")
print("#"*105)
print(f"{'#':<3} | {'Ticket':<8} | {'Fecha':<10} | {'Placas':<10} | {'Conductor Reportado':<22} | {'Obra Destino':<26} | {'Litros':<8} | {'Importe':<10}")
print("-" * 105)

for idx, u in enumerate(unmatched, 1):
    print(f"{idx:<3} | {u['ticket']:<8} | {u['fecha']:<10} | {u['placa']:<10} | {u['conductor']:<22} | {u['obra']:<26} | {u['litros']:>7.2f}L | ${u['importe']:>9.2f}")
print("-" * 105)
print(f"TOTAL FALTANTE: {len(unmatched)} cargas | {tot_unm_lts:,.2f} Litros | ${tot_unm_imp:,.2f} MXN\n")
