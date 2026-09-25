import sqlite3
db = sqlite3.connect('c:/Users/JOSE/Desktop/Proyecto fenix/fenix_v2.db')
cur = db.cursor()
cur.execute('SELECT COUNT(*) FROM catalogos_equipos')
print('Equipos en BD:', cur.fetchone()[0])

