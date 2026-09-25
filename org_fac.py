import zipfile
import os
import shutil
import xml.etree.ElementTree as ET
from datetime import datetime

facturas_dir = r'c:\Users\JOSE\Desktop\Proyecto fenix\facturas'
extracted_dir = os.path.join(facturas_dir, 'extracted_tmp')
gasolina_dir = os.path.join(facturas_dir, 'Gasolina')
diesel_dir = os.path.join(facturas_dir, 'Diesel')

if not os.path.exists(extracted_dir):
    os.makedirs(extracted_dir)
if not os.path.exists(gasolina_dir):
    os.makedirs(gasolina_dir)
if not os.path.exists(diesel_dir):
    os.makedirs(diesel_dir)

# 1. Extract ZIP files
zips = [f for f in os.listdir(facturas_dir) if f.endswith('.zip')]
for z in zips:
    zip_path = os.path.join(facturas_dir, z)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extracted_dir)

# 2. Find all XML and PDF files
files = []
for root, dirs, filenames in os.walk(extracted_dir):
    for f in filenames:
        files.append(os.path.join(root, f))

xmls = [f for f in files if f.lower().endswith('.xml')]

gasolina_count = 0
diesel_count = 0
unknown_count = 0

for xml_path in xmls:
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # Determine namespaces (CFDI 3.3 or 4.0)
        ns = {'cfdi': 'http://www.sat.gob.mx/cfd/3'}
        if 'http://www.sat.gob.mx/cfd/4' in root.tag:
            ns = {'cfdi': 'http://www.sat.gob.mx/cfd/4'}
        
        # Get date
        fecha_str = root.attrib.get('Fecha', '')
        week = 0
        if fecha_str:
            # Parse '2026-06-25T14:32:00'
            date_obj = datetime.strptime(fecha_str.split('T')[0], '%Y-%m-%d')
            week = date_obj.isocalendar()[1]
        
        # Determine product type
        is_gasolina = False
        is_diesel = False
        
        conceptos = root.find('cfdi:Conceptos', ns)
        if conceptos is not None:
            for concepto in conceptos.findall('cfdi:Concepto', ns):
                desc = concepto.attrib.get('Descripcion', '').upper()
                clave = concepto.attrib.get('ClaveProdServ', '')
                
                if 'DIESEL' in desc or 'DISEL' in desc or clave == '15101505':
                    is_diesel = True
                if 'GASOLINA' in desc or 'MAGNA' in desc or 'PREMIUM' in desc or clave in ('15101514', '15101515'):
                    is_gasolina = True
        
        # Move files
        base_name = os.path.splitext(xml_path)[0]
        pdf_path = base_name + '.pdf'
        
        if is_gasolina:
            target_folder = os.path.join(gasolina_dir, f"Semana_{week}")
            os.makedirs(target_folder, exist_ok=True)
            gasolina_count += 1
            shutil.copy2(xml_path, os.path.join(target_folder, os.path.basename(xml_path)))
            if os.path.exists(pdf_path):
                shutil.copy2(pdf_path, os.path.join(target_folder, os.path.basename(pdf_path)))
        elif is_diesel:
            target_folder = os.path.join(diesel_dir, f"Semana_{week}")
            os.makedirs(target_folder, exist_ok=True)
            diesel_count += 1
            shutil.copy2(xml_path, os.path.join(target_folder, os.path.basename(xml_path)))
            if os.path.exists(pdf_path):
                shutil.copy2(pdf_path, os.path.join(target_folder, os.path.basename(pdf_path)))
        else:
            unknown_count += 1
            
    except Exception as e:
        print(f"Error parsing {xml_path}: {e}")

# Cleanup
shutil.rmtree(extracted_dir)

print(f"Extraction and classification complete.")
print(f"Gasolina invoices found: {gasolina_count}")
print(f"Diesel invoices found: {diesel_count}")
print(f"Unknown invoices: {unknown_count}")
