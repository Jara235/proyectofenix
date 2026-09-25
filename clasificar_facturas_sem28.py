import os
import shutil
import xml.etree.ElementTree as ET
import pandas as pd
import re
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side, numbers
from datetime import datetime

SOURCE_DIR = r"c:\Users\JOSE\Desktop\Proyecto fenix\facturas\carpeta28_temp\CARPERTA 28"
FACTURAS_DIR = r"c:\Users\JOSE\Desktop\Proyecto fenix\facturas"
MAESTRO_PATH = r"c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_DIESEL_NUEVO.xlsx"

SEMANA_MAP = {
    # Semana 27: Lunes 30 Jun - Domingo 06 Jul
    "2026-06-30": "Semana 27", "2026-07-01": "Semana 27", "2026-07-02": "Semana 27",
    "2026-07-03": "Semana 27", "2026-07-04": "Semana 27", "2026-07-05": "Semana 27", "2026-07-06": "Semana 27",
    # Semana 28: Lunes 07 Jul - Domingo 12 Jul
    "2026-07-07": "Semana 28", "2026-07-08": "Semana 28", "2026-07-09": "Semana 28",
    "2026-07-10": "Semana 28", "2026-07-11": "Semana 28", "2026-07-12": "Semana 28",
    # Semana 29: Lunes 13 Jul - Domingo 19 Jul
    "2026-07-13": "Semana 29", "2026-07-14": "Semana 29", "2026-07-15": "Semana 29",
    "2026-07-16": "Semana 29", "2026-07-17": "Semana 29", "2026-07-18": "Semana 29", "2026-07-19": "Semana 29",
    # Semana 30: Lunes 20 Jul - Domingo 26 Jul
    "2026-07-20": "Semana 30", "2026-07-21": "Semana 30", "2026-07-22": "Semana 30",
    "2026-07-23": "Semana 30", "2026-07-24": "Semana 30", "2026-07-25": "Semana 30", "2026-07-26": "Semana 30",
    # Semana 31: Lunes 27 Jul - Domingo 02 Ago
    "2026-07-27": "Semana 31", "2026-07-28": "Semana 31", "2026-07-29": "Semana 31",
    "2026-07-30": "Semana 31", "2026-07-31": "Semana 31", "2026-08-01": "Semana 31", "2026-08-02": "Semana 31",
}


def detectar_tipo_y_datos(xml_path):
    """Lee un XML CFDI y extrae tipo de combustible y datos clave."""
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        ns = {
            'cfdi': 'http://www.sat.gob.mx/cfd/4',
            'cfdi3': 'http://www.sat.gob.mx/cfd/3',
        }
        
        # Intentar encontrar el namespace del archivo
        tag = root.tag
        if 'cfd/4' in tag:
            ns_key = 'cfdi'
        elif 'cfd/3' in tag:
            ns_key = 'cfdi3'
        else:
            ns_key = 'cfdi'
        
        # Buscar en toda la raiz con findall recursivo
        all_text = ET.tostring(root, encoding='unicode')
        
        tipo = 'diesel'  # default por ser DPC (Distribuidora de Petróleo Castilla)
        # Detectar palabras clave en el XML
        if re.search(r'gasolina|magna|premium|gasolinas', all_text, re.IGNORECASE):
            tipo = 'gasolina'
        elif re.search(r'diesel|gasóleo|gasoil', all_text, re.IGNORECASE):
            tipo = 'diesel'
        
        # Extraer datos del comprobante
        datos = {
            'tipo': tipo,
            'uuid': '',
            'fecha': '',
            'semana': '',
            'emisor_rfc': '',
            'emisor_nombre': '',
            'receptor_rfc': '',
            'receptor_nombre': '',
            'descripcion': '',
            'cantidad': 0,
            'unidad': '',
            'precio_unitario': 0,
            'importe': 0,
            'subtotal': 0,
            'iva': 0,
            'total': 0,
            'folio': '',
            'serie': '',
        }
        
        # Atributos del comprobante raíz
        datos['total'] = float(root.get('Total', 0))
        datos['subtotal'] = float(root.get('SubTotal', 0))
        datos['fecha'] = root.get('Fecha', '')[:10]
        datos['folio'] = root.get('Folio', '')
        datos['serie'] = root.get('Serie', '')
        
        # Semana
        fecha_corta = datos['fecha']
        datos['semana'] = SEMANA_MAP.get(fecha_corta, 'Semana 28')
        
        # Emisor
        emisor = root.find('.//{http://www.sat.gob.mx/cfd/4}Emisor') or root.find('.//{http://www.sat.gob.mx/cfd/3}Emisor')
        if emisor is not None:
            datos['emisor_rfc'] = emisor.get('Rfc', '')
            datos['emisor_nombre'] = emisor.get('Nombre', '')
        
        # Receptor
        receptor = root.find('.//{http://www.sat.gob.mx/cfd/4}Receptor') or root.find('.//{http://www.sat.gob.mx/cfd/3}Receptor')
        if receptor is not None:
            datos['receptor_rfc'] = receptor.get('Rfc', '')
            datos['receptor_nombre'] = receptor.get('Nombre', '')
        
        # Concepto
        concepto = root.find('.//{http://www.sat.gob.mx/cfd/4}Concepto') or root.find('.//{http://www.sat.gob.mx/cfd/3}Concepto')
        if concepto is not None:
            datos['descripcion'] = concepto.get('Descripcion', '')
            datos['cantidad'] = float(concepto.get('Cantidad', 0))
            datos['unidad'] = concepto.get('Unidad', '')
            datos['precio_unitario'] = float(concepto.get('ValorUnitario', 0))
            datos['importe'] = float(concepto.get('Importe', 0))
            
            # Re-detectar tipo por descripcion del concepto
            desc = datos['descripcion'].upper()
            if 'GASOLINA' in desc or 'MAGNA' in desc or 'PREMIUM' in desc:
                datos['tipo'] = 'gasolina'
            elif 'DIESEL' in desc or 'GASÓLEO' in desc:
                datos['tipo'] = 'diesel'
        
        # IVA
        traslados = root.findall('.//{http://www.sat.gob.mx/cfd/4}Traslado') + root.findall('.//{http://www.sat.gob.mx/cfd/3}Traslado')
        for t in traslados:
            datos['iva'] += float(t.get('Importe', 0))
        
        # UUID
        comp_fiscal = root.find('.//{http://www.sat.gob.mx/TimbreFiscalDigital}TimbreFiscalDigital')
        if comp_fiscal is not None:
            datos['uuid'] = comp_fiscal.get('UUID', '')
        
        return datos
    except Exception as e:
        print(f"  ERROR leyendo {xml_path}: {e}")
        return None

print("="*60)
print("CLASIFICADOR DE FACTURAS - CARPETA 28")
print("="*60)

xmls = [f for f in os.listdir(SOURCE_DIR) if f.endswith('.xml')]
print(f"\nEncontrados {len(xmls)} archivos XML\n")

resultados = []
errores = []

for xml_file in sorted(xmls):
    xml_path = os.path.join(SOURCE_DIR, xml_file)
    pdf_file = xml_file.replace('.xml', '.pdf')
    pdf_path = os.path.join(SOURCE_DIR, pdf_file)
    
    datos = detectar_tipo_y_datos(xml_path)
    if datos is None:
        errores.append(xml_file)
        continue
    
    datos['archivo_xml'] = xml_file
    datos['archivo_pdf'] = pdf_file if os.path.exists(pdf_path) else ''
    resultados.append(datos)
    
    print(f"  [{datos['tipo'].upper():8}] {xml_file}")
    print(f"           Fecha: {datos['fecha']} | Semana: {datos['semana']} | Litros: {datos['cantidad']:.2f} | Total: ${datos['total']:,.2f}")
    print(f"           Desc: {datos['descripcion'][:70]}")

print(f"\n{'='*60}")
print(f"RESUMEN: {sum(1 for r in resultados if r['tipo']=='diesel')} Diésel | {sum(1 for r in resultados if r['tipo']=='gasolina')} Gasolina")
print(f"         {len(errores)} con error")

# Clasificar y mover archivos
print("\n" + "="*60)
print("MOVIENDO ARCHIVOS A CARPETAS...")
print("="*60)

for datos in resultados:
    tipo = datos['tipo']
    semana = datos['semana'].replace(' ', '_')
    
    # Crear directorio destino
    dest_dir = os.path.join(FACTURAS_DIR, tipo, semana)
    os.makedirs(dest_dir, exist_ok=True)
    
    # Mover XML
    src_xml = os.path.join(SOURCE_DIR, datos['archivo_xml'])
    dst_xml = os.path.join(dest_dir, datos['archivo_xml'])
    if os.path.exists(src_xml) and not os.path.exists(dst_xml):
        shutil.copy2(src_xml, dst_xml)
    
    # Mover PDF
    if datos['archivo_pdf']:
        src_pdf = os.path.join(SOURCE_DIR, datos['archivo_pdf'])
        dst_pdf = os.path.join(dest_dir, datos['archivo_pdf'])
        if os.path.exists(src_pdf) and not os.path.exists(dst_pdf):
            shutil.copy2(src_pdf, dst_pdf)
    
    print(f"  -> facturas/{tipo}/{semana}/  [{datos['archivo_xml']}]")

# Guardar datos para el siguiente paso
import json
with open(r"c:\Users\JOSE\Desktop\Proyecto fenix\facturas_sem28_clasificadas.json", 'w', encoding='utf-8') as f:
    json.dump(resultados, f, ensure_ascii=False, indent=2)

print("\n✓ Archivo JSON guardado: facturas_sem28_clasificadas.json")
print("✓ Archivos copiados a sus carpetas de clasificación")
print("\nListo. Lanzar siguiente script para vaciar en MAESTRO_DIESEL...")
