import os
import xml.etree.ElementTree as ET
import pandas as pd

gasolina_dir = r'c:\Users\JOSE\Desktop\Proyecto fenix\facturas\Gasolina'
maestro_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_GASOLINA_NUEVO.xlsx'

facturas_data = []
week_counts = {}

for root_dir, dirs, files in os.walk(gasolina_dir):
    folder_name = os.path.basename(root_dir)
    semana = 0
    if folder_name.startswith('Semana_'):
        try:
            semana = int(folder_name.split('_')[1])
        except:
            pass
            
    if semana not in week_counts:
        week_counts[semana] = 0
        
    for f in files:
        if f.lower().endswith('.xml'):
            filepath = os.path.join(root_dir, f)
            try:
                tree = ET.parse(filepath)
                root = tree.getroot()
                
                ns = {'cfdi': 'http://www.sat.gob.mx/cfd/3'}
                if 'http://www.sat.gob.mx/cfd/4' in root.tag:
                    ns = {'cfdi': 'http://www.sat.gob.mx/cfd/4'}
                    
                serie = root.attrib.get('Serie', '')
                folio_xml = root.attrib.get('Folio', '')
                if not folio_xml:
                    for elem in root.iter():
                        if 'TimbreFiscalDigital' in elem.tag:
                            folio_xml = elem.attrib.get('UUID', '')[:8].upper()
                            break
                            
                folio_factura = f"{serie}{folio_xml}"
                fecha_factura = root.attrib.get('Fecha', '').split('T')[0]
                
                emisor = root.find('cfdi:Emisor', ns)
                proveedor = emisor.attrib.get('Nombre', 'DESCONOCIDO') if emisor is not None else 'DESCONOCIDO'
                
                punto_carga = proveedor
                if 'J.D.J.' in proveedor.upper():
                    punto_carga = 'LEVET / MOBILE'
                
                conceptos = root.find('cfdi:Conceptos', ns)
                if conceptos is not None:
                    for concepto in conceptos.findall('cfdi:Concepto', ns):
                        desc = concepto.attrib.get('Descripcion', '').upper()
                        clave = concepto.attrib.get('ClaveProdServ', '')
                        
                        # Only process gasolina concepts
                        if 'GASOLINA' in desc or 'MAGNA' in desc or 'PREMIUM' in desc or clave in ('15101514', '15101515'):
                            cantidad = float(concepto.attrib.get('Cantidad', 0))
                            valor_unitario = float(concepto.attrib.get('ValorUnitario', 0))
                            importe_concepto = float(concepto.attrib.get('Importe', 0))
                            
                            tipo_combustible = 'Gasolina'
                            if 'MAGNA' in desc or clave == '15101514':
                                tipo_combustible = 'Magna'
                            elif 'PREMIUM' in desc or clave == '15101515':
                                tipo_combustible = 'Premium'
                            
                            iva_total = 0.0
                            impuestos = concepto.find('cfdi:Impuestos', ns)
                            if impuestos is not None:
                                traslados = impuestos.find('cfdi:Traslados', ns)
                                if traslados is not None:
                                    for traslado in traslados.findall('cfdi:Traslado', ns):
                                        if traslado.attrib.get('Impuesto') == '002':
                                            iva_total += float(traslado.attrib.get('Importe', 0))
                
                            if cantidad > 0:
                                week_counts[semana] += 1
                                folio_conciliacion = f"FAC-GAS-{semana}-{week_counts[semana]:03d}"
                                total_factura = importe_concepto + iva_total
                                
                                facturas_data.append({
                                    'FOLIO_CONCILIACION': folio_conciliacion,
                                    'FOLIO_FACTURA': folio_factura,
                                    'FECHA_FACTURA': fecha_factura,
                                    'SEMANA': semana,
                                    'PROVEEDOR': proveedor,
                                    'PUNTO_DE_CARGA': punto_carga,
                                    'LITROS_FACTURADOS': round(cantidad, 2),
                                    'PRECIO_UNITARIO': round(valor_unitario, 2),
                                    'IMPORTE': round(importe_concepto, 2),
                                    'I.V.A': round(iva_total, 2),
                                    'IMPORTE_TOTAL': round(total_factura, 2),
                                    'TIPO_COMBUSTIBLE': tipo_combustible,
                                    'ESTATUS_CONCILIACION': 'EN ESPERA'
                                })
                                
            except Exception as e:
                print(f"Error extracting from {f}: {e}")

df_facturas = pd.DataFrame(facturas_data, columns=[
    'FOLIO_CONCILIACION', 'FOLIO_FACTURA', 'FECHA_FACTURA', 'SEMANA', 'PROVEEDOR', 
    'PUNTO_DE_CARGA', 'LITROS_FACTURADOS', 'PRECIO_UNITARIO', 'IMPORTE', 'I.V.A', 
    'IMPORTE_TOTAL', 'TIPO_COMBUSTIBLE', 'ESTATUS_CONCILIACION'
])
df_facturas = df_facturas.sort_values(['SEMANA', 'FECHA_FACTURA'])
with pd.ExcelWriter(maestro_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    df_facturas.to_excel(writer, sheet_name='BD_FACTURAS', index=False)

print(f"Extracted {len(df_facturas)} individual gasolina charges into BD_FACTURAS.")
