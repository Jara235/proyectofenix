import sys
import os
sys.path.append(r"c:\Users\JOSE\Desktop\Proyecto fenix")
from app_admin import get_db

db = get_db()
print("Semanas en diesel.solicitudes:")
for r in db.execute("SELECT DISTINCT semana FROM diesel.solicitudes").fetchall():
    print(r['semana'])
