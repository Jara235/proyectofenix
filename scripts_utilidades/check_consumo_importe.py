import psycopg2
conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor()
cur.execute("SELECT obra_destino, SUM(litros), SUM(importe_total) FROM diesel.consumos WHERE semana='Semana 28' GROUP BY obra_destino")
print("Semana 28 consumos y montos:")
for row in cur.fetchall():
    print(row)
cur.close()
conn.close()
