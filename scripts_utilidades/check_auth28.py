import psycopg2
conn=psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur=conn.cursor()
cur.execute("SELECT referencia, semana, litros_autorizados FROM catalogos.autorizaciones WHERE tipo='DIESEL' AND semana=28 ORDER BY referencia")
for r in cur.fetchall():
    print(r)
