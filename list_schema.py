import psycopg2

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor()

# Get catalog tables
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'catalogos'")
print("Catalog tables:", cur.fetchall())

# Get schema for obras
cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = 'catalogos' AND table_name = 'obras'")
print("Obras schema:", cur.fetchall())

# Get schema for equipos
cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = 'catalogos' AND table_name = 'equipos'")
print("Equipos schema:", cur.fetchall())

cur.close()
conn.close()
