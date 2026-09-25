import sys
sys.path.append(r'c:\Users\JOSE\Desktop\Proyecto fenix')
from app_admin import get_db

db = get_db()
rows = db.execute("SELECT id, fecha, obra_destino, responsable, semana FROM diesel.consumos WHERE semana = '28'").fetchall()
for r in rows:
    print(dict(r))
db.close()
