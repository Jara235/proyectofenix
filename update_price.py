import sqlite3
db = sqlite3.connect('c:/Users/JOSE/Desktop/Proyecto fenix/fenix_v2.db')
c = db.cursor()
c.execute('UPDATE diesel_consumos SET costo_por_litro = 27.0, importe_total = litros * 27.0')
db.commit()
print('Filas actualizadas:', c.rowcount)
db.close()

