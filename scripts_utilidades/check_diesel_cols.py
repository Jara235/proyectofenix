import psycopg2

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor()

cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_schema = 'diesel' AND table_name = 'consumos';
""")
for r in cur.fetchall():
    print(r)

print("\nSample rows from diesel.consumos:")
cur.execute("SELECT * FROM diesel.consumos LIMIT 5;")
for r in cur.fetchall():
    print(r)

conn.close()
