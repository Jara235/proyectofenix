import sys
sys.path.append(r'c:\Users\JOSE\Desktop\Proyecto fenix')
from app_admin import get_db

db = get_db()
cur = db.cursor()

updates = {
    'Lerma - Tres Marías': 'Apolinar',
    'México - Toluca': 'Francisco Javier',
    'Bacheo Toluca': 'Diego Carreola',
    'Planta Pegaso': 'Jack',
    'Planta Huixquilucan': 'Luis'
}

for old_ref, new_ref in updates.items():
    cur.execute(
        "UPDATE catalogos.autorizaciones SET referencia = %s WHERE tipo='DIESEL' AND (semana=28 OR semana=29) AND referencia = %s AND litros_autorizados > 0",
        (new_ref, old_ref)
    )

db.commit()
print("Updated successfully.")
db.close()
