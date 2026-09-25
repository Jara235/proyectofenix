import sqlite3
db = sqlite3.connect('fenix_v2.db')
db.row_factory = sqlite3.Row
rows = db.execute("SELECT * FROM gasolina_autorizaciones WHERE estatus_autorizacion='en espera'").fetchall()
print(f'Total records en espera: {len(rows)}')
for r in rows:
    print(f"Obra: {r['obra_destino']:<15} | Vehiculo: {r['vehiculo']:<20} | Importe: {r['importe_autorizado']:>6} | Estatus: {r['estatus_autorizacion']} | Resp: {r['responsable']}")
db.close()
