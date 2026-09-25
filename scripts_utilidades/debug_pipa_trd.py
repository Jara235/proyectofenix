import psycopg2
from psycopg2.extras import DictCursor
import re

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

cur.execute("""
    SELECT semana, empresa, tag, no_economico, responsable, placas, tipo_unidad, COUNT(*) as pasadas, SUM(ABS(importe)) as total_consumo
    FROM tags.movimientos
    WHERE empresa = 'TRD' AND (responsable ILIKE '%PIPA%' OR no_economico ILIKE '%PIPA%' OR tag ILIKE '%28600325%' OR tag ILIKE '%30874319%')
    GROUP BY semana, empresa, tag, no_economico, responsable, placas, tipo_unidad
    ORDER BY semana, tag;
""")
rows = cur.fetchall()
print("=== MOVIMIENTOS EN BD PARA PIPA TRD ===")
for r in rows:
    print(dict(r))

# Ver cómo se calcula el consumo en la API
cur.execute("SELECT * FROM tags.autorizaciones WHERE empresa = 'TRD' AND responsable ILIKE '%PIPA%';")
auth_pipa = cur.fetchall()
print("\n=== AUTORIZACIONES PIPA EN BD ===")
for a in auth_pipa:
    print(dict(a))

conn.close()
