import psycopg2
from psycopg2.extras import DictCursor

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

# Ver registros ENTRADA que tienen archivo_pdf
cur.execute("""
    SELECT id, semana, fecha, tipo_movimiento, litros, importe_total, saldo_teorico, 
           observaciones,
           CASE WHEN archivo_pdf IS NOT NULL THEN 'SI' ELSE 'NO' END as tiene_pdf,
           CASE WHEN foto_evidencia IS NOT NULL THEN 'SI' ELSE 'NO' END as tiene_foto
    FROM diesel.jalisco_movimientos
    WHERE archivo_pdf IS NOT NULL OR tipo_movimiento = 'ENTRADA'
    ORDER BY id
""")
rows = cur.fetchall()
print("=== REGISTROS CON PDF O ENTRADAS ===")
for r in rows:
    print(dict(r))

# Contar cuantos tienen PDF
cur.execute("""
    SELECT semana, COUNT(*) as total, 
           SUM(CASE WHEN archivo_pdf IS NOT NULL THEN 1 ELSE 0 END) as con_pdf
    FROM diesel.jalisco_movimientos
    GROUP BY semana ORDER BY semana
""")
print("\n=== CONTEO DE PDFs POR SEMANA ===")
for r in cur.fetchall():
    print(dict(r))

conn.close()
