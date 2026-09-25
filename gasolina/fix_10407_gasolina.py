import psycopg2
conn=psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
conn.autocommit = True
cur=conn.cursor()

# 1. Move factura 10407 (EXTRA/Gasolina) OUT of diesel.facturas
# We need to add it to gasolina.facturas or at minimum remove from diesel
# First check gasolina.facturas schema
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema='gasolina' AND table_name='facturas' ORDER BY ordinal_position")
cols = [r[0] for r in cur.fetchall()]
print("Gasolina facturas columns:", cols)

# Get the full row from diesel.facturas
cur.execute("SELECT * FROM diesel.facturas WHERE folio_factura = '10407' AND folio_conciliacion = 'FA-DPC-28-127'")
row = cur.fetchone()
if row:
    print(f"\nFactura 10407 found: {row[0]} | litros={row[7]}")
    # Delete from diesel
    cur.execute("DELETE FROM diesel.facturas WHERE folio_factura = '10407' AND folio_conciliacion = 'FA-DPC-28-127'")
    print(f"  Deleted from diesel.facturas: {cur.rowcount}")

# 2. Check all other facturas that might be gasolina (SAT code 32025 = gasolina)
# We need to look at PDFs for any with "EXTRA" or "MAGNA" in their description
cur.execute("""
    SELECT id, folio_factura, folio_conciliacion, obra_destino, litros_facturados, punto_de_carga
    FROM diesel.facturas
    WHERE LOWER(punto_de_carga) LIKE '%extra%'
       OR LOWER(punto_de_carga) LIKE '%magna%'
       OR LOWER(punto_de_carga) LIKE '%litros de gasolina%'
       OR LOWER(punto_de_carga) LIKE '%gaso%'
    ORDER BY semana, folio_factura
""")
posibles_gas = cur.fetchall()
print(f"\n=== POSSIBLE GASOLINA in diesel ({len(posibles_gas)}) ===")
for r in posibles_gas:
    print(f"  id={r[0]} fac={r[1]} con={r[2]} obra={r[3]} lts={r[4]}")
    print(f"    desc: {r[5][:80]}")

# 3. Verify final Huixquilucan total
print("\n=== FINAL Planta Huixquilucan Semana 28 ===")
cur.execute("""
    SELECT folio_factura, folio_conciliacion, litros_facturados, punto_de_carga, fecha_factura
    FROM diesel.facturas 
    WHERE obra_destino = 'Planta Huixquilucan' AND semana = 'Semana 28'
    ORDER BY fecha_factura, folio_factura
""")
total = 0
for r in cur.fetchall():
    print(f"  {r[0]} ({r[1]}) {r[4]} → {r[2]} L | {r[3][:60]}")
    total += float(r[2])
print(f"  TOTAL: {total:.3f} L")
