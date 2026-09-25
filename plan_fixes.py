import psycopg2
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor()

# Get the list of discrepancies calculated earlier
import json
import pdfplumber
import re

cur.execute("""
    WITH sums AS (
        SELECT folio_factura, SUM(litros_facturados) as suma_db
        FROM diesel.facturas 
        GROUP BY folio_factura
    ),
    pdfs AS (
        SELECT DISTINCT ON (folio_factura) folio_factura, archivo_pdf
        FROM diesel.facturas
        WHERE archivo_pdf IS NOT NULL
    )
    SELECT s.folio_factura, s.suma_db, p.archivo_pdf
    FROM sums s
    LEFT JOIN pdfs p ON s.folio_factura = p.folio_factura
""")
facturas = cur.fetchall()

to_delete = []
to_update = []

for folio, suma_db, pdf_data in facturas:
    if not pdf_data: continue
    
    # Extract real PDF liters
    litros_pdf = 0.0
    fname = f"temp_{folio}.pdf"
    with open(fname, 'wb') as f:
        f.write(bytes(pdf_data))
    
    with pdfplumber.open(fname) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
        for line in text.split('\n'):
            match = re.search(r'^(\d+(?:\.\d+)?)\s+LTR\s+Litros', line)
            if match:
                if 'DIESEL' in line.upper() or '34015' in line:
                    litros_pdf += float(match.group(1))
                elif 'GASOLINA' not in text.upper() and 'EXTRA' not in text.upper() and 'MAGNA' not in text.upper():
                    litros_pdf += float(match.group(1))

    suma_db = float(suma_db)
    if litros_pdf > 0:
        diff = round(litros_pdf - suma_db, 3)
        if abs(diff) > 0.1:
            # We have a discrepancy
            if diff < 0:
                # DB has MORE than PDF (Likely duplicates)
                cur.execute("SELECT id, litros_facturados, folio_conciliacion FROM diesel.facturas WHERE folio_factura = %s ORDER BY id", (folio,))
                rows = cur.fetchall()
                # Find duplicates based on liters sequence. e.g. [280, 300, 280, 300]
                # If we just keep the first N rows that sum up to exactly PDF total
                current_sum = 0
                keep_ids = []
                del_ids = []
                for r_id, lts, fol_con in rows:
                    if current_sum + float(lts) <= litros_pdf + 0.1:
                        keep_ids.append(r_id)
                        current_sum += float(lts)
                    else:
                        del_ids.append(r_id)
                
                if abs(current_sum - litros_pdf) < 0.1:
                    to_delete.extend(del_ids)
                    print(f"[{folio}] RESOLVED DUP: Keep {len(keep_ids)} rows, Delete {len(del_ids)} rows. Sum matches PDF {litros_pdf} L.")
                else:
                    print(f"[{folio}] WARNING: Cannot easily resolve duplicate logic. Sum of kept is {current_sum}, target is {litros_pdf}")
                    
            elif diff > 0:
                # DB has LESS than PDF. We need to add liters.
                # If there's only 1 row, easy: update it.
                cur.execute("SELECT id, litros_facturados, folio_conciliacion FROM diesel.facturas WHERE folio_factura = %s", (folio,))
                rows = cur.fetchall()
                if len(rows) == 1:
                    to_update.append((rows[0][0], round(litros_pdf, 3), folio))
                    print(f"[{folio}] RESOLVED MISSING: Update row {rows[0][0]} from {rows[0][1]} L to {litros_pdf} L.")
                else:
                    print(f"[{folio}] WARNING: Has missing liters but multiple rows. DB sum: {suma_db}, PDF: {litros_pdf}")

print("\n--- PLAN SUMMARY ---")
print(f"Rows to DELETE: {len(to_delete)}")
print(f"Rows to UPDATE: {len(to_update)}")

import json
with open('plan.json', 'w') as f:
    json.dump({'delete': to_delete, 'update': to_update}, f)

