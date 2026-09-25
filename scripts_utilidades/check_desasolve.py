import sys
sys.path.append(r'c:\Users\JOSE\Desktop\Proyecto fenix')
from app_admin import get_db

db = get_db()
rows = db.execute("SELECT SUM(litros_facturados) as fac FROM diesel.facturas WHERE obra_destino='Desasolve' AND semana='28'").fetchall()
if rows and rows[0]['fac']:
    print("Desasolve Facturado Semana 28:", rows[0]['fac'])
else:
    print("No facturado found for Desasolve in week 28")
db.close()
