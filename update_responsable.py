import psycopg2
conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor()
cur.execute("UPDATE catalogos.obras SET responsable_default = 'Luis', ingeniero_responsable = 'Luis' WHERE nombre = 'Planta Huixquilucan'")
conn.commit()
print("Actualizado.")
