import psycopg2
from psycopg2.extras import DictCursor
from decimal import Decimal

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

# Resumen por semana mostrando ENTRADAS y SALIDAS
cur.execute("""
    SELECT 
        semana,
        tipo_movimiento,
        COUNT(*) as num,
        SUM(litros) as litros,
        SUM(importe_total) as importe,
        MIN(saldo_teorico) as saldo_min,
        MAX(saldo_teorico) as saldo_max
    FROM diesel.jalisco_movimientos
    GROUP BY semana, tipo_movimiento
    ORDER BY semana, tipo_movimiento
""")
print("=== ENTRADAS/SALIDAS/AJUSTES POR SEMANA ===")
for r in cur.fetchall():
    print(dict(r))

print()
# Ajustes en control_vales_jalisco
try:
    cur.execute("SELECT * FROM diesel.control_vales_jalisco ORDER BY semana")
    print("=== CONTROL_VALES_JALISCO ===")
    for r in cur.fetchall():
        print(dict(r))
except Exception as e:
    print(f"Error en control_vales_jalisco: {e}")

conn.close()
