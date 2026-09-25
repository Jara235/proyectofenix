import os
import shutil
import xml.etree.ElementTree as ET

facturas_dir = r'c:\Users\JOSE\Desktop\Proyecto fenix\facturas'
gasolina_dir = os.path.join(facturas_dir, 'Gasolina')
diesel_dir = os.path.join(facturas_dir, 'Diesel')

def analyze_xml(filepath):
    is_gasolina = False
    is_diesel = False
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
        ns = {'cfdi': 'http://www.sat.gob.mx/cfd/3'}
        if 'http://www.sat.gob.mx/cfd/4' in root.tag:
            ns = {'cfdi': 'http://www.sat.gob.mx/cfd/4'}
            
        conceptos = root.find('cfdi:Conceptos', ns)
        if conceptos is not None:
            for concepto in conceptos.findall('cfdi:Concepto', ns):
                desc = concepto.attrib.get('Descripcion', '').upper()
                clave = concepto.attrib.get('ClaveProdServ', '')
                if 'DIESEL' in desc or 'DISEL' in desc or clave == '15101505':
                    is_diesel = True
                if 'GASOLINA' in desc or 'MAGNA' in desc or 'PREMIUM' in desc or clave in ('15101514', '15101515'):
                    is_gasolina = True
    except:
        pass
    return is_gasolina, is_diesel

mixed_count = 0
for root_dir, dirs, files in os.walk(facturas_dir):
    for f in files:
        if f.lower().endswith('.xml'):
            filepath = os.path.join(root_dir, f)
            g, d = analyze_xml(filepath)
            if g and d:
                mixed_count += 1
                # Figure out week from path
                week = 0
                for part in filepath.split(os.sep):
                    if part.startswith('Semana_'):
                        try:
                            week = int(part.split('_')[1])
                        except:
                            pass
                
                if week > 0:
                    gas_target = os.path.join(gasolina_dir, f"Semana_{week}")
                    dis_target = os.path.join(diesel_dir, f"Semana_{week}")
                    
                    os.makedirs(gas_target, exist_ok=True)
                    os.makedirs(dis_target, exist_ok=True)
                    
                    pdf_file = os.path.splitext(f)[0] + '.pdf'
                    pdf_path = os.path.join(root_dir, pdf_file)
                    
                    if 'Gasolina' in filepath:
                        if not os.path.exists(os.path.join(dis_target, f)):
                            shutil.copy2(filepath, os.path.join(dis_target, f))
                        if os.path.exists(pdf_path) and not os.path.exists(os.path.join(dis_target, pdf_file)):
                            shutil.copy2(pdf_path, os.path.join(dis_target, pdf_file))
                    elif 'Diesel' in filepath:
                        if not os.path.exists(os.path.join(gas_target, f)):
                            shutil.copy2(filepath, os.path.join(gas_target, f))
                        if os.path.exists(pdf_path) and not os.path.exists(os.path.join(gas_target, pdf_file)):
                            shutil.copy2(pdf_path, os.path.join(gas_target, pdf_file))

print(f"Total mixed invoices found and synchronized: {mixed_count}")
