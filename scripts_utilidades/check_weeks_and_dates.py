import psycopg2
from psycopg2.extras import DictCursor

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

print("=== WEEKS IN DIESEL.CONSUMOS ===")
cur.execute("SELECT DISTINCT semana FROM diesel.consumos ORDER BY semana;")
print([r[0] for r in cur.fetchall()])

print("\n=== WEEKS IN GASOLINA.CONSUMOS ===")
cur.execute("SELECT DISTINCT semana FROM gasolina.consumos ORDER BY semana;")
print([r[0] for r in cur.fetchall()])

print("\n=== WEEKS IN DIESEL.FACTURAS ===")
cur.execute("SELECT DISTINCT semana FROM diesel.facturas ORDER BY semana;")
print([r[0] for r in cur.fetchall()])

print("\n=== WEEKS IN GASOLINA.FACTURAS ===")
cur.execute("SELECT DISTINCT semana FROM gasolina.facturas ORDER BY semana;")
print([r[0] for r in cur.fetchall()])

print("\n=== DATE RANGES IN DIESEL.CONSUMOS ===")
cur.execute("SELECT MIN(fecha), MAX(fecha) FROM diesel.consumos;")
print(cur.fetchone())

print("\n=== DATE RANGES IN GASOLINA.CONSUMOS ===")
cur.execute("SELECT MIN(fecha), MAX(fecha) FROM gasolina.consumos;")
print(cur.fetchone())

conn.close()
