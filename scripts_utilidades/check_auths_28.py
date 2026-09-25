import sys
sys.path.append(r'c:\Users\JOSE\Desktop\Proyecto fenix')
from app_admin import get_db

db = get_db()
rows = db.execute("SELECT referencia, litros_autorizados FROM catalogos.autorizaciones WHERE tipo='DIESEL' AND semana=28 AND litros_autorizados > 0").fetchall()
for r in rows:
    print(dict(r))
db.close()
