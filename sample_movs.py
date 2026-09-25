from app_admin import get_db

db = get_db()
cur = db.execute("SELECT * FROM tags.movimientos WHERE semana = 'SEMANA 32' LIMIT 5;")
rows = cur.fetchall()
print("Sample SEMANA 32 records in tags.movimientos:")
for r in rows:
    print(dict(r))

db.close()
