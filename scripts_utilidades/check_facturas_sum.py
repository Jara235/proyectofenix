import psycopg2
import io
import re
import pdfplumber
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor()

# Get all unique invoices and sum their liters in DB
cur.execute("""
    WITH sums AS (
        SELECT folio_factura, SUM(litros_facturados) as suma_db
        FROM diesel.facturas 
        GROUP BY folio_factura
    ),
    pdfs AS (
        SELECT DISTINCT ON (folio_factura) folio_factura, archivo_pdf, proveedor
        FROM diesel.facturas
        WHERE archivo_pdf IS NOT NULL
    )
    SELECT s.folio_factura, s.suma_db, p.archivo_pdf, p.proveedor
    FROM sums s
    LEFT JOIN pdfs p ON s.folio_factura = p.folio_factura
""")
facturas_agrupadas = cur.fetchall()

print(f"Total facturas únicas: {len(facturas_agrupadas)}")

discrepancias = []

for folio_fac, suma_db, pdf_data, proveedor in facturas_agrupadas:
    suma_db = float(suma_db) if suma_db is not None else 0.0
    litros_pdf = 0.0
    
    if pdf_data:
        try:
            fname = f"temp_{folio_fac}.pdf"
            with open(fname, 'wb') as f:
                f.write(bytes(pdf_data))
            
            with pdfplumber.open(fname) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
                
                # Check for gasoline/extra/magna in the text to exclude those lines if they mix them
                # A line looks like: "200.0020 LTR Litros PL/24814... DIESEL ..."
                # Let's extract all quantities and only sum the DIESEL ones.
                lines = text.split('\n')
                for line in lines:
                    match = re.search(r'^(\d+(?:\.\d+)?)\s+LTR\s+Litros', line)
                    if match:
                        if 'DIESEL' in line.upper() or '34015' in line:
                            litros_pdf += float(match.group(1))
                        # If the invoice doesn't specify diesel/gasolina on the same line, fallback
                        elif 'GASOLINA' not in text.upper() and 'EXTRA' not in text.upper() and 'MAGNA' not in text.upper():
                            litros_pdf += float(match.group(1))

        except Exception as e:
            pass

    if litros_pdf > 0:
        diff = round(litros_pdf - suma_db, 3)
        if abs(diff) > 0.1:
            discrepancias.append({
                'folio': folio_fac,
                'db': round(suma_db, 3),
                'pdf': round(litros_pdf, 3),
                'diff': diff,
                'proveedor': proveedor
            })

print(f"\nFacturas con diferencias reales (Total factura vs Suma BD): {len(discrepancias)}")
for d in discrepancias:
    print(f"Factura {d['folio']} ({d['proveedor']}) -> BD suma: {d['db']} L | PDF total: {d['pdf']} L | Diferencia: {d['diff']} L")
