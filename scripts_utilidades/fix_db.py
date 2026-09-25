import psycopg2

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor()

cur.execute("UPDATE diesel.consumos SET semana = 'Semana ' || semana WHERE semana ~ '^[0-9]+$'")
print('Consumos updated:', cur.rowcount)

conn.commit()
cur.close()
conn.close()
