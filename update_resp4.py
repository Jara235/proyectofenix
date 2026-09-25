import sys
sys.path.append(r'c:\Users\JOSE\Desktop\Proyecto fenix')
from app_admin import get_db

db = get_db()

updates = [
    ("UPDATE diesel.consumos SET responsable = 'Samuel' WHERE obra_destino = 'Providencia' AND semana IN ('28', '29')", []),
    ("UPDATE diesel.consumos SET responsable = 'Diego Carreola' WHERE obra_destino = 'Vicente Lombardo' AND semana IN ('28', '29')", []),
    ("UPDATE diesel.consumos SET responsable = 'Diego Carreola' WHERE obra_destino = 'Desasolve' AND semana IN ('28', '29')", []),
    ("UPDATE diesel.consumos SET responsable = 'Apolinar' WHERE obra_destino = 'Alfredo del Mazo' AND semana = '28'", [])
]

for q, p in updates:
    cur = db.execute(q, tuple(p))
    print(f"Rows affected: {cur.rowcount} -> {q.split('WHERE')[1]}")

db.commit()
db.close()
