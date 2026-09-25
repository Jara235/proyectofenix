import psycopg2
from psycopg2.extras import DictCursor

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

# 1. Distinct obras in catalogos.obras
cur.execute("SELECT id, nombre, cliente, ubicacion FROM catalogos.obras ORDER BY nombre;")
print("=== OBRAS EN CATALOGO ===")
for r in cur.fetchall():
    print(dict(r))

# 2. Distinct obras in diesel.consumos
cur.execute("""
    SELECT DISTINCT obra, COUNT(*) as registros, MIN(fecha) as fecha_min, MAX(fecha) as fecha_max,
           SUM(litros) as total_litros, SUM(importe) as total_importe
    FROM diesel.consumos
    GROUP BY obra
    ORDER BY total_litros DESC NULLS LAST;
""")
print("\n=== OBRAS EN DIESEL.CONSUMOS ===")
for r in cur.fetchall():
    print(dict(r))

# 3. Distinct obras in diesel.facturas
cur.execute("""
    SELECT DISTINCT obra, COUNT(*) as registros, MIN(fecha) as fecha_min, MAX(fecha) as fecha_max,
           SUM(litros) as total_litros, SUM(total) as total_importe
    FROM diesel.facturas
    GROUP BY obra
    ORDER BY total_litros DESC NULLS LAST;
""")
print("\n=== OBRAS EN DIESEL.FACTURAS ===")
for r in cur.fetchall():
    print(dict(r))

# 4. Distinct obras in gasolina.consumos
cur.execute("""
    SELECT DISTINCT obra, COUNT(*) as registros, MIN(fecha) as fecha_min, MAX(fecha) as fecha_max,
           SUM(litros) as total_litros, SUM(importe) as total_importe
    FROM gasolina.consumos
    GROUP BY obra
    ORDER BY total_litros DESC NULLS LAST;
""")
print("\n=== OBRAS EN GASOLINA.CONSUMOS ===")
for r in cur.fetchall():
    print(dict(r))

# 5. Distinct obras in gasolina.facturas
cur.execute("""
    SELECT DISTINCT obra, COUNT(*) as registros, MIN(fecha) as fecha_min, MAX(fecha) as fecha_max,
           SUM(litros) as total_litros, SUM(total) as total_importe
    FROM gasolina.facturas
    GROUP BY obra
    ORDER BY total_litros DESC NULLS LAST;
""")
print("\n=== OBRAS EN GASOLINA.FACTURAS ===")
for r in cur.fetchall():
    print(dict(r))

conn.close()
