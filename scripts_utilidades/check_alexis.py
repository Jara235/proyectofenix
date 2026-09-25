import sqlite3
db = sqlite3.connect('c:/Users/JOSE/Desktop/Proyecto fenix/fenix_v2.db')
c = db.cursor()
c.execute('SELECT numero_economico, descripcion, operador_default FROM catalogos_equipos WHERE operador_default LIKE "%ALEXIS%"')
for row in c.fetchall(): print(row)
db.close()

