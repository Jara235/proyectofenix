import sys
sys.path.append(r'c:\Users\JOSE\Desktop\Proyecto fenix')
from app_admin import get_db

db = get_db()
# ILIKE uses % which conflicts with psycopg2 param substitution - escape it
res = db.execute("SELECT COUNT(*) FROM diesel.solicitudes WHERE semana::text LIKE 'Semana%%'").fetchone()
print('diesel.solicitudes sucias:', res[0])

res2 = db.execute("SELECT DISTINCT semana::text FROM diesel.solicitudes ORDER BY semana::text").fetchall()
print('Semanas diesel.solicitudes:', [r[0] for r in res2])

res3 = db.execute("SELECT DISTINCT semana::text FROM diesel.facturas ORDER BY semana::text").fetchall()
print('Semanas diesel.facturas:', [r[0] for r in res3])

res4 = db.execute("SELECT DISTINCT semana::text FROM diesel.consumos ORDER BY semana::text").fetchall()
print('Semanas diesel.consumos:', [r[0] for r in res4])
db.close()
