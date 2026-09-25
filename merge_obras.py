import psycopg2

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor()

cur.execute("SELECT codigo, nombre FROM catalogos.obras WHERE nombre LIKE '%Pegaso%'")
print('Obras Pegaso:', cur.fetchall())

# Let's delete the one with codigo 'MPE' if both exist and have the same name.
cur.execute("DELETE FROM catalogos.obras WHERE codigo = 'MPE' AND nombre = 'Maquinaria Pegaso'")
conn.commit()

cur.execute("SELECT codigo, nombre FROM catalogos.obras WHERE nombre LIKE '%Pegaso%'")
print('Obras Pegaso (after delete):', cur.fetchall())

cur.close()
conn.close()
