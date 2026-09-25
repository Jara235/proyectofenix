import sqlite3
db = sqlite3.connect('fenix_v2.db')
print('=== gasolina_consumos schema ===')
for c in db.execute('PRAGMA table_info(gasolina_consumos)'): print(f'  {c[1]} ({c[2]})')
print()
print('=== gasolina_facturas schema ===')
for c in db.execute('PRAGMA table_info(gasolina_facturas)'): print(f'  {c[1]} ({c[2]})')
db.close()
