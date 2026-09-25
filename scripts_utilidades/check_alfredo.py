import sys
sys.path.append(r'c:\Users\JOSE\Desktop\Proyecto fenix')
from app_admin import get_db
db = get_db()
rows = db.execute("SELECT id, fecha, obra_destino, litros FROM diesel.consumos WHERE semana='28' AND obra_destino='Alfredo del Mazo'").fetchall()
for r in rows:
    print(dict(r))
db.close()
