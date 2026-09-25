import psycopg2
from psycopg2.extras import DictCursor

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

print("=== ESTRUCTURA Y CONTENIDO DE tags.autorizaciones ===")
cur.execute("SELECT * FROM tags.autorizaciones;")
rows_tags_aut = cur.fetchall()
print(f"Total registros en tags.autorizaciones: {len(rows_tags_aut)}")
for r in rows_tags_aut:
    print(dict(r))

print("\n=== ESTRUCTURA Y CONTENIDO DE tags.movimientos (Top 10) ===")
cur.execute("SELECT * FROM tags.movimientos LIMIT 10;")
rows_tags_mov = cur.fetchall()
print(f"Total registros en tags.movimientos (muestra): {len(rows_tags_mov)}")
for r in rows_tags_mov:
    print(dict(r))

print("\n=== BUSCAR BRYAN EN TODAS LAS TABLAS DE AUTORIZACIONES ===")
for tb in ['tags.autorizaciones', 'gasolina.autorizaciones', 'gasolina.autorizaciones_maestro', 'gasolina.autorizaciones_semanal', 'catalogos.autorizaciones']:
    try:
        cur.execute(f"SELECT * FROM {tb} WHERE CAST(row_to_json({tb}) AS TEXT) ILIKE '%BRYAN%';")
        res = cur.fetchall()
        print(f"\n>> {tb} ({len(res)} coincidencias):")
        for r in res:
            print(dict(r))
    except Exception as e:
        print(f"Error en {tb}: {e}")
        conn.rollback()

conn.close()
