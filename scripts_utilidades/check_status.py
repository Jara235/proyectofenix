import sqlite3
db = sqlite3.connect('c:/Users/JOSE/Desktop/Proyecto fenix/fenix_v2.db')

# Check tables
tables = db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print('TABLES:', [t[0] for t in tables])

# Count diesel records
c_diesel = db.execute('SELECT COUNT(*) FROM diesel_consumos').fetchone()[0]
print(f'diesel_consumos: {c_diesel} records')

c_fac = db.execute("SELECT COUNT(*) FROM diesel_consumos WHERE origen='FACTURA'").fetchone()[0]
print(f'  - Facturas: {c_fac}')

# Check folios pattern
folios = db.execute("SELECT folio_conciliacion FROM diesel_consumos ORDER BY id DESC LIMIT 5").fetchall()
print('Latest folios:', [f[0] for f in folios])

# Check other module tables
try:
    c_gas = db.execute('SELECT COUNT(*) FROM gasolina_consumos').fetchone()[0]
    print(f'gasolina_consumos: {c_gas} records')
except: print('gasolina_consumos: NOT FOUND or empty')

try:
    c_acar = db.execute('SELECT COUNT(*) FROM acarreos').fetchone()[0]
    print(f'acarreos: {c_acar} records')
except: print('acarreos: NOT FOUND')

try:
    c_mezcla = db.execute('SELECT COUNT(*) FROM mezcla').fetchone()[0]
    print(f'mezcla: {c_mezcla} records')
except: print('mezcla: NOT FOUND')

db.close()
