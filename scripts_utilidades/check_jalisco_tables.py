import sys
sys.path.append(r'c:\Users\JOSE\Desktop\Proyecto fenix')
from app_admin import get_db

db = get_db()
rows = db.execute("SELECT table_name, column_name, data_type FROM information_schema.columns WHERE table_schema='diesel' AND table_name LIKE '%%jalisco%%'").fetchall()
for r in rows:
    print(dict(r))
db.close()
