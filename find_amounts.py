import sqlite3
db = sqlite3.connect('c:/Users/JOSE/Desktop/Proyecto fenix/fenix.db')
c = db.cursor()
c.execute("SELECT folio, fecha_emision, litros_totales, nota_leyenda FROM fenix_facturas_documentos WHERE tipo_combustible='Diesel' AND semana IN (26,27)")
rows = c.fetchall()
target_lts = [400, 290, 600, 200]
print('Matching invoices for unassigned physical loads:')
for r in rows:
    lts = round(r[2], 0)
    if lts in target_lts:
        print(f'Folio: {r[0]:>8} | Litros: {lts} ({r[2]}) | Fecha: {r[1]} | Leyenda: {r[3]}')
db.close()

