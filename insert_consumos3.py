import sys
sys.path.append(r'c:\Users\JOSE\Desktop\Proyecto fenix')
from app_admin import get_db

db = get_db()

# Insert Desasolve
db.execute(
    "INSERT INTO diesel.consumos (semana, fecha, obra_destino, responsable, litros, estatus_revision, usuario_captura) VALUES (%s, %s, %s, %s, %s, %s, %s)",
    ('28', '2026-07-10', 'Desasolve', 'Diego Carreola', 1774.49, 'APROBADO', 'sistema_ia')
)

# Insert Maquinaria Pegaso
db.execute(
    "INSERT INTO diesel.consumos (semana, fecha, obra_destino, responsable, litros, estatus_revision, usuario_captura) VALUES (%s, %s, %s, %s, %s, %s, %s)",
    ('28', '2026-07-10', 'Maquinaria Pegaso', 'Dayanne', 100, 'APROBADO', 'sistema_ia')
)

db.commit()
print("Inserted successfully.")
db.close()
