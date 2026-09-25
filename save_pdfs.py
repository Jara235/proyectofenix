import psycopg2, io
conn=psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur=conn.cursor()

# Save the PDFs of 10405 and 10407 to disk to review them
for folio_fac, folio_con in [('10405','FA-DPC-28-125'), ('10407','FA-DPC-28-127')]:
    cur.execute("SELECT archivo_pdf FROM diesel.facturas WHERE folio_factura = %s AND folio_conciliacion = %s", (folio_fac, folio_con))
    row = cur.fetchone()
    if row and row[0]:
        with open(f'factura_{folio_fac}.pdf', 'wb') as f:
            f.write(bytes(row[0]))
        print(f"Saved factura_{folio_fac}.pdf")
    else:
        print(f"No PDF for {folio_fac}")
