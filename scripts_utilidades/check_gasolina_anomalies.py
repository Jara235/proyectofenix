import psycopg2
from psycopg2.extras import DictCursor

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

cur.execute("""
    SELECT id, fecha, semana, obra_destino, vehiculo, placa, litros, costo_por_litro, importe_total, conductor, observaciones
    FROM gasolina.consumos
    WHERE costo_por_litro = 0 OR importe_total = 0 OR litros > 250
    ORDER BY fecha, id;
""")
for r in cur.fetchall():
    print(dict(r))

conn.close()
