import psycopg2
conn=psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
conn.autocommit = True
cur=conn.cursor()

# Fix the 3 unclear ones manually
cur.execute("UPDATE diesel.facturas SET obra_destino = 'Planta Pegaso' WHERE folio_factura = '10380' AND folio_conciliacion = 'FA-DPC-28-115'")
print(f"10380 -> Planta Pegaso: {cur.rowcount}")

cur.execute("UPDATE diesel.facturas SET obra_destino = 'Obra sin asignar' WHERE folio_factura = '10394' AND folio_conciliacion = 'FA-DPC-28-121'")
print(f"10394 (Transportes Flotilla) -> Obra sin asignar: {cur.rowcount}")

cur.execute("UPDATE diesel.facturas SET obra_destino = 'Obra sin asignar' WHERE folio_factura = '10906' AND folio_conciliacion = 'FA-DPC-28-147'")
print(f"10906 (Gasolina Flotilla) -> Obra sin asignar: {cur.rowcount}")

# Also fix FA-DPC-28-130 which was tagged as 'Tanque Pegaso' (storage tank = Planta Pegaso)
cur.execute("UPDATE diesel.facturas SET obra_destino = 'Planta Pegaso' WHERE folio_conciliacion = 'FA-DPC-28-130'")
print(f"FA-DPC-28-130 -> Planta Pegaso: {cur.rowcount}")

# ============================================================
# Now check: facturas MARKED as gasolina but in diesel
# These two (10910, 10911) say "gasolina" in description but seem to be in diesel
# They're for Lerma trucks - CHECK point_de_carga
# ============================================================
cur.execute("""
    SELECT folio_factura, folio_conciliacion, obra_destino, punto_de_carga, litros_facturados
    FROM diesel.facturas 
    WHERE folio_factura IN ('10910', '10911')
""")
print("\nLerma gasolina-tagged entries:")
for r in cur.fetchall():
    print(r)

# Final count by obra
print("\n=== FINAL FACTURAS BY OBRA (Semana 28) ===")
cur.execute("""
    SELECT obra_destino, COUNT(*) as n_facturas, SUM(litros_facturados) as total_lts
    FROM diesel.facturas WHERE semana = 'Semana 28'
    GROUP BY obra_destino ORDER BY obra_destino
""")
for r in cur.fetchall():
    print(r)
