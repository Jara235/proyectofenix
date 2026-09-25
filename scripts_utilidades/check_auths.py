import sys
sys.path.append(r'c:\Users\JOSE\Desktop\Proyecto fenix')
from app_admin import get_db

db = get_db()
rows = db.execute("SELECT * FROM catalogos.autorizaciones WHERE tipo='DIESEL' AND semana=28 LIMIT 5").fetchall()
for r in rows:
    print(dict(r))
db.close()
