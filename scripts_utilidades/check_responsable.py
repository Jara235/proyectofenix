import psycopg2
conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor()
cur.execute("SELECT codigo, nombre, responsable_default, ingeniero_responsable FROM catalogos.obras WHERE nombre ILIKE '%huix%'")
for r in cur.fetchall(): print(r)
