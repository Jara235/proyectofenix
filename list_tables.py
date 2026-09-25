from app_admin import get_db

db = get_db()
dtables = db.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'diesel'").fetchall()
gtables = db.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'gasolina'").fetchall()
ctables = db.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'catalogos'").fetchall()

print("Diesel tables:", [t['table_name'] for t in dtables])
print("Gasolina tables:", [t['table_name'] for t in gtables])
print("Catalogos tables:", [t['table_name'] for t in ctables])

db.close()
