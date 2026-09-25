import psycopg2
conn=psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
conn.autocommit = True
cur=conn.cursor()

# FA-DPC-28-143: 915 LTS = 95 LTS Vicente Lombardo + 820 LTS Desasolve
# Currently assigned to Vicente Lombardo (350.001 total lit from ticket split)
# Let's check what is in DB
cur.execute("SELECT id, folio_conciliacion, obra_destino, litros_facturados, punto_de_carga FROM diesel.facturas WHERE folio_conciliacion = 'FA-DPC-28-143'")
r = cur.fetchone()
print("Current:", r)

if r:
    fac_id = r[0]
    # Update original to Desasolve with 820 lts portion (the main one)
    cur.execute("UPDATE diesel.facturas SET obra_destino = 'Desasolve', litros_facturados = 820.000 WHERE id = %s", (fac_id,))
    print(f"  Updated id={fac_id} -> Desasolve 820 lts")
    
    # Insert a split entry for Vicente Lombardo 95 lts
    cur.execute("""
        INSERT INTO diesel.facturas 
        (folio_conciliacion, folio_factura, fecha_factura, semana, proveedor, punto_de_carga, litros_facturados, precio_unitario, importe, importe_total, obra_destino, estatus_revision)
        SELECT 'FA-DPC-28-143-VL', folio_factura, fecha_factura, semana, proveedor, punto_de_carga, 95.000, 0, 0, 0, 'Vicente Lombardo', estatus_revision
        FROM diesel.facturas WHERE folio_conciliacion = 'FA-DPC-28-143'
    """)
    print(f"  Inserted Vicente Lombardo split: {cur.rowcount}")

# Verify Semana 28 final state
print("\n=== FINAL by obra Semana 28 ===")
cur.execute("""
    SELECT obra_destino, ROUND(SUM(litros_facturados)::numeric, 2) as total_lts
    FROM diesel.facturas WHERE semana = 'Semana 28'
    GROUP BY obra_destino ORDER BY obra_destino
""")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]} L")
