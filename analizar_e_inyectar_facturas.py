import os
import xml.etree.ElementTree as ET
import psycopg2
from psycopg2.extras import DictCursor
import datetime
import re

# Namespaces for CFDI XML
NAMESPACES = {
    'cfdi': 'http://www.sat.gob.mx/cfd/4',
    'cfdi33': 'http://www.sat.gob.mx/cfd/3',
    'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'
}

def parse_cfdi_xml(xml_path):
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # Handle namespaces dynamically
        ns_map = {}
        for event, elem in ET.iterparse(xml_path, events=['start-ns']):
            ns_map[elem[0]] = elem[1]

        def get_attr(elem, attr, default=''):
            if elem is None:
                return default
            return elem.attrib.get(attr, default)

        # Basic attributes
        folio = root.attrib.get('Folio', root.attrib.get('folio', ''))
        serie = root.attrib.get('Serie', root.attrib.get('serie', ''))
        fecha = root.attrib.get('Fecha', root.attrib.get('fecha', ''))
        total = root.attrib.get('Total', root.attrib.get('total', '0'))
        subtotal = root.attrib.get('SubTotal', root.attrib.get('subTotal', '0'))

        # Emisor
        emisor_name = ''
        emisor_rfc = ''
        for child in root:
            tag = child.tag.split('}')[-1]
            if tag == 'Emisor':
                emisor_name = child.attrib.get('Nombre', child.attrib.get('nombre', ''))
                emisor_rfc = child.attrib.get('Rfc', child.attrib.get('rfc', ''))

        # UUID TimbreFiscalDigital
        uuid = ''
        for elem in root.iter():
            if elem.tag.endswith('TimbreFiscalDigital'):
                uuid = elem.attrib.get('UUID', elem.attrib.get('uuid', ''))

        # Conceptos -> Litros / ClaveProdServ
        litros = 0.0
        tipo_combustible = 'GASOLINA' # default
        
        for elem in root.iter():
            if elem.tag.endswith('Concepto'):
                descripcion = elem.attrib.get('Descripcion', elem.attrib.get('descripcion', '')).upper()
                cant = float(elem.attrib.get('Cantidad', elem.attrib.get('cantidad', '0')))
                clave = elem.attrib.get('ClaveProdServ', '')

                if any(kw in descripcion for k in ['DIESEL', 'DIÉSEL'] for kw in [k]):
                    tipo_combustible = 'DIESEL'
                elif 'GASOLINA' in descripcion or 'MAGNA' in descripcion or 'PREMIUM' in descripcion:
                    tipo_combustible = 'GASOLINA'

                litros += cant

        # Format fecha (YYYY-MM-DD)
        fecha_str = str(fecha).split('T')[0] if fecha else ''

        return {
            'xml_path': xml_path,
            'folio': str(folio).strip(),
            'serie': str(serie).strip(),
            'folio_completo': f"{serie}{folio}".strip() if (serie and folio) else (str(folio).strip() or str(serie).strip()),
            'fecha': fecha_str,
            'total': float(total or 0),
            'subtotal': float(subtotal or 0),
            'emisor_nombre': emisor_name.strip(),
            'emisor_rfc': emisor_rfc.strip(),
            'uuid': uuid.strip().upper(),
            'litros': litros,
            'tipo_combustible': tipo_combustible
        }
    except Exception as e:
        print(f"Error parsing XML {xml_path}: {e}")
        return None

def analyze_and_inject():
    conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
    cur = conn.cursor(cursor_factory=DictCursor)

    # 1. Load existing UUIDs and Folios in DB to avoid any duplication
    cur.execute("SELECT uuid_cfdi, folio_factura, proveedor, fecha_factura, importe_total FROM gasolina.facturas")
    gas_db = cur.fetchall()
    gas_uuids = set(str(r['uuid_cfdi'] or '').strip().upper() for r in gas_db if r['uuid_cfdi'])
    gas_folios = set(str(r['folio_factura'] or '').strip().upper() for r in gas_db if r['folio_factura'])

    cur.execute("SELECT uuid_cfdi, folio_factura, proveedor, fecha_factura, importe_total FROM diesel.facturas")
    die_db = cur.fetchall()
    die_uuids = set(str(r['uuid_cfdi'] or '').strip().upper() for r in die_db if r['uuid_cfdi'])
    die_folios = set(str(r['folio_factura'] or '').strip().upper() for r in die_db if r['folio_factura'])

    print("=== CURRENT DATABASE STATS ===")
    print(f"Gasolina Facturas in DB: {len(gas_db)} | Unique UUIDs: {len(gas_uuids)} | Unique Folios: {len(gas_folios)}")
    print(f"Diesel Facturas in DB:   {len(die_db)} | Unique UUIDs: {len(die_uuids)} | Unique Folios: {len(die_folios)}")

    # 2. Scan facturas folder
    facturas_dir = r'c:\Users\JOSE\Desktop\Proyecto fenix\facturas'
    all_xml_files = []
    for root, dirs, files in os.walk(facturas_dir):
        if any(sk in root.lower() for sk in ['node_modules', '.git', 'venv', 'antigravity']):
            continue
        for f in files:
            if f.lower().endswith('.xml'):
                all_xml_files.append(os.path.join(root, f))

    print(f"\nTotal XML files found in '{facturas_dir}': {len(all_xml_files)}")

    # 3. Parse XMLs and check status
    gas_to_insert = []
    die_to_insert = []
    skipped_duplicates = 0

    for xml_p in all_xml_files:
        parsed = parse_cfdi_xml(xml_p)
        if not parsed:
            continue

        uuid = parsed['uuid']
        folio = parsed['folio'] or parsed['folio_completo']
        tipo = parsed['tipo_combustible']

        # Find matching PDF file on disk
        pdf_path = xml_p.rsplit('.', 1)[0] + '.pdf'
        if not os.path.exists(pdf_path):
            # Try searching in same folder
            pdf_path = None
            dir_name = os.path.dirname(xml_p)
            for f in os.listdir(dir_name):
                if f.lower().endswith('.pdf'):
                    if (folio and folio.upper() in f.upper()) or (uuid and uuid.upper() in f.upper()):
                        pdf_path = os.path.join(dir_name, f)
                        break

        # Check if UUID or Folio exists in DB
        is_gas_dup = (uuid and uuid in gas_uuids) or (folio and folio.upper() in gas_folios)
        is_die_dup = (uuid and uuid in die_uuids) or (folio and folio.upper() in die_folios)

        if is_gas_dup or is_die_dup:
            skipped_duplicates += 1
            continue

        # Prepare insertion item
        item = {
            'parsed': parsed,
            'pdf_path': pdf_path,
            'xml_path': xml_p
        }

        if tipo == 'GASOLINA':
            gas_to_insert.append(item)
            if uuid: gas_uuids.add(uuid)
            if folio: gas_folios.add(folio.upper())
        else:
            die_to_insert.append(item)
            if uuid: die_uuids.add(uuid)
            if folio: die_folios.add(folio.upper())

    print(f"\n=== ANALYSIS RESULTS ===")
    print(f"Skipped Duplicates (Already in DB): {skipped_duplicates}")
    print(f"New Gasoline Invoices to Inject:    {len(gas_to_insert)}")
    print(f"New Diesel Invoices to Inject:      {len(die_to_insert)}")

    if gas_to_insert:
        print("\n--- SAMPLE NEW GASOLINE INVOICES ---")
        for g in gas_to_insert[:10]:
            p = g['parsed']
            print(f"Folio: {p['folio_completo']:12s} | Fecha: {p['fecha']} | Emisor: {p['emisor_nombre'][:30]:30s} | Total: ${p['total']:,.2f} | Litros: {p['litros']:.2f}")

    if die_to_insert:
        print("\n--- SAMPLE NEW DIESEL INVOICES ---")
        for d in die_to_insert[:10]:
            p = d['parsed']
            print(f"Folio: {p['folio_completo']:12s} | Fecha: {p['fecha']} | Emisor: {p['emisor_nombre'][:30]:30s} | Total: ${p['total']:,.2f} | Litros: {p['litros']:.2f}")

    # 4. Inject into DB
    inserted_gas_count = 0
    for item in gas_to_insert:
        p = item['parsed']
        xml_p = item['xml_path']
        pdf_p = item['pdf_path']

        # Read binary files
        xml_bytes = None
        if os.path.exists(xml_p):
            with open(xml_p, 'rb') as f:
                xml_bytes = f.read()

        pdf_bytes = None
        if pdf_p and os.path.exists(pdf_p):
            with open(pdf_p, 'rb') as f:
                pdf_bytes = f.read()

        folio_str = p['folio_completo'] or p['folio'] or p['uuid'][:10]
        conciliacion = f"FAC-GAS-{folio_str}"

        cur.execute("""
            INSERT INTO gasolina.facturas (
                folio_conciliacion, folio_factura, fecha_factura, semana, proveedor,
                litros_facturados, importe_total, uuid_cfdi,
                archivo_pdf, archivo_xml, estatus_revision
            ) VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s
            )
        """, (
            conciliacion, folio_str, p['fecha'], '30', p['emisor_nombre'],
            p['litros'], p['total'], p['uuid'],
            psycopg2.Binary(pdf_bytes) if pdf_bytes else None,
            psycopg2.Binary(xml_bytes) if xml_bytes else None,
            'PENDIENTE'
        ))
        inserted_gas_count += 1

    inserted_die_count = 0
    for item in die_to_insert:
        p = item['parsed']
        xml_p = item['xml_path']
        pdf_p = item['pdf_path']

        xml_bytes = None
        if os.path.exists(xml_p):
            with open(xml_p, 'rb') as f:
                xml_bytes = f.read()

        pdf_bytes = None
        if pdf_p and os.path.exists(pdf_p):
            with open(pdf_p, 'rb') as f:
                pdf_bytes = f.read()

        folio_str = p['folio_completo'] or p['folio'] or p['uuid'][:10]
        conciliacion = f"FAC-DIE-{folio_str}"

        cur.execute("""
            INSERT INTO diesel.facturas (
                folio_conciliacion, folio_factura, fecha_factura, semana, proveedor,
                litros_facturados, importe_total, uuid_cfdi,
                archivo_pdf, archivo_xml, estatus_revision
            ) VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s
            )
        """, (
            conciliacion, folio_str, p['fecha'], '30', p['emisor_nombre'],
            p['litros'], p['total'], p['uuid'],
            psycopg2.Binary(pdf_bytes) if pdf_bytes else None,
            psycopg2.Binary(xml_bytes) if xml_bytes else None,
            'PENDIENTE'
        ))
        inserted_die_count += 1

    conn.commit()
    conn.close()

    print(f"\n=== INJECTION COMPLETED SUCCESSFULLY ===")
    print(f"Gasoline Invoices Injected: {inserted_gas_count}")
    print(f"Diesel Invoices Injected:   {inserted_die_count}")

if __name__ == '__main__':
    analyze_and_inject()
