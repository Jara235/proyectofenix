import os
import xml.etree.ElementTree as ET
import pandas as pd

# Namespace definitions common in CFDI
ns = {
    'cfdi': 'http://www.sat.gob.mx/cfd/4',
    'cfdi3': 'http://www.sat.gob.mx/cfd/3'
}

folder_path = r"c:\Users\JOSE\Desktop\Proyecto fenix\facturas"
data = []

for filename in os.listdir(folder_path):
    if filename.lower().endswith('.xml'):
        filepath = os.path.join(folder_path, filename)
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            
            # Determine CFDI version
            prefix = 'cfdi' if root.tag.endswith('Comprobante') and 'http://www.sat.gob.mx/cfd/4' in root.tag else 'cfdi3'
            # Check namespaces actually used
            namespaces = dict([
                node for _, node in ET.iterparse(filepath, events=['start-ns'])
            ])
            cfdi_ns = namespaces.get('cfdi', 'http://www.sat.gob.mx/cfd/4')
            ns_map = {'cfdi': cfdi_ns}

            # Extract basic info
            folio = root.get('Folio', filename.replace('.xml', ''))
            fecha = root.get('Fecha', '').split('T')[0]
            
            emisor_node = root.find('cfdi:Emisor', ns_map)
            proveedor = emisor_node.get('Nombre', 'Desconocido') if emisor_node is not None else 'Desconocido'
            
            conceptos = root.find('cfdi:Conceptos', ns_map)
            if conceptos is not None:
                for concepto in conceptos.findall('cfdi:Concepto', ns_map):
                    descripcion = concepto.get('Descripcion', '').upper()
                    
                    # Extract values
                    try:
                        cantidad = float(concepto.get('Cantidad', 0))
                    except:
                        cantidad = 0.0
                        
                    try:
                        valor_unitario = float(concepto.get('ValorUnitario', 0))
                    except:
                        valor_unitario = 0.0
                        
                    try:
                        importe = float(concepto.get('Importe', 0))
                    except:
                        importe = 0.0
                    
                    tipo_combustible = "Otro"
                    if "DIESEL" in descripcion or "DIÉSEL" in descripcion:
                        tipo_combustible = "Diésel"
                    elif "MAGNA" in descripcion or "REGULAR" in descripcion or "GASOLINA" in descripcion:
                        tipo_combustible = "Gasolina"

                    data.append({
                        'ARCHIVO_ORIGEN': filename,
                        'FOLIO_FACTURA': folio,
                        'FECHA_FACTURA': fecha,
                        'PROVEEDOR': proveedor,
                        'DESCRIPCION_SAT': descripcion,
                        'TIPO_COMBUSTIBLE': tipo_combustible,
                        'LITROS_FACTURADOS': cantidad,
                        'PRECIO_UNITARIO': valor_unitario,
                        'IMPORTE_TOTAL': importe
                    })
        except Exception as e:
            print(f"Error parseando {filename}: {str(e)}")

# Create DataFrame
df = pd.DataFrame(data)

# Sort by Date
if not df.empty:
    df = df.sort_values(by='FECHA_FACTURA')
    
    # Filter only Diesel (or allow the user to see all but clearly marked)
    # The user requested specifically all, but let them filter, however they said "necesitarimos todas laas que digan disel"
    # I will sort Diesel first so it's easy for them
    df = df.sort_values(by=['TIPO_COMBUSTIBLE', 'FECHA_FACTURA'], ascending=[True, True])

# Export to Excel
output_path = r"c:\Users\JOSE\Desktop\Proyecto fenix\FACTURAS_EXTRAIDAS_REVISION.xlsx"
df.to_excel(output_path, index=False)
print(f"Exportado exitosamente a {output_path} con {len(df)} registros.")
