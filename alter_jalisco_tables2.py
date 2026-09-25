import sys
sys.path.append(r'c:\Users\JOSE\Desktop\Proyecto fenix')
from app_admin import get_db

db = get_db()
cur = db.conn.cursor()

try:
    cur.execute("ALTER TABLE diesel.jalisco_movimientos ADD COLUMN tipo_combustible VARCHAR(20) DEFAULT 'DIESEL'")
    print("Added tipo_combustible to jalisco_movimientos.")
except Exception as e:
    print(e)
    db.conn.rollback()

try:
    # Need to drop constraint because now a week can have both diesel and gasolina vales
    cur.execute("ALTER TABLE diesel.control_vales_jalisco ADD COLUMN tipo_combustible VARCHAR(20) DEFAULT 'DIESEL'")
    cur.execute("ALTER TABLE diesel.control_vales_jalisco DROP CONSTRAINT IF EXISTS control_vales_jalisco_semana_key")
    cur.execute("ALTER TABLE diesel.control_vales_jalisco ADD CONSTRAINT control_vales_jalisco_semana_tipo_key UNIQUE (semana, tipo_combustible)")
    print("Added tipo_combustible to control_vales_jalisco.")
except Exception as e:
    print(e)
    db.conn.rollback()

db.conn.commit()
db.close()
