from app_admin import get_db

db = get_db()
obras = [r['nombre_obra'] for r in db.execute("SELECT nombre_obra FROM catalogos.obras ORDER BY nombre_obra").fetchall()]
print("Available obras in catalogos.obras:")
for o in obras:
    if any(k in o.upper() for k in ['HUIX', 'PEGASO', 'LERMA', 'TOLUCA', 'CORP', 'BACHEO', 'MINA', 'JALISCO']):
        print(" -", o)
db.close()
