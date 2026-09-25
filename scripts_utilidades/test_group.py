import sys
import json
sys.path.append(r'c:\Users\JOSE\Desktop\Proyecto fenix')
from app_admin import get_db
db = get_db()

query = """
WITH con AS (
    SELECT obra_destino as obra,
           NULLIF(NULLIF(responsable, 'nan'), '') as responsable,
           SUM(litros) as consumido
    FROM diesel.consumos
    WHERE semana = '28' AND obra_destino NOT ILIKE '%%Tanque Pegaso%%' AND estatus_revision = 'APROBADO'
    GROUP BY obra_destino, responsable
)
SELECT * FROM con ORDER BY obra
"""
rows = db.execute(query).fetchall()
for r in rows:
    print(r[0], "|", r[1], "|", r[2])

db.close()
