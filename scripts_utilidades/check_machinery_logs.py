import psycopg2
from psycopg2.extras import DictCursor

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

print("=== CHECK BITACORA MAQUINARIA ===")
cur.execute("SELECT * FROM catalogos.bitacora_maquinaria LIMIT 10;")
rows = cur.fetchall()
print(f"Total rows: {len(rows)}")
for r in rows:
    print(dict(r))

print("\n=== CHECK PRODUCTION / MEZCLA DATA ===")
cur.execute("SELECT * FROM mezcla.tendido LIMIT 10;")
rows = cur.fetchall()
print(f"Total tendido: {len(rows)}")

conn.close()
