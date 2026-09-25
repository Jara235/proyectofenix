from app_admin import get_db

db = get_db()
db.execute("UPDATE gasolina.autorizaciones_semanal SET importe_semanal = 4000.00 WHERE semana = 33 AND responsable ILIKE '%%SAMUEL ORTEGA%%'")
print("Samuel S33 authorization updated to $4,000.00")
db.close()
