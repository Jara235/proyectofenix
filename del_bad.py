import sqlite3
db = sqlite3.connect('fenix_v2.db')
db.execute("DELETE FROM gasolina_autorizaciones WHERE vehiculo = 'UNIDAD / EQUIPO'")
db.commit()
rows = db.execute("SELECT * FROM gasolina_autorizaciones WHERE estatus_autorizacion='en espera'").fetchall()
print(f'Total records en espera: {len(rows)}')
db.close()
