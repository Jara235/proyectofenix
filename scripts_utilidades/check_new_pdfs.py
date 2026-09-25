import sqlite3
db = sqlite3.connect('c:/Users/JOSE/Desktop/Proyecto fenix/fenix.db')
c = db.cursor()
c.execute("SELECT folio, texto_pdf_extraido FROM fenix_facturas_documentos WHERE folio IN ('10198', '10213', '10214', '10216', '10217', '10225', '10226')")
for r in c.fetchall():
    texto = str(r[1]).lower()
    if 'magna' in texto or 'premium' in texto or 'gasolina' in texto or 'extra' in texto:
        print(f'Found Gasolina in {r[0]}')
        c.execute("UPDATE fenix_facturas_documentos SET tipo_combustible='Gasolina' WHERE folio=?", (r[0],))
db.commit()
db.close()

