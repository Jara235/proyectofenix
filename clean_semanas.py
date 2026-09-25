import sys
import psycopg2

DB_URL = "postgresql://postgres:postgres@localhost:5432/fenix_db"
conn = psycopg2.connect(DB_URL)
cur = conn.cursor()

schemas = ['diesel', 'gasolina', 'jalisco']
tables = ['solicitudes', 'facturas', 'consumos']

print("Updating 'semana' column to raw numbers across all schemas...")

for s in schemas:
    for t in tables:
        try:
            cur.execute(f"UPDATE {s}.{t} SET semana = REPLACE(semana, 'Semana ', '') WHERE semana LIKE 'Semana %'")
            conn.commit()
            print(f"Updated {s}.{t} - {cur.rowcount} rows affected.")
            
            # Trim any whitespace just in case
            cur.execute(f"UPDATE {s}.{t} SET semana = TRIM(semana)")
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Error in {s}.{t}: {e}")

print("Done.")
