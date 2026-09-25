import sys
sys.path.append(r'c:\Users\JOSE\Desktop\Proyecto fenix')
from app_admin import get_db

db = get_db()
cur = db.connection.cursor()

try:
    cur.execute("ALTER TABLE diesel.jalisco_movimientos ADD COLUMN tipo_combustible VARCHAR(20) DEFAULT 'DIESEL'")
    print("Added tipo_combustible to jalisco_movimientos.")
except Exception as e:
    print(e)
    db.connection.rollback()

try:
    cur.execute("ALTER TABLE diesel.control_vales_jalisco ADD COLUMN tipo_combustible VARCHAR(20) DEFAULT 'DIESEL'")
    print("Added tipo_combustible to control_vales_jalisco.")
except Exception as e:
    print(e)
    db.connection.rollback()

db.connection.commit()
db.close()
