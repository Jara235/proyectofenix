import sys
import os
sys.path.append(r"c:\Users\JOSE\Desktop\Proyecto fenix")
from app_admin import get_db
import re

db = get_db()
schemas = ['diesel', 'gasolina']
tables = ['solicitudes', 'facturas', 'consumos', 'jalisco_movimientos']

print("Updating 'semana' column to raw numbers across all schemas...")

for s in schemas:
    for t in tables:
        try:
            db.execute(f"UPDATE {s}.{t} SET semana = REPLACE(semana, 'Semana ', '') WHERE semana LIKE %s", ('Semana %',))
            db.execute(f"UPDATE {s}.{t} SET semana = REPLACE(semana, 'Semana', '') WHERE semana LIKE %s", ('Semana%',))
            db.execute(f"UPDATE {s}.{t} SET semana = TRIM(semana)")
        except Exception as e:
            db.conn.rollback()

db.close()
print("Done DB cleanup.")
