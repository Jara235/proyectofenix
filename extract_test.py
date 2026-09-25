import re, json
import pdfplumber
import xml.etree.ElementTree as ET

def extract_factura(pdf_path, xml_path):
    res = {'cargas': [], 'obra_texto': ''}
    # Parse PDF
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = pdf.pages[0].extract_text()
            match = re.search(r'Fecha de Vencimiento:\s*\S+\s+(.*)', text, re.IGNORECASE)
            if match:
                res['obra_texto'] = match.group(1).strip()
    except: pass
    
    # Parse XML
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        ns = {'cfdi': 'http://www.sat.gob.mx/cfd/4', 'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'}
        
        res['fecha'] = root.get('Fecha', '').split('T')[0]
        timbre = root.find('.//tfd:TimbreFiscalDigital', ns)
        res['uuid'] = timbre.get('UUID', '') if timbre is not None else ''
        
        for c in root.findall('.//cfdi:Concepto', ns):
            desc = c.get('Descripcion', '').lower()
            clave = c.get('ClaveProdServ', '')
            if 'diesel' in desc or 'disel' in desc or clave == '15101505':
                litros = float(c.get('Cantidad', 0))
                precio = float(c.get('ValorUnitario', 0))
                subtotal = float(c.get('Importe', 0))
                iva = 0
                for imp in c.findall('.//cfdi:Traslado', ns):
                    if imp.get('Impuesto') == '002':
                        iva += float(imp.get('Importe', 0))
                res['cargas'].append({
                    'descripcion': c.get('Descripcion'),
                    'litros': litros,
                    'precio': precio,
                    'subtotal': subtotal,
                    'iva': iva,
                    'total': subtotal + iva
                })
    except Exception as e: print(e)
    return res

print(json.dumps(extract_factura('c:/Users/JOSE/Desktop/Proyecto fenix/facturas/Diesel/Semana_25/2c6f01d9-fdba-4376-8cef-ed0d989e49df.pdf', 'c:/Users/JOSE/Desktop/Proyecto fenix/facturas/Diesel/Semana_25/2c6f01d9-fdba-4376-8cef-ed0d989e49df.xml'), indent=2))

