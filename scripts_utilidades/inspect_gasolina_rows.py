import psycopg2
from psycopg2.extras import DictCursor

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

print("=== DETALLE GASOLINA.CONSUMOS MEXICO-TOLUCA ===")
cur.execute("""
    SELECT id, fecha, semana, vehiculo, placa, litros, costo_por_litro, importe_total, conductor, observaciones
    FROM gasolina.consumos
    WHERE obra_destino ILIKE '%TOLUCA%' AND obra_destino NOT ILIKE '%BACHEO%'
    ORDER BY fecha, id;
""")
for r in cur.fetchall():
    print(dict(r))

print("\n=== DETALLE GASOLINA.CONSUMOS LERMA-TRES MARIAS ===")
cur.execute("""
    SELECT id, fecha, semana, vehiculo, placa, litros, costo_por_litro, importe_total, conductor, observaciones
    FROM gasolina.consumos
    WHERE obra_destino ILIKE '%LERMA%'
    ORDER BY fecha, id;
""")
for r in cur.fetchall():
    print(dict(r))

conn.close()
