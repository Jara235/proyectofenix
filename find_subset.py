import sqlite3, itertools
db = sqlite3.connect('c:/Users/JOSE/Desktop/Proyecto fenix/fenix.db')
c = db.cursor()
c.execute("SELECT folio, litros_totales, total FROM fenix_facturas_documentos WHERE tipo_combustible='Diesel' AND fecha_emision >= '2026-06-22' AND fecha_emision <= '2026-07-02'")
rows = c.fetchall()
print('Trying to find subset of invoices that sum to 2913 liters...')
# This is the subset sum problem. We will just print all invoices and their liters around week 26/27.
for r in rows: print(r)
db.close()

