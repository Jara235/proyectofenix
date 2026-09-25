import psycopg2, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor()

cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_schema='diesel' AND table_name='facturas' ORDER BY ordinal_position")
print('diesel.facturas columnas:')
for r in cur.fetchall(): print(f'  {r[0]}: {r[1]}')

cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_schema='diesel' AND table_name='consumos' ORDER BY ordinal_position")
print('\ndiesel.consumos columnas:')
for r in cur.fetchall(): print(f'  {r[0]}: {r[1]}')

conn.close()
