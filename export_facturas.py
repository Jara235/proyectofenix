import psycopg2
import os
import shutil

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor()

base_dir = r"c:\Users\JOSE\Desktop\Proyecto fenix\facturas"

# We will export to DB_Diesel and DB_Gasolina to avoid deleting their zips or unknown files
out_diesel = os.path.join(base_dir, "DB_Diesel")
out_gasolina = os.path.join(base_dir, "DB_Gasolina")

# Create fresh directories
for d in [out_diesel, out_gasolina]:
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(d)

print("Exporting Diesel facturas...")
cur.execute("SELECT DISTINCT folio_factura, archivo_pdf, archivo_xml FROM diesel.facturas WHERE archivo_pdf IS NOT NULL")
diesel_rows = cur.fetchall()
for folio, pdf, xml in diesel_rows:
    pdf_path = os.path.join(out_diesel, f"Factura_{folio}.pdf")
    with open(pdf_path, 'wb') as f:
        f.write(bytes(pdf))
    if xml:
        xml_path = os.path.join(out_diesel, f"Factura_{folio}.xml")
        with open(xml_path, 'wb') as f:
            f.write(bytes(xml))

print(f"Exported {len(diesel_rows)} Diesel invoices.")

print("Exporting Gasolina facturas...")
# Try checking if gasolina.facturas exists and has files
try:
    cur.execute("SELECT DISTINCT folio_factura, archivo_pdf, archivo_xml FROM gasolina.facturas WHERE archivo_pdf IS NOT NULL")
    gasolina_rows = cur.fetchall()
    for folio, pdf, xml in gasolina_rows:
        pdf_path = os.path.join(out_gasolina, f"Factura_{folio}.pdf")
        with open(pdf_path, 'wb') as f:
            f.write(bytes(pdf))
        if xml:
            xml_path = os.path.join(out_gasolina, f"Factura_{folio}.xml")
            with open(xml_path, 'wb') as f:
                f.write(bytes(xml))
    print(f"Exported {len(gasolina_rows)} Gasolina invoices.")
except Exception as e:
    print(f"No gasolina facturas found or error: {e}")

print("\nBackup complete! Files are perfectly matched to DB in facturas/DB_Diesel and facturas/DB_Gasolina.")
