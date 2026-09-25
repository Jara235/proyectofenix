import sqlite3, re
db = sqlite3.connect('c:/Users/JOSE/Desktop/Proyecto fenix/fenix.db')
c = db.cursor()
c.execute("SELECT folio, fecha_emision, nota_leyenda FROM fenix_facturas_documentos WHERE tipo_combustible='Diesel' AND semana=27")
rows = c.fetchall()
for r in rows:
    print(r)
db.close()

