import sys
sys.path.append(r'c:\Users\JOSE\Desktop\Proyecto fenix')
from app_admin import get_db
db = get_db()
rows = db.execute("SELECT DISTINCT referencia FROM catalogos.autorizaciones").fetchall()
print("Referencias en autorizaciones:")
for r in rows:
    print(r[0])
db.close()
