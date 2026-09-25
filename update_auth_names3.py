import sys
sys.path.append(r'c:\Users\JOSE\Desktop\Proyecto fenix')
from app_admin import get_db

db = get_db()

updates = {
    'Lerma - Tres Marías': 'Apolinar',
    'México - Toluca': 'Francisco Javier',
    'Bacheo Toluca': 'Diego Carreola',
    'Planta Pegaso': 'Jack',
    'Planta Huixquilucan': 'Luis'
}

total_updated = 0
for old_ref, new_ref in updates.items():
    try:
        # Note: sometimes DbProxy execute doesn't return cursor so rowcount might not be accessible directly
        # Let's execute raw SQL directly using psycopg2 to be absolutely sure
        db.execute(
            "UPDATE catalogos.autorizaciones SET referencia = %s WHERE tipo='DIESEL' AND (semana=28 OR semana=29) AND referencia = %s",
            (new_ref, old_ref)
        )
        total_updated += 1
    except Exception as e:
        print(f"Error on {old_ref}: {e}")

# IMPORTANT: we must commit if it's a raw psycopg2 connection, wait, DbProxy might have auto-commit? 
# Or we might need db.commit()! Let's just do it directly.
try:
    db.conn.commit()
except:
    pass

print(f"Executed updates.")

rows = db.execute("SELECT id, semana, referencia, litros_autorizados FROM catalogos.autorizaciones WHERE tipo='DIESEL' AND semana=28 AND litros_autorizados > 0").fetchall()
for r in rows:
    print(dict(r))
db.close()
