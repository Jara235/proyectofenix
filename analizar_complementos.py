import os
import glob
import xml.etree.ElementTree as ET

def analizar_xmls():
    xml_files = glob.glob(r'complemnetos de pago mobil\**\*.xml', recursive=True)
    print(f"Total archivos XML encontrados: {len(xml_files)}")
    
    resumen_complementos = []
    
    for path in sorted(xml_files):
        try:
            tree = ET.parse(path)
            root = tree.getroot()
            
            # Namespace stripping for easier navigation
            for elem in root.iter():
                if '}' in elem.tag:
                    elem.tag = elem.tag.split('}', 1)[1]
            
            comprobante = {
                'archivo': os.path.basename(path),
                'carpeta': os.path.basename(os.path.dirname(path)),
                'fecha_emision': root.attrib.get('Fecha'),
                'serie': root.attrib.get('Serie', ''),
                'folio': root.attrib.get('Folio', ''),
                'subtotal': root.attrib.get('SubTotal', '0'),
                'total': root.attrib.get('Total', '0'),
            }
            
            emisor = root.find('Emisor')
            if emisor is not None:
                comprobante['emisor_rfc'] = emisor.attrib.get('Rfc', '')
                comprobante['emisor_nombre'] = emisor.attrib.get('Nombre', '')
                
            receptor = root.find('Receptor')
            if receptor is not None:
                comprobante['receptor_rfc'] = receptor.attrib.get('Rfc', '')
                comprobante['receptor_nombre'] = receptor.attrib.get('Nombre', '')
                
            # Buscar TimbreFiscalDigital UUID
            tfd = root.find('.//TimbreFiscalDigital')
            comprobante['uuid'] = tfd.attrib.get('UUID', '') if tfd is not None else ''
            
            # Buscar Pagos
            pagos_list = []
            pagos_node = root.find('.//Pagos')
            if pagos_node is not None:
                for p in pagos_node.findall('Pago'):
                    pago_data = {
                        'fecha_pago': p.attrib.get('FechaPago'),
                        'forma_pago': p.attrib.get('FormaDePagoP'),
                        'moneda': p.attrib.get('MonedaP'),
                        'monto': float(p.attrib.get('Monto', 0)),
                        'num_operacion': p.attrib.get('NumOperacion', ''),
                        'doctos_relacionados': []
                    }
                    
                    for doc in p.findall('DoctoRelacionado'):
                        d_info = {
                            'id_documento': doc.attrib.get('IdDocumento'),
                            'serie': doc.attrib.get('Serie', ''),
                            'folio': doc.attrib.get('Folio', ''),
                            'num_parcialidad': doc.attrib.get('NumParcialidad', '1'),
                            'saldo_anterior': float(doc.attrib.get('ImpSaldoAnt', 0)),
                            'importe_pagado': float(doc.attrib.get('ImpPagado', 0)),
                            'saldo_insoluto': float(doc.attrib.get('ImpSaldoInsoluto', 0)),
                            'moneda': doc.attrib.get('MonedaDR', 'MXN')
                        }
                        pago_data['doctos_relacionados'].append(d_info)
                        
                    pagos_list.append(pago_data)
                    
            comprobante['pagos'] = pagos_list
            resumen_complementos.append(comprobante)
            
        except Exception as e:
            print(f"Error procesando {path}: {e}")
            
    return resumen_complementos

if __name__ == '__main__':
    datos = analizar_xmls()
    print("\n" + "="*80)
    print("DETALLE COMPLETO DE COMPLEMENTOS DE PAGO ENCONTRADOS")
    print("="*80)
    
    total_general_pagado = 0.0
    todas_facturas_aplicadas = []
    
    for idx, c in enumerate(datos, 1):
        print(f"\n[{idx}] ARCHIVO: {c['archivo']} (Carpeta: {c['carpeta']})")
        print(f"    Folio CFDI: {c['serie']}-{c['folio']} | UUID: {c['uuid']}")
        print(f"    Emisor: {c.get('emisor_nombre')} ({c.get('emisor_rfc')})")
        print(f"    Receptor: {c.get('receptor_nombre')} ({c.get('receptor_rfc')})")
        print(f"    Fecha Emisión CFDI: {c['fecha_emision']}")
        
        for p_idx, p in enumerate(c['pagos'], 1):
            total_general_pagado += p['monto']
            print(f"    --- PAGO #{p_idx} ---")
            print(f"    Fecha Pago: {p['fecha_pago']} | Monto Transferido: ${p['monto']:,.2f} {p['moneda']} | Forma Pago: {p['forma_pago']}")
            if p['num_operacion']:
                print(f"    Operación/Referencia: {p['num_operacion']}")
                
            docs = p['doctos_relacionados']
            print(f"    Facturas Liquidadas / Abonadas ({len(docs)} facturas):")
            
            suma_aplicada = sum(d['importe_pagado'] for d in docs)
            for d in docs:
                factura_tag = f"{d['serie']}{d['folio']}".strip()
                todas_facturas_aplicadas.append({
                    'complemento_archivo': c['archivo'],
                    'complemento_folio': f"{c['serie']}-{c['folio']}",
                    'fecha_pago': p['fecha_pago'],
                    'factura': factura_tag,
                    'uuid_factura': d['id_documento'],
                    'parcialidad': d['num_parcialidad'],
                    'saldo_anterior': d['saldo_anterior'],
                    'importe_pagado': d['importe_pagado'],
                    'saldo_insoluto': d['saldo_insoluto']
                })
                estado = "SALDADA AL 100%" if d['saldo_insoluto'] == 0 else f"CON SALDO PENDIENTE (${d['saldo_insoluto']:,.2f})"
                print(f"      * Factura: {factura_tag:<10} | Saldo Anterior: ${d['saldo_anterior']:>10,.2f} | Pagado: ${d['importe_pagado']:>10,.2f} | Saldo Insoluto: ${d['saldo_insoluto']:>10,.2f} | {estado}")
            print(f"    --> Total Aplicado a Facturas en este Pago: ${suma_aplicada:,.2f} (Diferencia vs Pago: ${p['monto'] - suma_aplicada:,.2f})")

    print("\n" + "="*80)
    print(f"RESUMEN GLOBAL:")
    print(f"Total Complementos XML analizados: {len(datos)}")
    print(f"Monto Total Pagado Reportado en los Complementos: ${total_general_pagado:,.2f} MXN")
    print(f"Total de Aplicaciones a Facturas: {len(todas_facturas_aplicadas)}")
    print("="*80)
