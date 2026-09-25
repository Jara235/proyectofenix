import psycopg2
import io
import re
import pdfplumber
import xml.etree.ElementTree as ET
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor()

cur.execute("SELECT id, folio_factura, folio_conciliacion, litros_facturados, archivo_pdf, archivo_xml, proveedor FROM diesel.facturas")
facturas = cur.fetchall()

print(f"Total facturas a revisar: {len(facturas)}")

discrepancias = []

for fac_id, folio_fac, folio_con, litros_db, pdf_data, xml_data, proveedor in facturas:
    litros_db = float(litros_db) if litros_db is not None else 0.0
    litros_reales = 0.0
    origen_datos = "Ninguno"
    
    # Try XML first
    if xml_data:
        try:
            xml_text = bytes(xml_data).decode('utf-8', errors='ignore')
            # Very basic regex for CFDI Conceptos
            # <cfdi:Concepto ... Cantidad="200.002" ... >
            cantidades = re.findall(r'<cfdi:Concepto[^>]+Cantidad="([^"]+)"', xml_text)
            if cantidades:
                litros_reales = sum(float(c) for c in cantidades)
                origen_datos = "XML"
        except Exception as e:
            pass
            
    # If no XML or parsing failed, try PDF
    if origen_datos == "Ninguno" and pdf_data:
        try:
            # We must write it to a temporary file
            fname = f"temp_{folio_fac}.pdf"
            with open(fname, 'wb') as f:
                f.write(bytes(pdf_data))
            
            with pdfplumber.open(fname) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
                
                # Regex to find quantities. Format: "200.0020 LTR Litros" or similar
                # Just looking for lines that have LTR Litros and a number at the start
                # or finding "Cantidad" column values.
                # In the previous PDF, line was: "200.0020 LTR Litros PL/24814/EXP/ES/2023-1245392 15101505 34015 DIESEL..."
                cantidades = re.findall(r'^(\d+(?:\.\d+)?)\s+LTR\s+Litros', text, re.MULTILINE)
                if cantidades:
                    # check if the line contains DIESEL to exclude GASOLINA if mixed in same invoice?
                    # let's just parse lines that have DIESEL in them
                    diesel_lines = re.findall(r'^(\d+(?:\.\d+)?)\s+LTR\s+Litros.*?(?:DIESEL|34015)', text, re.MULTILINE | re.IGNORECASE)
                    if diesel_lines:
                        litros_reales = sum(float(c) for c in diesel_lines)
                        origen_datos = "PDF"
                    else:
                        # Maybe it's another format, fallback to all LTR Litros
                        litros_reales = sum(float(c) for c in cantidades)
                        origen_datos = "PDF (Sin DIESEL explícito)"
                else:
                    # Try another regex for J.D.J EQUIPO Y CONSTRUCCIONES or others
                    pass
        except Exception as e:
            pass

    # Compare
    # Use a small epsilon for float comparison
    if origen_datos != "Ninguno":
        diff = abs(litros_db - litros_reales)
        if diff > 0.1:
            discrepancias.append({
                'id': fac_id,
                'folio': folio_fac,
                'conciliacion': folio_con,
                'db': litros_db,
                'real': litros_reales,
                'diff': diff,
                'origen': origen_datos,
                'proveedor': proveedor
            })

print(f"\nSe encontraron {len(discrepancias)} discrepancias:")
for d in discrepancias:
    print(f"Factura {d['folio']} ({d['conciliacion']}) - {d['proveedor']}")
    print(f"  En BD: {d['db']} L | Extraído de {d['origen']}: {d['real']} L | Diferencia: {d['diff']:.3f} L")

