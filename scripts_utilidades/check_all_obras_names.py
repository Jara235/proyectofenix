import psycopg2
from psycopg2.extras import DictCursor

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

print("=== ALL UNIQUE OBRAS IN DIESEL.CONSUMOS ===")
cur.execute("SELECT DISTINCT obra_destino FROM diesel.consumos ORDER BY obra_destino;")
for r in cur.fetchall():
    print(" -", r['obra_destino'])

print("\n=== ALL UNIQUE OBRAS IN GASOLINA.CONSUMOS ===")
cur.execute("SELECT DISTINCT obra_destino FROM gasolina.consumos ORDER BY obra_destino;")
for r in cur.fetchall():
    print(" -", r['obra_destino'])

print("\n=== ALL UNIQUE OBRAS IN DIESEL.FACTURAS ===")
cur.execute("SELECT DISTINCT obra_destino FROM diesel.facturas ORDER BY obra_destino;")
for r in cur.fetchall():
    print(" -", r['obra_destino'])

print("\n=== ALL UNIQUE OBRAS IN GASOLINA.FACTURAS ===")
cur.execute("SELECT DISTINCT obra_destino FROM gasolina.facturas ORDER BY obra_destino;")
for r in cur.fetchall():
    print(" -", r['obra_destino'])

print("\n=== ALL UNIQUE OBRAS IN TAGS.MOVIMIENTOS ===")
cur.execute("SELECT DISTINCT obra_asignada FROM tags.movimientos ORDER BY obra_asignada;")
for r in cur.fetchall():
    print(" -", r['obra_asignada'])

conn.close()
