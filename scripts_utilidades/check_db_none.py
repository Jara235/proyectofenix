import sqlite3
db = sqlite3.connect('c:/Users/JOSE/Desktop/Proyecto fenix/fenix_v2.db')
res = db.execute('SELECT folio_conciliacion, equipo, equipo_economico FROM diesel_consumos ORDER BY id DESC LIMIT 5').fetchall()
print(res)

