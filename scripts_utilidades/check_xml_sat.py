import psycopg2, sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

conn=psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
conn.autocommit = True
cur=conn.cursor()

# Check the UUID CFDI and XML for suspicious entries to determine product type
suspicious_cons = [
    'FA-DPC-28-117',  # TANQUE PEGASO (GASOLINA)
    'FA-DPC-28-146',  # "500 de gasolina tanque pegaso" 
    'FA-DPC-28-147',  # "1000 gasolina LHB184D" -- already obra sin asignar
    'FA-DPC-28-148',  # "gasolina PBT-12-29 Lerma"
    'FA-DPC-28-149',  # "gasolina NYZ-790-C Lerma"
]

for folio_con in suspicious_cons:
    cur.execute("""
        SELECT folio_factura, folio_conciliacion, obra_destino, litros_facturados, punto_de_carga, uuid_cfdi, archivo_xml
        FROM diesel.facturas WHERE folio_conciliacion=%s
    """, (folio_con,))
    r = cur.fetchone()
    if r:
        print(f"\n{r[1]} (fac {r[0]}) - {r[2]} - {r[3]} L")
        print(f"  desc: {r[4]}")
        print(f"  uuid: {r[5]}")
        # Try to decode XML
        xml_data = r[6]
        if xml_data:
            xml_text = bytes(xml_data).decode('utf-8', errors='ignore')
            # Find product key
            prod_match = re.findall(r'ClaveProdServ="(\d+)"', xml_text)
            desc_match = re.findall(r'Descripcion="([^"]+)"', xml_text)
            print(f"  ClaveProdServ: {prod_match}")
            print(f"  Descripcion: {desc_match[:3]}")
        else:
            print("  No XML")
