import os
import shutil
import xml.etree.ElementTree as ET
import PyPDF2
import re
from datetime import datetime

base_dir = r"c:\Users\JOSE\Desktop\Proyecto fenix\facturas"
sin_clasificar_dir = os.path.join(base_dir, "Sin_Clasificar")
diesel_dir = os.path.join(base_dir, "Diesel")
gasolina_dir = os.path.join(base_dir, "Gasolina")

# Helper function to get ISO week from YYYY-MM-DD
def get_semana(fecha_str):
    try:
        fecha_str = fecha_str.split('T')[0].strip()
        dt = datetime.strptime(fecha_str, "%Y-%m-%d")
        return f"Semana_{dt.isocalendar()[1]:02d}"
    except:
        return "Semana_Desconocida"
        
# Parse XML
def parse_xml_for_classification(filepath):
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
        namespaces = dict([node for _, node in ET.iterparse(filepath, events=['start-ns'])])
        cfdi_ns = namespaces.get('cfdi', 'http://www.sat.gob.mx/cfd/4')
        if not cfdi_ns: cfdi_ns = 'http://www.sat.gob.mx/cfd/3'
        ns_map = {'cfdi': cfdi_ns}
        
        fecha = root.get('Fecha', '')
        
        is_gasolina = False
        conceptos = root.find('cfdi:Conceptos', ns_map)
        if conceptos is not None:
            for concepto in conceptos.findall('cfdi:Concepto', ns_map):
                desc = str(concepto.get('Descripcion', '')).upper()
                if "GASOLINA" in desc or "MAGNA" in desc or "PREMIUM" in desc:
                    is_gasolina = True
                    break
                    
        return fecha, is_gasolina
    except:
        return "", False

# Parse PDF
def parse_pdf_for_classification(filepath):
    try:
        text = ""
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
                
        fecha = ""
        fecha_match = re.search(r'Fecha\s*[:\-]?\s*(\d{4}[-/]\d{2}[-/]\d{2})', text, re.IGNORECASE)
        if not fecha_match:
            # Try DD/MM/YYYY
            fecha_match2 = re.search(r'Fecha\s*[:\-]?\s*(\d{2}[-/]\d{2}[-/]\d{4})', text, re.IGNORECASE)
            if fecha_match2:
                # Convert DD/MM/YYYY to YYYY-MM-DD
                parts = fecha_match2.group(1).replace('-', '/').split('/')
                fecha = f"{parts[2]}-{parts[1]}-{parts[0]}"
        else:
            fecha = fecha_match.group(1).replace('/', '-')
            
        is_gasolina = False
        if "GASOLINA" in text.upper() or "MAGNA" in text.upper() or "PREMIUM" in text.upper():
            is_gasolina = True
            
        return fecha, is_gasolina
    except:
        return "", False

def process_file(folder, filename):
    filepath = os.path.join(folder, filename)
    basename, ext = os.path.splitext(filename)
    ext = ext.lower()
    
    fecha = ""
    is_gasolina = False
    
    if ext == '.xml':
        fecha, is_gasolina = parse_xml_for_classification(filepath)
    elif ext == '.pdf':
        # If it's a PDF, check if we can read the XML instead
        xml_path = os.path.join(folder, basename + ".xml")
        if os.path.exists(xml_path):
            fecha, is_gasolina = parse_xml_for_classification(xml_path)
        else:
            fecha, is_gasolina = parse_pdf_for_classification(filepath)
    else:
        return None
        
    semana = get_semana(fecha) if fecha else "Semana_Desconocida"
    target_base = gasolina_dir if is_gasolina else diesel_dir
    target_dir = os.path.join(target_base, semana)
    
    os.makedirs(target_dir, exist_ok=True)
    return os.path.join(target_dir, filename)

moved = 0
# Process root (the 8 locked ones)
for f in os.listdir(base_dir):
    src = os.path.join(base_dir, f)
    if os.path.isfile(src) and (f.lower().endswith('.xml') or f.lower().endswith('.pdf')):
        dst = process_file(base_dir, f)
        if dst:
            try:
                shutil.move(src, dst)
                moved += 1
            except: pass

# Process Sin_Clasificar
if os.path.exists(sin_clasificar_dir):
    for f in os.listdir(sin_clasificar_dir):
        src = os.path.join(sin_clasificar_dir, f)
        if os.path.isfile(src):
            dst = process_file(sin_clasificar_dir, f)
            if dst:
                try:
                    shutil.move(src, dst)
                    moved += 1
                except: pass

print(f"Clasificacion profunda completada. Se movieron {moved} archivos a sus carpetas finales.")
