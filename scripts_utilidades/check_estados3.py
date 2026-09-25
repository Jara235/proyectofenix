import sqlite3
db = r'c:\Users\JOSE\Desktop\Proyecto fenix\fenix_v2.db'
c = sqlite3.connect(db)
cur = c.cursor()
cur.execute("SELECT placa, vehiculo, SUM(importe_autorizado), SUM(consumo_real) FROM gasolina_estados_cuenta WHERE semana='Semana 26' GROUP BY placa, vehiculo")
print("estados cuenta:")
for r in cur.fetchall(): print(r)

cur.execute("SELECT placa, vehiculo, SUM(importe_total), SUM(litros) FROM gasolina_consumos WHERE semana='Semana 26' GROUP BY placa, vehiculo")
print("\nconsumos:")
for r in cur.fetchall(): print(r)
c.close()
