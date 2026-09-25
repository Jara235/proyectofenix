import sqlite3
db = sqlite3.connect('c:/Users/JOSE/Desktop/Proyecto fenix/fenix_v2.db')

# Fix weeks without 'Semana ' prefix
updated = db.execute("UPDATE diesel_consumos SET semana='Semana '||semana WHERE semana NOT LIKE 'Semana %'").rowcount
db.commit()
print(f'Fixed {updated} records with missing Semana prefix')
db.close()
