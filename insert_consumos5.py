import sys
sys.path.append(r'c:\Users\JOSE\Desktop\Proyecto fenix')
from app_admin import get_db

db = get_db()

# Insert Desasolve
db.execute(
    "INSERT INTO diesel.consumos (folio_conciliacion, semana, fecha, obra_destino, responsable, litros, costo_por_litro, importe_total, estatus_revision, usuario_captura) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
    ('AUTO-DES-28', '28', '2026-07-10', 'Desasolve', 'Diego Carreola', 1774.49, 0, 0, 'APROBADO', 'sistema_ia')
)

# Insert Maquinaria Pegaso
db.execute(
    "INSERT INTO diesel.consumos (folio_conciliacion, semana, fecha, obra_destino, responsable, litros, costo_por_litro, importe_total, estatus_revision, usuario_captura) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
    ('AUTO-MAQ-28', '28', '2026-07-10', 'Maquinaria Pegaso', 'Dayanne', 100, 0, 0, 'APROBADO', 'sistema_ia')
)

db.commit()
print("Inserted successfully.")
db.close()
