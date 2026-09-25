import psycopg2
from psycopg2.extras import DictCursor

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

# Ver estructura de jalisco_movimientos
cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_schema='diesel' AND table_name='jalisco_movimientos'
    ORDER BY ordinal_position
""")
cols = cur.fetchall()
print("=== COLUMNAS jalisco_movimientos ===")
for c in cols:
    print(f"  {c['column_name']}: {c['data_type']}")

# Ver datos reales agrupados por semana
cur.execute("""
    SELECT 
        semana,
        tipo_movimiento,
        COUNT(*) as registros,
        SUM(litros) as litros,
        SUM(importe_total) as importe
    FROM diesel.jalisco_movimientos
    GROUP BY semana, tipo_movimiento
    ORDER BY semana, tipo_movimiento
""")
rows = cur.fetchall()
print("\n=== DATOS POR SEMANA Y TIPO ===")
for r in rows:
    print(dict(r))

conn.close()
