from app_admin import get_db

db = get_db()
c = db.execute("SELECT id, fecha, conductor, importe_total FROM gasolina.consumos WHERE semana = '33' LIMIT 10").fetchall()
for r in c:
    print(r['id'], repr(r['fecha']), r['conductor'], r['importe_total'])
db.close()
