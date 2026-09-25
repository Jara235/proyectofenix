import sys
import os
sys.path.append(r"c:\Users\JOSE\Desktop\Proyecto fenix")
from app_admin import get_db

db = get_db()
schemas = ['diesel', 'gasolina']
tables = ['solicitudes', 'facturas', 'consumos']

print("Updating 'semana' column to raw numbers across all schemas...")

for s in schemas:
    for t in tables:
        try:
            db.execute(f"UPDATE {s}.{t} SET semana = REPLACE(semana, 'Semana ', '') WHERE semana LIKE %s", ('Semana %',))
            print(f"Updated {s}.{t} - replaced 'Semana '")
            
            db.execute(f"UPDATE {s}.{t} SET semana = TRIM(semana)")
            print(f"Updated {s}.{t} - trimmed")
        except Exception as e:
            print(f"Error in {s}.{t}: {e}")
            db.conn.rollback()

# Check what the final DB data looks like
for r in db.execute("SELECT DISTINCT semana FROM diesel.solicitudes").fetchall():
    print("diesel.solicitudes:", r['semana'])

db.close()
print("Done.")
