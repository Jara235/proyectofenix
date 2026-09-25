import psycopg2
from psycopg2.extras import DictCursor

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

# Ver los saldos reales de jalisco - saldo_teorico es el running balance
cur.execute("""
    SELECT 
        semana,
        MIN(saldo_teorico) as saldo_min,
        MAX(saldo_teorico) as saldo_max,
        FIRST_VALUE(saldo_teorico) OVER (PARTITION BY semana ORDER BY id ASC) as saldo_inicio,
        LAST_VALUE(saldo_teorico) OVER (PARTITION BY semana ORDER BY id ASC ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) as saldo_final,
        SUM(CASE WHEN tipo_movimiento='SALIDA' THEN importe_total ELSE 0 END) as importe_salidas,
        MAX(CASE WHEN tipo_movimiento='ENTRADA' THEN importe_total ELSE 0 END) as importe_entrada,
        MAX(CASE WHEN tipo_movimiento='AJUSTE' THEN importe_total ELSE 0 END) as ajuste
    FROM diesel.jalisco_movimientos
    GROUP BY semana
    ORDER BY semana
""")
rows = cur.fetchall()
print("=== RESUMEN POR SEMANA ===")
for r in rows:
    print(dict(r))

# Ver el saldo de vales (importe) por semana - ENTRADA
cur.execute("""
    SELECT semana,
           SUM(CASE WHEN tipo_movimiento='ENTRADA' THEN importe_total ELSE 0 END) as saldo_inicial_vales,
           SUM(CASE WHEN tipo_movimiento='SALIDA'  THEN importe_total ELSE 0 END) as importe_salidas,
           SUM(CASE WHEN tipo_movimiento='AJUSTE'  THEN importe_total ELSE 0 END) as ajuste
    FROM diesel.jalisco_movimientos
    GROUP BY semana
    ORDER BY semana
""")
rows = cur.fetchall()
print("\n=== ENTRADA/SALIDA/AJUSTE POR SEMANA ===")
for r in rows:
    print(dict(r))

conn.close()
