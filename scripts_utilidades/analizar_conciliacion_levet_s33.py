import openpyxl, datetime, re
import psycopg2
from psycopg2.extras import DictCursor

def norm_placa(p):
    if not p: return ''
    p_clean = re.sub(r'[^A-Z0-9]', '', str(p).upper())
    return p_clean

# 1. Leer Levet Excel
wb = openpyxl.load_workbook('conciliacion gasolina/JDJ 1a Y 2a SEMANA AGOSTO.xlsx', data_only=True)
ws = wb['AGOSTO 2026']

levet_rows = []
for r in range(5, ws.max_row + 1):
    ticket = ws.cell(r, 2).value
    fecha = ws.cell(r, 3).value
    placa = ws.cell(r, 4).value
    km = ws.cell(r, 5).value
    conductor = ws.cell(r, 6).value
    obra = ws.cell(r, 7).value
    litros = ws.cell(r, 8).value
    precio = ws.cell(r, 9).value
    importe = ws.cell(r, 10).value
    
    if ticket is None and placa is None and importe is None:
        continue
    if isinstance(ticket, str) and ('TOTAL' in ticket.upper() or 'TICKET' in ticket.upper()):
        continue
    if isinstance(placa, str) and 'TOTAL' in placa.upper():
        continue
        
    fecha_str = str(fecha)
    if isinstance(fecha, (datetime.datetime, datetime.date)):
        fecha_str = fecha.strftime('%Y-%m-%d')
        
    try: litros_f = float(litros or 0)
    except: litros_f = 0.0
    try: importe_f = float(importe or 0)
    except: importe_f = 0.0
    try: precio_f = float(precio or 0)
    except: precio_f = 0.0

    rec = {
        'row': r,
        'ticket': str(ticket or '').strip(),
        'fecha': fecha_str,
        'placa_orig': str(placa or '').strip(),
        'placa': norm_placa(placa),
        'conductor': str(conductor or '').strip(),
        'obra': str(obra or '').strip(),
        'litros': round(litros_f, 3),
        'precio': round(precio_f, 2),
        'importe': round(importe_f, 2)
    }
    levet_rows.append(rec)

# 2. Leer DB
conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)
cur.execute('''
    SELECT id, fecha, semana, conductor, vehiculo, placa, obra_destino, litros, costo_por_litro, importe_total, gasolineria, folio_conciliacion, estatus_revision, origen
    FROM gasolina.consumos
    WHERE semana IN ('33', 'Semana 33') OR (fecha >= '2026-08-10' AND fecha <= '2026-08-16')
    ORDER BY id
''')
db_rows = cur.fetchall()
db_list = []
for r in db_rows:
    db_list.append({
        'id': r['id'],
        'fecha': str(r['fecha'] or ''),
        'semana': str(r['semana'] or ''),
        'conductor': str(r['conductor'] or '').strip(),
        'vehiculo': str(r['vehiculo'] or '').strip(),
        'placa_orig': str(r['placa'] or '').strip(),
        'placa': norm_placa(r['placa']),
        'obra': str(r['obra_destino'] or '').strip(),
        'litros': round(float(r['litros'] or 0), 3),
        'costo': round(float(r['costo_por_litro'] or 0), 2),
        'importe': round(float(r['importe_total'] or 0), 2),
        'gasolineria': str(r['gasolineria'] or '').strip().upper(),
        'folio': str(r['folio_conciliacion'] or ''),
        'origen': str(r['origen'] or '')
    })

print("=== TOTALES LEVET (EXCEL) VS SISTEMA FÉNIX (DB) ===")
levet_s33 = [r for r in levet_rows if '2026-08-10' <= r['fecha'] <= '2026-08-16']
lts_lev = sum(r['litros'] for r in levet_s33)
imp_lev = sum(r['importe'] for r in levet_s33)
print(f"Levet Semana 33 (10-15 Ago): {len(levet_s33)} registros | {lts_lev:,.2f} L | ${imp_lev:,.2f} MXN")

lts_db = sum(r['litros'] for r in db_list)
imp_db = sum(r['importe'] for r in db_list)
print(f"DB Total Semana 33: {len(db_list)} registros | {lts_db:,.2f} L | ${imp_db:,.2f} MXN")

db_levet = [r for r in db_list if 'LEVET' in r['gasolineria'] or not r['gasolineria']]
db_mobile = [r for r in db_list if 'MOBILE' in r['gasolineria']]
print(f" - DB Registros LEVET: {len(db_levet)} registros | {sum(r['litros'] for r in db_levet):,.2f} L | ${sum(r['importe'] for r in db_levet):,.2f} MXN")
print(f" - DB Registros MOBILE: {len(db_mobile)} registros | {sum(r['litros'] for r in db_mobile):,.2f} L | ${sum(r['importe'] for r in db_mobile):,.2f} MXN")

# 3. Matching Exhaustivo (Placa + Monto, Conductor + Monto, Placa + Litros)
matched_levet = []
unmatched_levet = []
db_used_ids = set()

# Paso 1: Match Exacto (Placa + Monto +/- $2)
for lr in levet_s33:
    found = None
    for dr in db_list:
        if dr['id'] in db_used_ids:
            continue
        placa_match = False
        if lr['placa'] and dr['placa'] and (lr['placa'] == dr['placa']):
            placa_match = True
        amount_match = abs(lr['importe'] - dr['importe']) <= 2.0
        
        if placa_match and amount_match:
            found = dr
            break
            
    if found:
        db_used_ids.add(found['id'])
        matched_levet.append({'levet': lr, 'db': found, 'tipo': 'MATCH EXACTO (PLACA + MONTO)'})
    else:
        unmatched_levet.append(lr)

# Paso 2: Match por Equipo Menor / Cortadora / Maquinaria sin placa o con coincidencia de monto y conductor
unmatched_levet_p2 = []
for lr in unmatched_levet:
    found = None
    for dr in db_list:
        if dr['id'] in db_used_ids:
            continue
        amount_match = abs(lr['importe'] - dr['importe']) <= 2.0
        
        # Match conductor
        cond_match = False
        if lr['conductor'] and dr['conductor']:
            l_words = [w for w in lr['conductor'].upper().split() if len(w) > 3]
            d_words = [w for w in dr['conductor'].upper().split() if len(w) > 3]
            if set(l_words) & set(d_words):
                cond_match = True
        
        # Match equipo menor
        if 'MENOR' in lr['placa_orig'].upper() and ('CORTADORA' in dr['conductor'].upper() or 'MENOR' in dr['vehiculo'].upper()):
            cond_match = True

        if amount_match and cond_match:
            found = dr
            break
            
    if found:
        db_used_ids.add(found['id'])
        matched_levet.append({'levet': lr, 'db': found, 'tipo': 'MATCH POR MONTO + CONDUCTOR/EQUIPO'})
    else:
        unmatched_levet_p2.append(lr)

# Paso 3: Match por Placa + Litros aproximados
unmatched_levet_p3 = []
for lr in unmatched_levet_p2:
    found = None
    for dr in db_list:
        if dr['id'] in db_used_ids:
            continue
        placa_match = (lr['placa'] and dr['placa'] and lr['placa'] == dr['placa'])
        lts_match = abs(lr['litros'] - dr['litros']) <= 2.0
        if placa_match and lts_match:
            found = dr
            break
            
    if found:
        db_used_ids.add(found['id'])
        matched_levet.append({'levet': lr, 'db': found, 'tipo': 'MATCH POR PLACA + LITROS'})
    else:
        unmatched_levet_p3.append(lr)

# Paso 4: Match con otras semanas (desfase de fecha)
cur.execute('SELECT * FROM gasolina.consumos WHERE semana NOT IN (\'33\', \'Semana 33\')')
other_db_rows = cur.fetchall()
other_db = []
for r in other_db_rows:
    other_db.append({
        'id': r['id'],
        'fecha': str(r['fecha'] or ''),
        'semana': str(r['semana'] or ''),
        'conductor': str(r['conductor'] or '').strip(),
        'vehiculo': str(r['vehiculo'] or '').strip(),
        'placa_orig': str(r['placa'] or '').strip(),
        'placa': norm_placa(r['placa']),
        'obra': str(r['obra_destino'] or '').strip(),
        'litros': round(float(r['litros'] or 0), 3),
        'costo': round(float(r['costo_por_litro'] or 0), 2),
        'importe': round(float(r['importe_total'] or 0), 2),
        'gasolineria': str(r['gasolineria'] or '').strip().upper(),
        'folio': str(r['folio_conciliacion'] or ''),
        'origen': str(r['origen'] or '')
    })

unmatched_final_levet = []
matched_other_weeks = []
for lr in unmatched_levet_p3:
    found = None
    for dr in other_db:
        placa_match = (lr['placa'] and dr['placa'] and lr['placa'] == dr['placa'])
        amount_match = abs(lr['importe'] - dr['importe']) <= 2.0
        if placa_match and amount_match:
            found = dr
            break
    if found:
        matched_other_weeks.append({'levet': lr, 'db': found})
    else:
        unmatched_final_levet.append(lr)

print("\n" + "="*70)
print("REPORTE DE CONCILIACIÓN GASOLINA: LEVET VS SISTEMA FÉNIX (SEMANA 33)")
print("="*70)
print(f"Total cargas facturadas/reportadas por Levet (Semana 33): {len(levet_s33)} cargas (${imp_lev:,.2f} | {lts_lev:,.2f} L)")
print(f"Total cargas coincidentes en Fénix (Semana 33):          {len(matched_levet)} cargas (${sum(m['levet']['importe'] for m in matched_levet):,.2f})")
print(f"Cargas encontradas registradas en OTRA semana (desfase): {len(matched_other_weeks)} cargas")
print(f"TOTAL CARGAS QUE LEVET REPORTA Y NO TENEMOS EN BD:       {len(unmatched_final_levet)} CARGAS (${sum(u['importe'] for u in unmatched_final_levet):,.2f} | {sum(u['litros'] for u in unmatched_final_levet):,.2f} L)")
print("="*70)

print("\n>>> DETALLE DE LAS CARGAS NO REGISTRADAS EN NUESTRA BASE DE DATOS (FALTANTES):")
for idx, ur in enumerate(unmatched_final_levet, 1):
    print(f"{idx:2d}. [Ticket {ur['ticket']}] Fecha: {ur['fecha']} | Placa: {ur['placa_orig']:<10} | Conductor: {ur['conductor']:<20} | Obra: {ur['obra']:<28} | {ur['litros']:>7.2f} L | ${ur['importe']:>9.2f}")

if matched_other_weeks:
    print("\n>>> CARGAS DE SEMANA 33 REGISTRADAS EN FÉNIX EN OTRA SEMANA (DESFASE):")
    for idx, mo in enumerate(matched_other_weeks, 1):
        lr = mo['levet']
        dr = mo['db']
        print(f"{idx:2d}. [Ticket {lr['ticket']}] Fecha Levet: {lr['fecha']} vs Fecha Fénix: {dr['fecha']} (Semana {dr['semana']}) | Placa: {lr['placa_orig']} | Monto: ${lr['importe']:,.2f}")

unmatched_db = [dr for dr in db_list if dr['id'] not in db_used_ids]
print(f"\n>>> REGISTROS EN BD FÉNIX SEMANA 33 SIN COINCIDENCIA EN LEVET (Total: {len(unmatched_db)}):")
for idx, dr in enumerate(unmatched_db, 1):
    print(f"{idx:2d}. [ID {dr['id']}] Fecha: {dr['fecha']} | Gasolinera: {dr['gasolineria']:<8} | Placa: {dr['placa_orig']:<10} | Conductor: {dr['conductor']:<22} | Obra: {dr['obra']:<20} | {dr['litros']:>7.2f} L | ${dr['importe']:>9.2f}")

