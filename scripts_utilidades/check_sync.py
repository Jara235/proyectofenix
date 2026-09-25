import pandas as pd
import sqlite3

excel_path = 'c:/Users/JOSE/Desktop/Proyecto fenix/MAESTRO_CONTROL_DIESEL_NUEVO.xlsx'
try:
    df = pd.read_excel(excel_path, sheet_name='BD_DIESEL')
    print(f'Excel rows: {len(df)}')
    print('Latest in Excel:', df['FOLIO_CONCILIACION'].tail(5).tolist())
except Exception as e:
    print('Error reading DIESEL sheet:', e)

db = sqlite3.connect('c:/Users/JOSE/Desktop/Proyecto fenix/fenix_v2.db')
c = db.cursor()
c.execute('SELECT COUNT(*) FROM diesel_consumos')
print(f'DB rows: {c.fetchone()[0]}')
c.execute('SELECT folio_conciliacion FROM diesel_consumos ORDER BY id DESC LIMIT 5')
print('Latest in DB:', [row[0] for row in c.fetchall()])
db.close()

