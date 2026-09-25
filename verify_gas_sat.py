import psycopg2, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

conn=psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
conn.autocommit = True
cur=conn.cursor()

# Save PDFs of all suspicious "gasolina" entries to verify SAT code
# Focus on the ones that explicitly say "gasolina" in description
suspicious = [
    ('10386', 'FA-DPC-28-117'),  # "TANQUE PEGASO (GASOLINA)"
    ('10905', 'FA-DPC-28-146'),  # "500 de gasolina tanque pegaso"
    ('10906', 'FA-DPC-28-147'),  # "1000 gasolina LHB184D"
    ('10903', 'FA-DPC-28-144'),  # "SUMINISTRO DE $800 ... [OBRA: Planta Pegaso]" - 27 lts suspicious
]

import pdfplumber
for folio_fac, folio_con in suspicious:
    cur.execute("SELECT archivo_pdf, litros_facturados FROM diesel.facturas WHERE folio_factura=%s AND folio_conciliacion=%s", (folio_fac, folio_con))
    row = cur.fetchone()
    if row and row[0]:
        fname = f'check_{folio_fac}.pdf'
        with open(fname, 'wb') as f:
            f.write(bytes(row[0]))
        try:
            with pdfplumber.open(fname) as pdf:
                text = pdf.pages[0].extract_text()[:600]
                # Look for SAT code
                import re
                sat_match = re.search(r'\b(15101514|15101505|32025|34015)\b', text)
                prod_match = re.search(r'(DIESEL|EXTRA|MAGNA|gasolina)', text, re.IGNORECASE)
                print(f"\n=== {folio_fac} ({folio_con}) - {row[1]} L ===")
                print(f"  SAT Code: {sat_match.group() if sat_match else 'NOT FOUND'}")
                print(f"  Product: {prod_match.group() if prod_match else 'NOT FOUND'}")
                # Show relevant lines
                for line in text.split('\n'):
                    if any(kw in line.upper() for kw in ['DIESEL','EXTRA','MAGNA','SAT','LITROS','LTR','34015','32025']):
                        print(f"  > {line.strip()}")
        except Exception as e:
            print(f"  PDF error: {e}")

# Final: verify Huixquilucan after removing 10407
print("\n=== FINAL Planta Huixquilucan Semana 28 ===")
cur.execute("""
    SELECT folio_factura, folio_conciliacion, litros_facturados, fecha_factura
    FROM diesel.facturas 
    WHERE obra_destino = 'Planta Huixquilucan' AND semana = 'Semana 28'
    ORDER BY fecha_factura, folio_factura
""")
total = 0
for r in cur.fetchall():
    print(f"  {r[0]} ({r[1]}) {r[3]} -> {r[2]} L")
    total += float(r[2])
print(f"  TOTAL: {total:.3f} L")
