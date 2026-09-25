import psycopg2
from psycopg2.extras import DictCursor

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

print("=== 1. OBRAS EN CATALOGOS.OBRAS ===")
cur.execute("SELECT codigo, nombre, ingeniero_responsable FROM catalogos.obras ORDER BY nombre;")
for r in cur.fetchall():
    print(dict(r))

print("\n=== 2. OBRAS EN DIESEL.CONSUMOS ===")
cur.execute("""
    SELECT obra_destino, COUNT(*) as cargas, MIN(fecha) as min_f, MAX(fecha) as max_f,
           SUM(litros) as total_litros, SUM(importe_total) as total_importe
    FROM diesel.consumos
    GROUP BY obra_destino
    ORDER BY total_litros DESC NULLS LAST;
""")
for r in cur.fetchall():
    print(dict(r))

print("\n=== 3. OBRAS EN GASOLINA.CONSUMOS ===")
cur.execute("""
    SELECT obra_destino, COUNT(*) as cargas, MIN(fecha) as min_f, MAX(fecha) as max_f,
           SUM(litros) as total_litros, SUM(importe_total) as total_importe
    FROM gasolina.consumos
    GROUP BY obra_destino
    ORDER BY total_litros DESC NULLS LAST;
""")
for r in cur.fetchall():
    print(dict(r))

print("\n=== 4. OBRAS EN DIESEL.FACTURAS ===")
cur.execute("""
    SELECT obra_destino, COUNT(*) as facturas, MIN(fecha_factura) as min_f, MAX(fecha_factura) as max_f,
           SUM(litros_facturados) as total_litros, SUM(importe_total) as total_importe
    FROM diesel.facturas
    GROUP BY obra_destino
    ORDER BY total_litros DESC NULLS LAST;
""")
for r in cur.fetchall():
    print(dict(r))

print("\n=== 5. OBRAS EN GASOLINA.FACTURAS ===")
cur.execute("""
    SELECT obra_destino, COUNT(*) as facturas, MIN(fecha_factura) as min_f, MAX(fecha_factura) as max_f,
           SUM(litros_facturados) as total_litros, SUM(importe_total) as total_importe
    FROM gasolina.facturas
    GROUP BY obra_destino
    ORDER BY total_litros DESC NULLS LAST;
""")
for r in cur.fetchall():
    print(dict(r))

conn.close()
