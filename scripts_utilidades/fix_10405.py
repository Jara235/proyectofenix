import psycopg2
conn=psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
conn.autocommit = True
cur=conn.cursor()

# Actualizar los litros de la factura 10405 a 400.004
cur.execute("UPDATE diesel.facturas SET litros_facturados = 400.004 WHERE folio_factura = '10405'")
print(f"Factura 10405 actualizada a 400.004 L. Registros modificados: {cur.rowcount}")

# Verificar los totales de Planta Huixquilucan para Semana 28
cur.execute("""
    SELECT folio_factura, litros_facturados 
    FROM diesel.facturas 
    WHERE obra_destino = 'Planta Huixquilucan' AND semana = 'Semana 28'
""")
rows = cur.fetchall()
total = 0
for r in rows:
    print(f"Factura {r[0]}: {r[1]} L")
    total += float(r[1])
print(f"Total Planta Huixquilucan: {total} L")
