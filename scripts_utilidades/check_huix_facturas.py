import psycopg2
conn=psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur=conn.cursor()

# Check facturas 10405, 10406, 10407
cur.execute("""
SELECT id, folio_factura, folio_conciliacion, obra_destino, litros_facturados, punto_de_carga, archivo_pdf
FROM diesel.facturas 
WHERE folio_factura IN ('10405', '10406', '10407')
ORDER BY folio_factura, folio_conciliacion
""")
print("=== FACTURAS 10405, 10406, 10407 ===")
for r in cur.fetchall():
    print(f"  id={r[0]} folio_fac={r[1]} folio_con={r[2]} obra={r[3]} litros={r[4]}")
    print(f"    desc: {r[5]}")
    print(f"    pdf:  {r[6]}")

# Also check all Planta Huixquilucan facturas for Semana 28
print("\n=== ALL Planta Huixquilucan Semana 28 ===")
cur.execute("""
SELECT id, folio_factura, folio_conciliacion, litros_facturados, punto_de_carga, fecha_factura
FROM diesel.facturas 
WHERE obra_destino = 'Planta Huixquilucan' AND semana = 'Semana 28'
ORDER BY fecha_factura, folio_factura
""")
total = 0
for r in cur.fetchall():
    print(f"  {r[1]} ({r[2]}) fecha={r[5]} litros={r[3]}")
    print(f"    desc: {r[4]}")
    total += float(r[3])
print(f"  TOTAL: {total:.3f} L")
