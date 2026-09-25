import psycopg2
from psycopg2.extras import DictCursor
import re

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

# Check all tags in autorizaciones with monto_autorizado == 0 or NULL
cur.execute("""
    SELECT a.id, a.empresa, a.tag, a.responsable, a.no_economico, a.placas, a.tipo_unidad, a.monto_autorizado, a.estatus,
           COALESCE(SUM(ABS(m.importe)), 0) as consumo_acumulado,
           COUNT(m.id) as total_pasadas
    FROM tags.autorizaciones a
    LEFT JOIN tags.movimientos m ON (
        m.tag = a.tag 
        OR (m.tag IS NOT NULL AND a.tag IS NOT NULL AND LENGTH(a.tag) >= 6 AND (m.tag ILIKE '%%' || a.tag || '%%' OR a.tag ILIKE '%%' || m.tag || '%%'))
    )
    WHERE a.monto_autorizado IS NULL OR a.monto_autorizado = 0
    GROUP BY a.id, a.empresa, a.tag, a.responsable, a.no_economico, a.placas, a.tipo_unidad, a.monto_autorizado, a.estatus
    ORDER BY a.empresa, a.responsable;
""")
print("=== TAGS SIN AUTORIZACION EN CATALOGO ===")
rows = cur.fetchall()
for r in rows:
    print(f"[{r['empresa']}] {r['responsable']} | Tag: {r['tag']} | Placas: {r['placas']} | Consumo: ${r['consumo_acumulado']:,.2f} ({r['total_pasadas']} pasadas)")

conn.close()
