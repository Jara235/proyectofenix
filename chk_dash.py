import sqlite3
db = sqlite3.connect('fenix_v2.db')
db.row_factory = sqlite3.Row
print('=== DIESEL CONSUMOS ===')
r = db.execute('SELECT COUNT(*) c, COALESCE(SUM(litros),0) lts, COALESCE(SUM(importe_total),0) imp FROM diesel_consumos').fetchone()
print(f'  Registros: {r[0]}, Litros: {r[1]:.1f}, Importe: {r[2]:.2f}')
sems = db.execute('SELECT semana, SUM(litros) lts, SUM(importe_total) imp, COUNT(*) c FROM diesel_consumos GROUP BY semana ORDER BY semana').fetchall()
for s in sems: print(f'  {s[0]}: {s[1]:.1f} Lts - \ ({s[3]} regs)')

print('\n=== DIESEL FACTURAS ===')
r = db.execute('SELECT COUNT(*) c, COALESCE(SUM(litros_facturados),0) lts, COALESCE(SUM(importe_total),0) imp FROM diesel_facturas').fetchone()
print(f'  Registros: {r[0]}, Litros: {r[1]:.1f}, Importe: {r[2]:.2f}')

print('\n=== GASOLINA CONSUMOS ===')
r = db.execute('SELECT COUNT(*) c FROM gasolina_consumos').fetchone()
print(f'  Registros: {r[0]}')

print('\n=== ALL TABLES ===')
tables = db.execute(\"SELECT name FROM sqlite_master WHERE type='table' ORDER BY name\").fetchall()
for t in tables: print(f'  {t[0]}')
db.close()
