import psycopg2
import json

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
conn.autocommit = True
cur = conn.cursor()

with open('plan.json', 'r') as f:
    plan = json.load(f)

print(f"Applying plan: DELETE {len(plan['delete'])} rows, UPDATE {len(plan['update'])} rows.")

for del_id in plan['delete']:
    cur.execute("DELETE FROM diesel.facturas WHERE id = %s", (del_id,))
    print(f"Deleted ID {del_id}")

for up_id, lts, fol in plan['update']:
    cur.execute("UPDATE diesel.facturas SET litros_facturados = %s WHERE id = %s", (lts, up_id))
    print(f"Updated ID {up_id} to {lts} L")

print("All fixes applied successfully.")
