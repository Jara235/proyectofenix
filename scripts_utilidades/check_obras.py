import psycopg2
conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor()
cur.execute("SELECT codigo, nombre FROM catalogos.obras WHERE nombre ILIKE '%pegaso%' OR nombre ILIKE '%transporte%' OR nombre ILIKE '%tanque%'")
for row in cur.fetchall():
    print('Obra:', row)
cur.close()
conn.close()
