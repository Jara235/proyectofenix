import os
import re
import pandas as pd
import xml.etree.ElementTree as ET
import PyPDF2

folder_path = r"c:\Users\JOSE\Desktop\Proyecto fenix\facturas"
excel_path = r"c:\Users\JOSE\Desktop\Proyecto fenix\FACTURAS_EXTRAIDAS_REVISION.xlsx"

# Find files related to 10246
xml_file = None
pdf_file = None

for f in os.listdir(folder_path):
    if '10246' in f:
        if f.lower().endswith('.xml'):
            xml_file = os.path.join(folder_path, f)
        elif f.lower().endswith('.pdf'):
            pdf_file = os.path.join(folder_path, f)

if not xml_file and not pdf_file:
    print("No se encontro la factura 10246 (ni XML ni PDF)")
    exit(1)

# Extract data
data = {
    'ARCHIVO_ORIGEN': os.path.basename(xml_file) if xml_file else os.path.basename(pdf_file),
    'FOLIO_FACTURA': '10246',
    'FECHA_FACTURA': '',
    'PROVEEDOR': 'Desconocido',
    'DESCRIPCION_SAT': '',
    'TIPO_COMBUSTIBLE': 'Desconocido',
    'LITROS_FACTURADOS': 0.0,
    'PRECIO_UNITARIO': 0.0,
    'IMPORTE_TOTAL': 0.0,
    'DESTINO_REPORTADO_PDF': ''
}

# Parse XML if available
if xml_file:
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        namespaces = dict([node for _, node in ET.iterparse(xml_file, events=['start-ns'])])
        cfdi_ns = namespaces.get('cfdi', 'http://www.sat.gob.mx/cfd/4')
        ns_map = {'cfdi': cfdi_ns}

        data['FOLIO_FACTURA'] = root.get('Folio', '10246')
        data['FECHA_FACTURA'] = root.get('Fecha', '').split('T')[0]
        
        emisor = root.find('cfdi:Emisor', ns_map)
        if emisor is not None:
            data['PROVEEDOR'] = emisor.get('Nombre', 'Desconocido')
            
        conceptos = root.find('cfdi:Conceptos', ns_map)
        if conceptos is not None:
            concepto = conceptos.find('cfdi:Concepto', ns_map)
            if concepto is not None:
                desc = concepto.get('Descripcion', '').upper()
                data['DESCRIPCION_SAT'] = desc
                if "DIESEL" in desc or "DIÉSEL" in desc:
                    data['TIPO_COMBUSTIBLE'] = "Diésel"
                elif "GASOLINA" in desc or "MAGNA" in desc:
                    data['TIPO_COMBUSTIBLE'] = "Gasolina"
                    
                data['LITROS_FACTURADOS'] = float(concepto.get('Cantidad', 0))
                data['PRECIO_UNITARIO'] = float(concepto.get('ValorUnitario', 0))
                data['IMPORTE_TOTAL'] = float(concepto.get('Importe', 0))
    except Exception as e:
        print(f"Error parsing XML: {e}")

# Parse PDF for Destination (or fallback data)
if pdf_file:
    try:
        text = ""
        with open(pdf_file, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
                
        # Extract destination
        match = re.search(r'Fecha de Vencimiento\s*:\s*\d{2}[-/]\d{2}[-/]\d{2,4}\s*(.+)', text, re.IGNORECASE)
        if match:
            data['DESTINO_REPORTADO_PDF'] = match.group(1).strip()
        else:
            match2 = re.search(r'Vencimiento.*?\d{4}\s+([A-Za-z].+)', text, re.IGNORECASE)
            if match2:
                data['DESTINO_REPORTADO_PDF'] = match2.group(1).strip()
                
        # Fallback if no XML
        if not xml_file:
            folio_match = re.search(r'Folio\s*[:\-]\s*([A-Za-z0-9]+)', text, re.IGNORECASE)
            if folio_match: data['FOLIO_FACTURA'] = folio_match.group(1)
            
            fecha_match = re.search(r'Fecha\s*[:\-]?\s*(\d{2,4}[-/]\d{2}[-/]\d{2,4})', text, re.IGNORECASE)
            if fecha_match: data['FECHA_FACTURA'] = fecha_match.group(1)
            
            total_match = re.search(r'Total\s*[:\$]?\s*(\d+[,.]\d{2})', text, re.IGNORECASE)
            if total_match: data['IMPORTE_TOTAL'] = float(total_match.group(1).replace(',', ''))
            
            litros_match = re.search(r'(\d+[,.]\d{2,4})\s*(LTR|Lts|Litros)', text, re.IGNORECASE)
            if litros_match: data['LITROS_FACTURADOS'] = float(litros_match.group(1).replace(',', ''))
            
            if "DIESEL" in text.upper(): data['TIPO_COMBUSTIBLE'] = "Diésel (PDF)"
            elif "GASOLINA" in text.upper(): data['TIPO_COMBUSTIBLE'] = "Gasolina (PDF)"
            
    except Exception as e:
        print(f"Error parsing PDF: {e}")

# Append to Excel
try:
    df = pd.read_excel(excel_path)
    new_df = pd.DataFrame([data])
    combined_df = pd.concat([df, new_df], ignore_index=True)
    combined_df.to_excel(excel_path, index=False)
    print(f"Exito. Factura 10246 agregada con {data['LITROS_FACTURADOS']} Lts. Destino: {data['DESTINO_REPORTADO_PDF']}")
except Exception as e:
    print(f"Error saving to Excel: {e}")
