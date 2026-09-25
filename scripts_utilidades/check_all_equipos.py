import psycopg2
conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor()
cur.execute("SELECT numero_economico, descripcion FROM catalogos.equipos")
for r in cur.fetchall(): print(r)
