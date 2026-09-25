import datetime

# Definición de semanas en 2026 (Lunes a Domingo o estándar Fénix)
# Semana 27: 29 Junio 2026 - 05 Julio 2026 (o 06 Jul - 12 Jul)
# Veamos cómo están definidas las semanas en la base de datos de Fénix

import psycopg2
from psycopg2.extras import DictCursor

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

cur.execute("""
    SELECT semana, min(fecha_factura) as f_min, max(fecha_factura) as f_max, count(*) as cant, sum(importe_total) as tot
    FROM diesel.facturas
    WHERE proveedor ILIKE '%CASTILLA%'
    GROUP BY semana
    ORDER BY semana;
""")
print("=== SEMANAS EN diesel.facturas (CASTILLA / MOBIL) ===")
for r in cur.fetchall():
    print(dict(r))

cur.execute("""
    SELECT semana, min(fecha) as f_min, max(fecha) as f_max, count(*) as cant, sum(litros) as lts, sum(importe_total) as tot
    FROM diesel.consumos
    GROUP BY semana
    ORDER BY semana;
""")
print("\n=== SEMANAS EN diesel.consumos ===")
for r in cur.fetchall():
    print(dict(r))
