import sqlite3

db = r'c:\Users\JOSE\Desktop\Proyecto fenix\fenix_v2.db'
c = sqlite3.connect(db)
cur = c.cursor()

cur.execute("SELECT semana, COUNT(*), SUM(importe_autorizado), SUM(litros_reales) FROM gasolina_estados_cuenta GROUP BY semana")
for r in cur.fetchall():
    print(f"Semana {r[0]}: {r[1]} registros | Importe: {r[2]} | Litros: {r[3]}")
c.close()
