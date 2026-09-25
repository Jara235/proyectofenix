import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import sqlite3
import os
import json
import xml.etree.ElementTree as ET
import glob

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fenix.db")
FACTURAS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "facturas")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # Crear tabla documental
    cur.execute("""
        CREATE TABLE IF NOT EXISTS fenix_facturas_documentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uuid_cfdi TEXT UNIQUE,
            folio TEXT,
            fecha_emision TEXT,
            emisor_rfc TEXT,
            emisor_nombre TEXT,
            receptor_rfc TEXT,
            receptor_nombre TEXT,
            litros_totales REAL,
            subtotal REAL,
            total REAL,
            conceptos_json TEXT,
            archivo_pdf BLOB,
            archivo_xml BLOB,
            estatus_validacion TEXT DEFAULT 'PENDIENTE', -- PENDIENTE, VALIDADA, RECHAZADA
            fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def extract_xml_data(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    ns = {'cfdi': 'http://www.sat.gob.mx/cfd/4'}
    
    # ATRIBUTOS PRINCIPALES
    uuid_cfdi = None
    folio = root.attrib.get('Folio', '')
    fecha = root.attrib.get('Fecha', '')
    subtotal = float(root.attrib.get('SubTotal', 0))
    total = float(root.attrib.get('Total', 0))
    
    # EMISOR Y RECEPTOR
    emisor = root.find('cfdi:Emisor', ns)
    receptor = root.find('cfdi:Receptor', ns)
    
    emi_rfc = emisor.attrib.get('Rfc', '') if emisor is not None else ''
    emi_nom = emisor.attrib.get('Nombre', '') if emisor is not None else ''
    
    rec_rfc = receptor.attrib.get('Rfc', '') if receptor is not None else ''
    rec_nom = receptor.attrib.get('Nombre', '') if receptor is not None else ''
    
    # CONCEPTOS
    conceptos_node = root.find('cfdi:Conceptos', ns)
    conceptos = []
    litros_totales = 0.0
    
    if conceptos_node is not None:
        for c in conceptos_node.findall('cfdi:Concepto', ns):
            cant = float(c.attrib.get('Cantidad', 0))
            desc = c.attrib.get('Descripcion', '')
            vu = float(c.attrib.get('ValorUnitario', 0))
            imp = float(c.attrib.get('Importe', 0))
            
            conceptos.append({
                'cantidad': cant,
                'descripcion': desc,
                'valor_unitario': vu,
                'importe': imp
            })
            
            # Asumir que si dice LTR o litros es combustible (en este caso es de gasolinera/diesel)
            if 'LTR' in c.attrib.get('ClaveUnidad', '') or 'LITRO' in c.attrib.get('Unidad', '').upper():
                litros_totales += cant
            elif cant > 100: # Si no dice LTR pero es grande, asume que es litros
                litros_totales += cant

    # TIMBRE FISCAL (Para el UUID)
    complemento = root.find('cfdi:Complemento', ns)
    if complemento is not None:
        for child in complemento:
            if 'TimbreFiscalDigital' in child.tag:
                uuid_cfdi = child.attrib.get('UUID')
                break
                
    if not uuid_cfdi:
        # Fallback al filename
        uuid_cfdi = os.path.basename(xml_path).replace('.xml', '')
        
    return {
        'uuid': uuid_cfdi,
        'folio': folio,
        'fecha': fecha,
        'emisor_rfc': emi_rfc,
        'emisor_nombre': emi_nom,
        'receptor_rfc': rec_rfc,
        'receptor_nombre': rec_nom,
        'litros_totales': litros_totales,
        'subtotal': subtotal,
        'total': total,
        'conceptos': conceptos
    }

def process_folder():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Buscar todos los XML de forma recursiva
    xml_files = glob.glob(os.path.join(FACTURAS_DIR, '**', '*.xml'), recursive=True)
    insertados = 0
    errores = 0
    duplicados = 0
    
    for xml_path in xml_files:
        pdf_path = xml_path.replace('.xml', '.pdf')
        
        try:
            data = extract_xml_data(xml_path)
            
            # Leer XML como BLOB
            with open(xml_path, 'rb') as f:
                xml_blob = f.read()
                
            # Leer PDF como BLOB (si existe)
            pdf_blob = None
            if os.path.exists(pdf_path):
                with open(pdf_path, 'rb') as f:
                    pdf_blob = f.read()
            else:
                print(f"⚠️ Advertencia: PDF no encontrado para {os.path.basename(xml_path)}")
                
            cur.execute("""
                INSERT INTO fenix_facturas_documentos
                (uuid_cfdi, folio, fecha_emision, emisor_rfc, emisor_nombre, 
                 receptor_rfc, receptor_nombre, litros_totales, subtotal, total, 
                 conceptos_json, archivo_pdf, archivo_xml)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['uuid'], data['folio'], data['fecha'], 
                data['emisor_rfc'], data['emisor_nombre'],
                data['receptor_rfc'], data['receptor_nombre'],
                data['litros_totales'], data['subtotal'], data['total'],
                json.dumps(data['conceptos']),
                pdf_blob, xml_blob
            ))
            insertados += 1
            
        except sqlite3.IntegrityError:
            duplicados += 1
        except Exception as e:
            print(f"❌ Error procesando {os.path.basename(xml_path)}: {e}")
            errores += 1
            
    conn.commit()
    conn.close()
    
    print(f"\n✅ Procesamiento Documental Completado:")
    print(f"  - Nuevas insertadas: {insertados}")
    print(f"  - Duplicadas ignoradas: {duplicados}")
    print(f"  - Errores: {errores}")

if __name__ == "__main__":
    init_db()
    process_folder()
