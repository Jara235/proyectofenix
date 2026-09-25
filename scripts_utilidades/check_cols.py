import sys
sys.path.append(r'c:\Users\JOSE\Desktop\Proyecto fenix')
from app_admin import get_db
db = get_db()
rows = db.execute("SELECT column_name FROM information_schema.columns WHERE table_schema='diesel' AND table_name='consumos'").fetchall()
print([r[0] for r in rows])
db.close()
