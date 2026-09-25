from app_admin import get_db

db = get_db()
obras = [r['nombre'] for r in db.execute("SELECT nombre FROM catalogos.obras ORDER BY nombre").fetchall()]
print(f"Total obras: {len(obras)}")
for o in obras:
    print(f"'{o}',")
db.close()
