import psycopg2
from psycopg2.extras import DictCursor
import os
import glob

def find_pdf_for_factura(folio_factura, folio_conciliacion, uuid_cfdi):
    folio_factura = str(folio_factura or '').strip()
    folio_conciliacion = str(folio_conciliacion or '').strip()
    uuid_cfdi = str(uuid_cfdi or '').strip()

    search_dirs = [
        r'c:\Users\JOSE\Desktop\Proyecto fenix\facturas',
        r'c:\Users\JOSE\Desktop\Proyecto fenix'
    ]

    # Search candidates
    patterns = []
    if folio_factura:
        patterns.append(f"*{folio_factura}*.pdf")
    if folio_conciliacion:
        patterns.append(f"*{folio_conciliacion}*.pdf")
    if uuid_cfdi:
        patterns.append(f"*{uuid_cfdi}*.pdf")

    for d in search_dirs:
        for root, dirs, files in os.walk(d):
            if any(skip in root.lower() for skip in ['node_modules', '.git', 'venv', 'antigravity']):
                continue
            for f in files:
                if not f.lower().endswith('.pdf'):
                    continue
                f_upper = f.upper()
                if folio_factura and folio_factura.upper() in f_upper:
                    return os.path.join(root, f)
                if folio_conciliacion and folio_conciliacion.upper() in f_upper:
                    return os.path.join(root, f)
                if uuid_cfdi and len(uuid_cfdi) > 5 and uuid_cfdi.upper() in f_upper:
                    return os.path.join(root, f)

    return None

def update_db_pdfs():
    conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
    cur = conn.cursor(cursor_factory=DictCursor)

    # 1. Update gasolina.facturas
    cur.execute("""
        SELECT id, folio_factura, folio_conciliacion, uuid_cfdi,
               CASE WHEN archivo_pdf IS NOT NULL THEN LENGTH(archivo_pdf) ELSE 0 END as len_pdf
        FROM gasolina.facturas
    """)
    rows = cur.fetchall()

    print(f"=== CHECKING gasolina.facturas ({len(rows)} rows) ===")
    gas_updated = 0
    for r in rows:
        r_id = r['id']
        f_fac = r['folio_factura']
        f_con = r['folio_conciliacion']
        uuid = r['uuid_cfdi']
        l_pdf = r['len_pdf']

        if l_pdf == 0:
            pdf_path = find_pdf_for_factura(f_fac, f_con, uuid)
            if pdf_path and os.path.exists(pdf_path):
                print(f"Found PDF for Gasolina ID {r_id} ({f_fac}): {pdf_path}")
                with open(pdf_path, 'rb') as fp:
                    pdf_bytes = fp.read()
                cur.execute("""
                    UPDATE gasolina.facturas
                    SET archivo_pdf = %s
                    WHERE id = %s
                """, (psycopg2.Binary(pdf_bytes), r_id))
                gas_updated += 1
            else:
                print(f"No PDF file found on disk for Gasolina ID {r_id} (Folio: {f_fac}, Conc: {f_con})")

    # 2. Update diesel.facturas
    cur.execute("""
        SELECT id, folio_factura, folio_conciliacion, uuid_cfdi,
               CASE WHEN archivo_pdf IS NOT NULL THEN LENGTH(archivo_pdf) ELSE 0 END as len_pdf
        FROM diesel.facturas
    """)
    rows_diesel = cur.fetchall()

    print(f"\n=== CHECKING diesel.facturas ({len(rows_diesel)} rows) ===")
    diesel_updated = 0
    for r in rows_diesel:
        r_id = r['id']
        f_fac = r['folio_factura']
        f_con = r['folio_conciliacion']
        uuid = r['uuid_cfdi']
        l_pdf = r['len_pdf']

        if l_pdf == 0:
            pdf_path = find_pdf_for_factura(f_fac, f_con, uuid)
            if pdf_path and os.path.exists(pdf_path):
                print(f"Found PDF for Diesel ID {r_id} ({f_fac}): {pdf_path}")
                with open(pdf_path, 'rb') as fp:
                    pdf_bytes = fp.read()
                cur.execute("""
                    UPDATE diesel.facturas
                    SET archivo_pdf = %s
                    WHERE id = %s
                """, (psycopg2.Binary(pdf_bytes), r_id))
                diesel_updated += 1

    conn.commit()
    conn.close()

    print(f"\n=== SUMMARY ===")
    print(f"Gasolina Facturas updated with PDF: {gas_updated}")
    print(f"Diesel Facturas updated with PDF: {diesel_updated}")

if __name__ == '__main__':
    update_db_pdfs()
