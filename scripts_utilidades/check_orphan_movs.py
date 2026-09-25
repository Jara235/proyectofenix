import psycopg2
from psycopg2.extras import DictCursor

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

cur.execute("""
    SELECT DISTINCT m.empresa, m.tag, m.responsable, m.no_economico, m.placas, m.tipo_unidad,
           SUM(ABS(m.importe)) as total_consumo,
           COUNT(*) as total_pasadas
    FROM tags.movimientos m
    LEFT JOIN tags.autorizaciones a ON (
        m.tag = a.tag 
        OR (m.tag IS NOT NULL AND a.tag IS NOT NULL AND LENGTH(a.tag) >= 6 AND (m.tag ILIKE '%%' || a.tag || '%%' OR a.tag ILIKE '%%' || m.tag || '%%'))
    )
    WHERE a.id IS NULL
    GROUP BY m.empresa, m.tag, m.responsable, m.no_economico, m.placas, m.tipo_unidad;
""")
print("=== MOVIMIENTOS SIN REGISTRO EN AUTORIZACIONES ===")
for r in cur.fetchall():
    print(dict(r))

conn.close()
