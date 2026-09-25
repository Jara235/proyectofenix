import psycopg2
from psycopg2.extras import DictCursor

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

def print_dups(schema):
    print(f"--- Duplicados en {schema}.solicitudes ---")
    cur.execute(f"""
        SELECT fecha, importe_total, litros, COUNT(*) as cantidad
        FROM {schema}.solicitudes
        GROUP BY fecha, importe_total, litros
        HAVING COUNT(*) > 1
        ORDER BY fecha DESC
    """)
    rows = cur.fetchall()
    if not rows:
        print("Sin duplicados.")
    for r in rows:
        print(f"Fecha: {r['fecha']}, Litros: {r['litros']}, Importe: {r['importe_total']}, Cantidad: {r['cantidad']}")

print_dups('diesel')
print_dups('gasolina')

conn.close()
