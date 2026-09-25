import os
import xml.etree.ElementTree as ET
from datetime import datetime

facturas_dir = r'c:\Users\JOSE\Desktop\Proyecto fenix\facturas'

uuids = {}

# 1. Collect all XMLs
for root_dir, dirs, files in os.walk(facturas_dir):
    for f in files:
        if f.lower().endswith('.xml'):
            filepath = os.path.join(root_dir, f)
            try:
                tree = ET.parse(filepath)
                root = tree.getroot()
                
                uuid = None
                for elem in root.iter():
                    if 'TimbreFiscalDigital' in elem.tag:
                        uuid = elem.attrib.get('UUID')
                        break
                        
                if uuid:
                    if uuid not in uuids:
                        uuids[uuid] = []
                    uuids[uuid].append(filepath)
            except:
                pass

# 2. Determine correct placement and delete duplicates
deleted_xmls = 0
deleted_pdfs = 0

for uuid, paths in uuids.items():
    if len(paths) > 1:
        # Determine the "best" path. 
        # Parse the first file to see what it is and what week it belongs to.
        tree = ET.parse(paths[0])
        root = tree.getroot()
        
        ns = {'cfdi': 'http://www.sat.gob.mx/cfd/3'}
        if 'http://www.sat.gob.mx/cfd/4' in root.tag:
            ns = {'cfdi': 'http://www.sat.gob.mx/cfd/4'}
            
        fecha_str = root.attrib.get('Fecha', '')
        week = 0
        if fecha_str:
            date_obj = datetime.strptime(fecha_str.split('T')[0], '%Y-%m-%d')
            week = date_obj.isocalendar()[1]
            
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
                    
        correct_folder_type = 'Gasolina' if is_gasolina else 'Diesel'
        expected_folder_substring = os.path.join(correct_folder_type, f"Semana_{week}")
        
        # Select the best path to keep
        best_path = None
        for p in paths:
            if expected_folder_substring in p:
                best_path = p
                break
        
        if not best_path:
            # Fallback to the first one that has correct type
            for p in paths:
                if correct_folder_type in p:
                    best_path = p
                    break
                    
        if not best_path:
            best_path = paths[0]
            
        # Delete all others
        for p in paths:
            if p != best_path:
                print(f"Deleting duplicate: {p}")
                os.remove(p)
                deleted_xmls += 1
                
                pdf_path = os.path.splitext(p)[0] + '.pdf'
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
                    deleted_pdfs += 1

print(f"Deleted {deleted_xmls} duplicate XMLs and {deleted_pdfs} duplicate PDFs.")
