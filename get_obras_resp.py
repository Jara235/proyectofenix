# -*- coding: utf-8 -*-
import sys
import json
sys.path.append(r'c:\Users\JOSE\Desktop\Proyecto fenix')
from app_admin import get_db

db = get_db()
query = """
    SELECT DISTINCT obra_destino, responsable 
    FROM diesel.solicitudes 
    WHERE semana = '28' AND obra_destino IS NOT NULL
    UNION
    SELECT DISTINCT obra_destino, responsable 
    FROM diesel.consumos 
    WHERE semana = '28' AND obra_destino IS NOT NULL
    ORDER BY obra_destino
"""
rows = db.execute(query).fetchall()
result = [{"obra": r[0], "responsable": r[1]} for r in rows]
print(json.dumps(result, ensure_ascii=False, indent=2))
db.close()
