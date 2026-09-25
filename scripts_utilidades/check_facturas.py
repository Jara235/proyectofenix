import psycopg2
conn=psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur=conn.cursor()
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema='diesel' AND table_name='facturas';")
print([row[0] for row in cur.fetchall()])
