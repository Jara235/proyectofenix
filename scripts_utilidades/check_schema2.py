import sqlite3
db = sqlite3.connect('c:/Users/JOSE/Desktop/Proyecto fenix/fenix_v2.db')
c = db.cursor()
c.execute('PRAGMA table_info(diesel_consumos)')
print([r[1] for r in c.fetchall()])

