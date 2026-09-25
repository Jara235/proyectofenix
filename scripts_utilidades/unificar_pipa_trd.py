import psycopg2
from psycopg2.extras import DictCursor

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

# 1. Unificar autorizaciones en tags.autorizaciones
# Eliminar el registro duplicado con $0.00 (IMDM28600325)
cur.execute("""
    DELETE FROM tags.autorizaciones
    WHERE empresa = 'TRD' AND tag = 'IMDM28600325';
""")

# Actualizar el registro principal de Pipa de Agua en tags.autorizaciones
cur.execute("""
    UPDATE tags.autorizaciones
    SET responsable = 'PIPA DE AGUA',
        no_economico = 'PIPA DE AGUA (NPW1169)',
        placas = 'NPW1169',
        tipo_unidad = 'PIPA DE AGUA',
        monto_autorizado = 1000.00,
        estatus = 'ACTIVO'
    WHERE empresa = 'TRD' AND (tag = 'IMDM30874319' OR responsable ILIKE '%PIPA%');
""")

# 2. Unificar movimientos en tags.movimientos
cur.execute("""
    UPDATE tags.movimientos
    SET responsable = 'PIPA DE AGUA',
        no_economico = 'PIPA DE AGUA (NPW1169)',
        placas = 'NPW1169',
        tipo_unidad = 'PIPA DE AGUA'
    WHERE empresa = 'TRD' AND (
        tag ILIKE '%30874319%' OR 
        tag ILIKE '%3087431P%' OR 
        tag ILIKE '%28600325%' OR 
        responsable ILIKE '%PIPA%' OR 
        no_economico ILIKE '%PIPA%'
    );
""")

conn.commit()

# 3. Verificar
cur.execute("SELECT * FROM tags.autorizaciones WHERE empresa = 'TRD' AND responsable ILIKE '%PIPA%';")
print("=== AUTORIZACIÓN TRD PIPA UNIFICADA ===")
for r in cur.fetchall():
    print(dict(r))

cur.execute("""
    SELECT semana, empresa, responsable, placas, COUNT(*) as pasadas, SUM(ABS(importe)) as total_consumo
    FROM tags.movimientos
    WHERE empresa = 'TRD' AND responsable = 'PIPA DE AGUA'
    GROUP BY semana, empresa, responsable, placas
    ORDER BY semana;
""")
print("\n=== CONSUMOS POR SEMANA PIPA DE AGUA UNIFICADOS ===")
for r in cur.fetchall():
    print(dict(r))

conn.close()
