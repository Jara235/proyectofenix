import psycopg2
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor()

print("=== CHECKING INVOICE 10383 (DB SUM < PDF) ===")
cur.execute("SELECT id, folio_conciliacion, obra_destino, litros_facturados, punto_de_carga FROM diesel.facturas WHERE folio_factura = '10383'")
rows = cur.fetchall()
for r in rows:
    print(r)

print("\n=== CHECKING INVOICE 10331 (DB SUM > PDF) ===")
cur.execute("SELECT id, folio_conciliacion, obra_destino, litros_facturados, punto_de_carga FROM diesel.facturas WHERE folio_factura = '10331' ORDER BY id")
rows = cur.fetchall()
for r in rows:
    print(r)
    
print("\n=== CHECKING INVOICE 10298 (DB SUM > PDF) ===")
cur.execute("SELECT id, folio_conciliacion, obra_destino, litros_facturados, punto_de_carga FROM diesel.facturas WHERE folio_factura = '10298' ORDER BY id")
rows = cur.fetchall()
for r in rows:
    print(r)
