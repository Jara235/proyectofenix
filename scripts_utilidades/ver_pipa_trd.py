import psycopg2
from psycopg2.extras import DictCursor

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

print("=== AUTORIZACIONES TRD PIPA ===")
cur.execute("SELECT * FROM tags.autorizaciones WHERE empresa = 'TRD' AND (responsable ILIKE '%PIPA%' OR no_economico ILIKE '%PIPA%' OR placas ILIKE '%NPW%' OR placas ILIKE '%NE4262%');")
for r in cur.fetchall():
    print(dict(r))

print("\n=== MOVIMIENTOS TRD PIPA ===")
cur.execute("SELECT semana, empresa, tag, no_economico, responsable, placas, tipo_unidad, COUNT(*) as pasadas, SUM(ABS(importe)) as total_consumo FROM tags.movimientos WHERE empresa = 'TRD' AND (responsable ILIKE '%PIPA%' OR no_economico ILIKE '%PIPA%' OR placas ILIKE '%NPW%' OR tag ILIKE '%30874319%' OR tag ILIKE '%28600325%') GROUP BY semana, empresa, tag, no_economico, responsable, placas, tipo_unidad ORDER BY semana, tag;")
for r in cur.fetchall():
    print(dict(r))

conn.close()
