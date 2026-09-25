import psycopg2
conn=psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur=conn.cursor()

# Check facturas in diesel that might be gasolina
cur.execute("""
SELECT folio_factura, folio_conciliacion, obra_destino, litros_facturados, semana, punto_de_carga, proveedor
FROM diesel.facturas 
ORDER BY semana, folio_conciliacion
""")
rows = cur.fetchall()
print(f"Total facturas diesel: {len(rows)}")
print("---")
for r in rows:
    print(r)
