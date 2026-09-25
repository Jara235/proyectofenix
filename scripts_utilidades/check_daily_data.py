import sys
sys.path.append(r'c:\Users\JOSE\Desktop\Proyecto fenix')
from app_admin import get_db

db = get_db()

# Get a sample of daily consumption data for week 28 to understand the structure
rows = db.execute("""
    SELECT 
        c.fecha,
        c.obra_destino,
        c.maquinaria,
        c.operador,
        c.litros,
        c.responsable
    FROM diesel.consumos c
    WHERE c.semana = '28'
    AND c.estatus_revision != 'RECHAZADO'
    ORDER BY c.fecha, c.obra_destino, c.maquinaria
    LIMIT 30
""").fetchall()

for r in rows:
    print(dict(r))
db.close()
