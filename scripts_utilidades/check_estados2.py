import sqlite3
db = r'c:\Users\JOSE\Desktop\Proyecto fenix\fenix_v2.db'
c = sqlite3.connect(db)
cur = c.cursor()
cur.execute("SELECT semana, gasolinera, SUM(importe_autorizado), SUM(consumo_real), SUM(litros_reales) FROM gasolina_estados_cuenta GROUP BY semana, gasolinera")
print("estados cuenta:")
for r in cur.fetchall(): print(r)

cur.execute("SELECT semana, origen, SUM(importe_total), SUM(litros) FROM gasolina_consumos GROUP BY semana, origen")
print("\nconsumos:")
for r in cur.fetchall(): print(r)
c.close()
