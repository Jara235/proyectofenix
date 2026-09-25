import sqlite3
db = sqlite3.connect('fenix_v2.db')
print('gasolina_autorizaciones records:')
rows = db.execute('SELECT count(*) FROM gasolina_autorizaciones').fetchone()
print(f'Total records: {rows[0]}')
db.close()
