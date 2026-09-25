import openpyxl, datetime, re
import psycopg2
from psycopg2.extras import DictCursor

def norm_placa(p):
    if not p: return ''
    return re.sub(r'[^A-Z0-9]', '', str(p).upper())

# 1. Cargar Levet Excel
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
    
    if ticket is None and placa is None and importe is None: continue
    if isinstance(ticket, str) and ('TOTAL' in ticket.upper() or 'TICKET' in ticket.upper()): continue
    if isinstance(placa, str) and 'TOTAL' in placa.upper(): continue
        
    fecha_str = str(fecha)
    if isinstance(fecha, (datetime.datetime, datetime.date)):
        fecha_str = fecha.strftime('%Y-%m-%d')
        
    try: litros_f = float(litros or 0)
    except: litros_f = 0.0
    try: importe_f = float(importe or 0)
    except: importe_f = 0.0
    try: precio_f = float(precio or 0)
    except: precio_f = 0.0

    levet_rows.append({
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
    })

# 2. Cargar DB Fenix
conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)
cur.execute('''
    SELECT id, fecha, semana, conductor, vehiculo, placa, obra_destino, litros, costo_por_litro, importe_total, gasolineria, folio_conciliacion, estatus_revision, origen
    FROM gasolina.consumos
    WHERE semana IN ('33', 'Semana 33') OR (fecha >= '2026-08-10' AND fecha <= '2026-08-16')
    ORDER BY fecha, id
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

# 3. Filtrar Semana 33 en Levet (Filas 50 a 93)
levet_s33 = [r for r in levet_rows if '2026-08-10' <= r['fecha'] <= '2026-08-16']

# Realizar matching con precisión quirúrgica
matched_pairs = []
unmatched_levet = []
used_db_ids = set()

# Paso 1: Match Exacto (Placa + Monto +/- $2)
for lr in levet_s33:
    found = None
    for dr in db_list:
        if dr['id'] in used_db_ids: continue
        if lr['placa'] and dr['placa'] and (lr['placa'] == dr['placa']):
            if abs(lr['importe'] - dr['importe']) <= 2.0:
                found = dr
                break
    if found:
        used_db_ids.add(found['id'])
        matched_pairs.append({'levet': lr, 'db': found, 'tipo': 'MATCH EXACTO: PLACA + MONTO'})
    else:
        unmatched_levet.append(lr)

# Paso 2: Casos especiales conocidos (Placa vacía en Levet pero mismo Monto + Fecha + Gasolinera LEVET)
unmatched_levet_p2 = []
for lr in unmatched_levet:
    found = None
    # Caso Juan Carlos Nazar $1,144.50 en 2026-08-14
    if lr['ticket'] == '418502' and abs(lr['importe'] - 1144.50) <= 0.1:
        for dr in db_list:
            if dr['id'] in used_db_ids: continue
            if dr['id'] == 409 and abs(dr['importe'] - 1144.50) <= 0.1:
                found = dr
                break
    # Caso Cortadora de Concreto / Equipo Menor $1,000 en 2026-08-10
    elif 'MENOR' in lr['placa_orig'].upper() and abs(lr['importe'] - 1000.0) <= 0.1:
        for dr in db_list:
            if dr['id'] in used_db_ids: continue
            if dr['id'] == 417 and abs(dr['importe'] - 1000.0) <= 0.1:
                found = dr
                break
    # Caso Cristobal Silva / LKV206D vs LKC794D $1,500 en 2026-08-10
    elif lr['ticket'] == '416459' and abs(lr['importe'] - 1500.0) <= 0.1:
        for dr in db_list:
            if dr['id'] in used_db_ids: continue
            if dr['id'] == 437 and abs(dr['importe'] - 1500.0) <= 0.1:
                found = dr
                break
    if found:
        used_db_ids.add(found['id'])
        matched_pairs.append({'levet': lr, 'db': found, 'tipo': 'MATCH ESPECIAL: VALE IDENTIFICADO'})
    else:
        unmatched_levet_p2.append(lr)

cargas_faltantes_levet = unmatched_levet_p2

tot_lts_levet = sum(r['litros'] for r in levet_s33)
tot_imp_levet = sum(r['importe'] for r in levet_s33)

tot_lts_match = sum(m['levet']['litros'] for m in matched_pairs)
tot_imp_match = sum(m['levet']['importe'] for m in matched_pairs)

tot_lts_falt = sum(r['litros'] for r in cargas_faltantes_levet)
tot_imp_falt = sum(r['importe'] for r in cargas_faltantes_levet)

print("="*80)
print("ESTADÍSTICAS FINALES CONCILIACIÓN SEMANA 33 (LEVET):")
print(f" - Cargas totales en Estado de Cuenta Levet: {len(levet_s33)} cargas ({tot_lts_levet:,.2f} L, ${tot_imp_levet:,.2f} MXN)")
print(f" - Cargas Conciliadas con éxito en BD Fénix: {len(matched_pairs)} cargas ({tot_lts_match:,.2f} L, ${tot_imp_match:,.2f} MXN)")
print(f" - CARGAS QUE LEVET REPORTA QUE NO TENEMOS EN BD: {len(cargas_faltantes_levet)} CARGAS ({tot_lts_falt:,.2f} L, ${tot_imp_falt:,.2f} MXN)")
print("="*80)

print("\n>>> DETALLE EXACTO DE LAS CARGAS QUE LEVET REPORTA Y NO TENEMOS EN BD:")
for idx, f in enumerate(cargas_faltantes_levet, 1):
    print(f"{idx:2d}. Ticket: {f['ticket']:<8} | Fecha: {f['fecha']} | Placa: {f['placa_orig']:<10} | Conductor: {f['conductor']:<20} | Obra: {f['obra']:<28} | {f['litros']:>7.2f} L | ${f['importe']:>9.2f}")
