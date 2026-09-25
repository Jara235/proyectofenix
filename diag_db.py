import sqlite3
db = sqlite3.connect('fenix.db')
cur = db.cursor()

print('--- SCHEMA: fenix_gas_presupuestos ---')
cur.execute('PRAGMA table_info(fenix_gas_presupuestos)')
for r in cur.fetchall(): print(r)

print('\n--- SCHEMA: fenix_gas_reportes_diarios ---')
cur.execute('PRAGMA table_info(fenix_gas_reportes_diarios)')
for r in cur.fetchall(): print(r)

print('\n--- SCHEMA: fenix_gas_tickets_reales ---')
cur.execute('PRAGMA table_info(fenix_gas_tickets_reales)')
for r in cur.fetchall(): print(r)

print('\n--- SCHEMA: fenix_gasolina_autorizaciones ---')
cur.execute('PRAGMA table_info(fenix_gasolina_autorizaciones)')
for r in cur.fetchall(): print(r)

print('\n--- SCHEMA: fenix_gasolina_consumos ---')
cur.execute('PRAGMA table_info(fenix_gasolina_consumos)')
for r in cur.fetchall(): print(r)

print('\n--- PRESUPUESTOS SAMPLE ---')
cur.execute('SELECT * FROM fenix_gas_presupuestos LIMIT 5')
for r in cur.fetchall(): print(r)

print('\n--- TICKETS REALES (by semana) ---')
cur.execute('SELECT semana, gasolinera, COUNT(*), ROUND(SUM(litros),2), ROUND(SUM(importe),2) FROM fenix_gas_tickets_reales GROUP BY semana, gasolinera')
for r in cur.fetchall(): print(r)

print('\n--- REPORTES DIARIOS SAMPLE ---')
cur.execute('SELECT * FROM fenix_gas_reportes_diarios LIMIT 5')
for r in cur.fetchall(): print(r)

print('\n--- GASOLINA AUTORIZACIONES SAMPLE ---')
cur.execute('SELECT * FROM fenix_gasolina_autorizaciones LIMIT 5')
for r in cur.fetchall(): print(r)

print('\n--- GASOLINA CONSUMOS SAMPLE ---')
cur.execute('SELECT * FROM fenix_gasolina_consumos LIMIT 5')
for r in cur.fetchall(): print(r)

db.close()
