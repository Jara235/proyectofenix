import sys
sys.path.append(r'c:\Users\JOSE\Desktop\Proyecto fenix')
from app_admin import get_db

db = get_db()

# Fix diesel.solicitudes: 'Semana 28' -> '28', 'Semana 29' -> '29'
print('Fixing diesel.solicitudes...')
db.execute("UPDATE diesel.solicitudes SET semana = regexp_replace(semana::text, 'Semana\s+', '', 'g') WHERE semana::text LIKE 'Semana%%'")
db.commit()
res = db.execute("SELECT DISTINCT semana::text FROM diesel.solicitudes ORDER BY semana::text").fetchall()
print('After fix:', [r[0] for r in res])

# Check gasolina tables too
res5 = db.execute("SELECT DISTINCT semana::text FROM gasolina.consumos ORDER BY semana::text").fetchall()
print('Semanas gasolina.consumos:', [r[0] for r in res5])

res6 = db.execute("SELECT DISTINCT semana::text FROM gasolina.facturas ORDER BY semana::text").fetchall()
print('Semanas gasolina.facturas:', [r[0] for r in res6])

db.close()
