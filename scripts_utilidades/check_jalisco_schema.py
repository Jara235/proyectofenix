import sys
sys.path.append(r'c:\Users\JOSE\Desktop\Proyecto fenix')
from app_admin import get_db

db = get_db()
rows = db.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_schema='jalisco'").fetchall()
for r in rows:
    print(f"Table: {r['column_name']}, Type: {r['data_type']}")
db.close()
