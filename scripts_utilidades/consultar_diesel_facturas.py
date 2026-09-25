import psycopg2
from psycopg2.extras import DictCursor

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

print("=== RESUMEN POR PROVEEDOR Y SEMANA EN diesel.facturas ===")
cur.execute("""
    SELECT proveedor, punto_de_carga, semana, count(*) as cant, sum(litros_facturados) as tot_lts, sum(importe_total) as tot_imp
    FROM diesel.facturas
    GROUP BY proveedor, punto_de_carga, semana
    ORDER BY proveedor, semana;
""")
for r in cur.fetchall():
    print(dict(r))

print("\n=== TOTAL GLOBAL EN diesel.facturas ===")
cur.execute("SELECT count(*), sum(litros_facturados), sum(importe_total) FROM diesel.facturas;")
print(cur.fetchone())
