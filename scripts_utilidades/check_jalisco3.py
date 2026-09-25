import psycopg2
from psycopg2.extras import DictCursor
from decimal import Decimal

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

# Ver todos los movimientos con saldo_teorico para entender la logica
cur.execute("""
    SELECT id, semana, fecha, tipo_movimiento, litros, importe_total, saldo_teorico, observaciones
    FROM diesel.jalisco_movimientos
    ORDER BY id
""")
rows = cur.fetchall()
print("=== TODOS LOS MOVIMIENTOS ===")
for r in rows:
    print(dict(r))

conn.close()
