import psycopg2
conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor()
cur.execute("SELECT referencia, litros_autorizados FROM catalogos.autorizaciones WHERE semana='29'")
w29 = {row[0]: row[1] for row in cur.fetchall() if row[1] > 0}
print('Week 29:', w29)
cur.close()
conn.close()
