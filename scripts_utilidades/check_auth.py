import sys
sys.path.append(r'c:\Users\JOSE\Desktop\Proyecto fenix')
from app_admin import get_db
db = get_db()
rows = db.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = 'catalogos' AND table_name = 'autorizaciones'").fetchall()
for r in rows:
    print(r[0], r[1])
db.close()
