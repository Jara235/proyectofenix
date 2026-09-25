import sys
sys.path.append(r'c:\Users\JOSE\Desktop\Proyecto fenix')
from app_admin import get_db

db = get_db()

rows = db.execute("""
    SELECT 
        fecha,
        obra_destino,
        equipo,
        responsable,
        SUM(litros) as lts
    FROM diesel.consumos
    WHERE semana = '28'
    AND estatus_revision != 'RECHAZADO'
    GROUP BY fecha, obra_destino, equipo, responsable
    ORDER BY fecha, obra_destino, equipo
    LIMIT 30
""").fetchall()

for r in rows:
    print(dict(r))
db.close()
