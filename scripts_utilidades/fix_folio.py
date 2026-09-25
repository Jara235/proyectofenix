import sqlite3
db = sqlite3.connect('c:/Users/JOSE/Desktop/Proyecto fenix/fenix_v2.db')
c = db.cursor()
c.execute('UPDATE diesel_consumos SET folio_conciliacion = ? WHERE folio_conciliacion = ?', ('CMQ-L3M-28-302', 'DSL-20260707123123'))
db.commit()
print('Folio actualizado.')

