import os
import xml.etree.ElementTree as ET
import PyPDF2
import re
import json

base_dir = r"c:\Users\JOSE\Desktop\Proyecto fenix\facturas\Diesel\Semana_28"
output_json = r"c:\Users\JOSE\Desktop\Proyecto fenix\temp_facturas.json"

def normalizar_destino(texto):
    if not texto: return "No aplica"
    texto = str(texto).upper()
    if "MEXICO-TOLUCA" in texto or "MÉXICO-TOLUCA" in texto or "MEXICO TOLUCA" in texto:
        return "México-Toluca"
    elif "TRES MARIAS" in texto or "TRES MARÍAS" in texto or "LERMA" in texto:
        return "Lerma - Tres Marías"
    elif "BACHEO" in texto:
        return "Bacheo Toluca"
    elif "HUIXQUILUCAN" in texto:
        return "Planta Asflato Huixquilucan"
    elif "DRAGONES" in texto:
        return "Dragones"
    elif "JALISCO" in texto:
        return "Jalisco"
    elif "PROVIDENCIA" in texto:
        return "Providencia"
    elif "PEGASO" in texto:
        if "MAQUINARIA" in texto:
            return "Maquinaria Pegaso"
        return "Planta Asfalto Pegaso"
    return "No aplica"

def parse_xml(xml_path):
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        namespaces = dict([node for _, node in ET.iterparse(xml_path, events=['start-ns'])])
        cfdi_ns = namespaces.get('cfdi', 'http://www.sat.gob.mx/cfd/4')
        if not cfdi_ns: cfdi_ns = 'http://www.sat.gob.mx/cfd/3'
        ns_map = {'cfdi': cfdi_ns}
        
        folio = root.get('Folio', '')
        fecha = root.get('Fecha', '').split('T')[0]
        
        proveedor = ""
        emisor = root.find('cfdi:Emisor', ns_map)
        if emisor is not None:
            proveedor = emisor.get('Nombre', '')
            
        total = float(root.get('Total', 0))
        subtotal = float(root.get('SubTotal', 0))
        iva = total - subtotal
        
        is_gasolina = False
        litros = 0.0
        precio = 0.0
        conceptos = root.find('cfdi:Conceptos', ns_map)
        if conceptos is not None:
            for concepto in conceptos.findall('cfdi:Concepto', ns_map):
                desc = str(concepto.get('Descripcion', '')).upper()
                if "GASOLINA" in desc or "MAGNA" in desc or "PREMIUM" in desc:
                    is_gasolina = True
                litros += float(concepto.get('Cantidad', 0))
                precio = float(concepto.get('ValorUnitario', 0))
                
        return {
            'folio': folio, 'fecha': fecha, 'proveedor': proveedor,
            'litros': litros, 'precio': precio, 'importe': subtotal,
            'iva': iva, 'total': total, 'gasolina': is_gasolina
        }
    except Exception as e:
        return None

def get_destino_from_pdf(pdf_path):
    try:
        text = ""
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return normalizar_destino(text)
    except:
        return "No aplica"

def main():
    if not os.path.exists(base_dir):
        print(f"Directory {base_dir} does not exist.")
        return
        
    archivos = os.listdir(base_dir)
    file_map = {}
    for f in archivos:
        if f.lower().endswith('.xml') or f.lower().endswith('.pdf'):
            bname = os.path.splitext(f)[0].lower()
            if bname not in file_map: file_map[bname] = {}
            if f.lower().endswith('.xml'): file_map[bname]['xml'] = f
            if f.lower().endswith('.pdf'): file_map[bname]['pdf'] = f
            
    results = []
    for bname, exts in file_map.items():
        data = None
        destino = "No aplica"
        if 'xml' in exts:
            data = parse_xml(os.path.join(base_dir, exts['xml']))
        if 'pdf' in exts:
            destino = get_destino_from_pdf(os.path.join(base_dir, exts['pdf']))
            
        if not data: continue
        if data['gasolina']: continue # Skip gasoline
        
        data['destino'] = destino
        results.append(data)
        
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
        
    print(f"Successfully extracted {len(results)} invoices to JSON.")

if __name__ == "__main__":
    main()
