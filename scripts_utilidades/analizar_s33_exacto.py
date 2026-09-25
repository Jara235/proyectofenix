import openpyxl, datetime, re, psycopg2
from psycopg2.extras import DictCursor

# 1. Leer Levet Excel
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

# 2. Leer DB
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

# Matching inteligente
matches = []
unmatched_lev = []
used_db = set()

for lr in levet_s33:
    best_match = None
    match_reason = ''
    
    for dr in db_s33:
        if dr['id'] in used_db:
            continue
        p1 = re.sub(r'[^A-Z0-9]', '', lr['placa'])
        p2 = re.sub(r'[^A-Z0-9]', '', dr['placa'])
        plate_match = (p1 == p2 and len(p1) > 2) or (p1.replace('L','Y') == p2.replace('L','Y'))
        amt_diff = abs(lr['importe'] - dr['importe'])
        
        # Exact plate + amount match
        if plate_match and amt_diff <= 5.0:
            best_match = dr
            match_reason = f"Placa ({lr['placa']} / {dr['placa']}) + Importe (${lr['importe']} vs ${dr['importe']})"
            break
            
        # Conductor match + amount match
        c_words_l = set(w for w in lr['conductor'].split() if len(w) > 3)
        c_words_d = set(w for w in dr['conductor'].split() if len(w) > 3)
        if c_words_l & c_words_d and amt_diff <= 5.0 and ('LEVET' in dr['gasolineria'] or not dr['gasolineria']):
            best_match = dr
            match_reason = f"Conductor ({lr['conductor']}) + Importe (${lr['importe']})"
            break
            
        # Lowboy
        if ('LOWBOY' in lr['placa'] or 'LOWBOY' in lr['conductor']) and ('LOWBOY' in dr['vehiculo'] or 'LOWBOY' in dr['conductor']) and amt_diff <= 5.0:
            best_match = dr
            match_reason = f"Lowboy + Importe (${lr['importe']})"
            break
            
        # Equipo menor / Cortadora
        if ('MENOR' in lr['placa'] or 'CORTADORA' in dr['conductor']) and amt_diff <= 5.0:
            best_match = dr
            match_reason = f"Equipo Menor + Importe (${lr['importe']})"
            break

    # Casos especiales de correspondencia directa
    if not best_match:
        if lr['ticket'] == '418502': # Placa vacia Levet = Juan Carlos Nazar $1,144.50
            for dr in db_s33:
                if dr['id'] == 409 and dr['id'] not in used_db:
                    best_match = dr
                    match_reason = "Ticket 418502 sin placa en Levet = Vale DB #409 ($1,144.50)"
                    break
        elif lr['ticket'] == '416424': # Carlos Alarcon $1,369.44 vs Autorizado $1,200
            for dr in db_s33:
                if dr['id'] == 134 and dr['id'] not in used_db:
                    best_match = dr
                    match_reason = "Carlos Alarcon MHL758A (Ticket $1,369.44 vs Autorizado $1,200.00)"
                    break

    if best_match:
        used_db.add(best_match['id'])
        matches.append({'levet': lr, 'db': best_match, 'motivo': match_reason})
    else:
        unmatched_lev.append(lr)

print("="*90)
print(f"RESUMEN DE CONCILIACIÓN SEMANA 33 (10 AL 15 DE AGOSTO 2026)")
print("="*90)
tot_lev_lts = sum(r['litros'] for r in levet_s33)
tot_lev_imp = sum(r['importe'] for r in levet_s33)
tot_mat_lts = sum(m['levet']['litros'] for m in matches)
tot_mat_imp = sum(m['levet']['importe'] for m in matches)
tot_fal_lts = sum(u['litros'] for u in unmatched_lev)
tot_fal_imp = sum(u['importe'] for u in unmatched_lev)

print(f"Total registros facturados por Gasolinería LEVET:     {len(levet_s33):2d} cargas | {tot_lev_lts:8.2f} L | ${tot_lev_imp:10.2f} MXN")
print(f"Total registros que SÍ coinciden con nuestra BD:       {len(matches):2d} cargas | {tot_mat_lts:8.2f} L | ${tot_mat_imp:10.2f} MXN")
print(f"TOTAL REGISTROS QUE LEVET REPORTA Y NO TENEMOS EN BD:  {len(unmatched_lev):2d} CARGAS | {tot_fal_lts:8.2f} L | ${tot_fal_imp:10.2f} MXN")
print("="*90)

print("\n>>> LISTA DE LAS CARGAS REPORTADAS POR LEVET QUE NO TENEMOS EN NUESTRA BASE DE DATOS:")
print("-" * 110)
print(f"{'#':<3} | {'Ticket':<8} | {'Fecha':<10} | {'Placas':<10} | {'Conductor':<22} | {'Obra Destino':<28} | {'Litros':<8} | {'Importe':<10}")
print("-" * 110)
for idx, u in enumerate(unmatched_lev, 1):
    print(f"{idx:<3} | {u['ticket']:<8} | {u['fecha']:<10} | {u['placa']:<10} | {u['conductor']:<22} | {u['obra']:<28} | {u['litros']:>7.2f}L | ${u['importe']:>9.2f}")
print("-" * 110)
print(f"TOTAL NO REGISTRADAS: {len(unmatched_lev)} cargas por un monto de ${tot_fal_imp:,.2f} MXN ({tot_fal_lts:,.2f} Litros)\n")

print("\n>>> CARGAS CONCILIADAS EXITOSAMENTE (MUESTRA):")
for idx, m in enumerate(matches[:10], 1):
    lr = m['levet']
    dr = m['db']
    print(f"{idx:2d}. Ticket: {lr['ticket']} | Placa: {lr['placa']} | Conductor Levet: {lr['conductor']} vs BD: {dr['conductor']} | Monto: ${lr['importe']} | Motivo: {m['motivo']}")

unmatched_db = [dr for dr in db_s33 if dr['id'] not in used_db]
print(f"\n>>> REGISTROS EN NUESTRA BD QUE NO ESTÁN EN LEVET (Total {len(unmatched_db)}):")
for idx, dr in enumerate(unmatched_db, 1):
    print(f"{idx:2d}. ID #{dr['id']:<3} | Fecha: {dr['fecha']} | Gasolinera: {dr['gasolineria']:<8} | Placa: {dr['placa']:<10} | Conductor: {dr['conductor']:<25} | Importe: ${dr['importe']:>8.2f}")
