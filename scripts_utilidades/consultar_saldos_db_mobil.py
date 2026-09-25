import psycopg2
from psycopg2.extras import DictCursor

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

print("=== diesel.pagos_facturas ===")
cur.execute("SELECT * FROM diesel.pagos_facturas;")
for r in cur.fetchall():
    print(dict(r))

print("\n=== diesel.complementos_pago ===")
cur.execute("SELECT * FROM diesel.complementos_pago;")
for r in cur.fetchall():
    print(dict(r))

print("\n=== FACTURAS EN diesel.facturas SEMANAS 28, 29, 30, 31 (PROVEEDOR CASTILLA / MOBIL) ===")
cur.execute("""
    SELECT semana, count(*) as cant, sum(litros_facturados) as lts, sum(importe_total) as tot
    FROM diesel.facturas
    WHERE proveedor ILIKE '%CASTILLA%' AND semana IN ('28', '29', '30', '31')
    GROUP BY semana
    ORDER BY semana;
""")
for r in cur.fetchall():
    print(dict(r))

print("\n=== TOTALES SEMANAS 28 A 31 EN BD ===")
cur.execute("""
    SELECT 
        sum(case when semana in ('28','29','30','31') then importe_total else 0 end) as tot_con_sem28,
        sum(case when semana in ('29','30','31') then importe_total else 0 end) as tot_sin_sem28
    FROM diesel.facturas
    WHERE proveedor ILIKE '%CASTILLA%';
""")
print(dict(cur.fetchone()))
