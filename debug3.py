# -*- coding: utf-8 -*-
import sys
sys.path.append(r'c:\Users\JOSE\Desktop\Proyecto fenix')
from app_admin import get_db
db = get_db()

rows = db.execute("SELECT DISTINCT obra_destino FROM diesel.solicitudes WHERE obra_destino LIKE '%%Pegaso%%' ORDER BY obra_destino").fetchall()
print("Obras Pegaso en solicitudes:")
for r in rows:
    print(" ->", r[0])

rows2 = db.execute("SELECT DISTINCT obra_destino FROM diesel.consumos WHERE obra_destino LIKE '%%Pegaso%%' ORDER BY obra_destino").fetchall()
print("Obras Pegaso en consumos:")
for r in rows2:
    print(" ->", r[0])
db.close()
