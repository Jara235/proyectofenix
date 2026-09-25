import sys
sys.path.append(r'c:\Users\JOSE\Desktop\Proyecto fenix')
from app_admin import get_db

db = get_db()
cur = db.cursor()

updates = [
    ("UPDATE diesel.consumos SET responsable = 'Javier Francisco' WHERE obra_destino = 'Alfredo del Mazo' AND fecha IN ('2026-07-10', '2026-07-13', '2026-07-16')", []),
    ("UPDATE diesel.consumos SET responsable = 'Edgar' WHERE obra_destino = 'Alfredo del Mazo' AND fecha = '2026-07-15'", []),
    ("UPDATE diesel.consumos SET responsable = 'Apolinar' WHERE obra_destino = 'Alfredo del Mazo' AND fecha = '2026-07-17'", []),
    ("UPDATE diesel.consumos SET responsable = 'Diego Carreola' WHERE obra_destino = 'Bacheo Toluca' AND semana IN ('28', '29')", []),
    ("UPDATE diesel.consumos SET responsable = 'Apolinar' WHERE obra_destino = 'Colegio Militar' AND semana IN ('28', '29')", []),
    ("UPDATE diesel.consumos SET responsable = 'Apolinar' WHERE obra_destino = 'Lerma - Tres Marías' AND semana IN ('28', '29')", []),
    ("UPDATE diesel.consumos SET responsable = 'Dayanne' WHERE obra_destino = 'Maquinaria Pegaso' AND semana IN ('28', '29')", []),
    ("UPDATE diesel.consumos SET responsable = 'Francisco Javier' WHERE obra_destino = 'México - Toluca' AND semana IN ('28', '29')", []),
    ("UPDATE diesel.consumos SET responsable = 'Luis' WHERE obra_destino = 'Planta Huixquilucan' AND semana IN ('28', '29')", []),
    ("UPDATE diesel.consumos SET responsable = 'Jack' WHERE obra_destino = 'Planta Pegaso' AND semana IN ('28', '29')", [])
]

for q, p in updates:
    cur.execute(q, p)
    print(f"Rows affected: {cur.rowcount} -> {q.split('WHERE')[1]}")

db.commit()
db.close()
