import sqlite3
db = sqlite3.connect('c:/Users/JOSE/Desktop/Proyecto fenix/fenix_v2.db')
cur = db.cursor()
cur.execute('PRAGMA table_info(diesel_consumos)')
for row in cur.fetchall(): print(row[1])

