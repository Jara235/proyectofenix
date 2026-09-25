import os
import glob
import xml.etree.ElementTree as ET
import pdfplumber
import psycopg2
from psycopg2.extras import DictCursor

def obtener_datos_db():
    try:
        conn = psycopg2.connect("dbname=fenix_db user=postgres password=Bupito*268 host=localhost port=5432")
        cur = conn.cursor(cursor_factory=DictCursor)
        
        # Facturas de diesel
        cur.execute("""
            SELECT id, folio_factura, uuid_cfdi, fecha_factura, litros_facturados, precio_unitario, importe_total, obra_destino, proveedor, estatus_pago
            FROM diesel.facturas
        """)
        dfacs = {}
        for r in cur.fetchall():
            if r['folio_factura']:
                dfacs[r['folio_factura'].strip().upper()] = dict(r)
            if r['uuid_cfdi']:
                dfacs[r['uuid_cfdi'].strip().upper()] = dict(r)
        
        # Facturas de transportes
        cur.execute("""
            SELECT id, folio_factura, uuid_cfdi, fecha_factura, litros_facturados, precio_unitario, importe_total, obra_destino, proveedor, estatus_pago
            FROM transportes.facturas
        """)
        tfacs = {}
        for r in cur.fetchall():
            if r['folio_factura']:
                tfacs[r['folio_factura'].strip().upper()] = dict(r)
            if r['uuid_cfdi']:
                tfacs[r['uuid_cfdi'].strip().upper()] = dict(r)
        
        conn.close()
        return dfacs, tfacs
    except Exception as e:
        print("Aviso: No se pudo conectar a BD local:", e)
        return {}, {}

def parse_xml_complement(path):
    tree = ET.parse(path)
    root = tree.getroot()
    for elem in root.iter():
        if '}' in elem.tag:
            elem.tag = elem.tag.split('}', 1)[1]
            
    tfd = root.find('.//TimbreFiscalDigital')
    uuid_comp = tfd.attrib.get('UUID') if tfd is not None else ''
    serie = root.attrib.get('Serie', '')
    folio = root.attrib.get('Folio', '')
    emisor = root.find('Emisor')
    emisor_nom = emisor.attrib.get('Nombre', '') if emisor is not None else ''
    emisor_rfc = emisor.attrib.get('Rfc', '') if emisor is not None else ''
    receptor = root.find('Receptor')
    receptor_nom = receptor.attrib.get('Nombre', '') if receptor is not None else ''
    receptor_rfc = receptor.attrib.get('Rfc', '') if receptor is not None else ''
    
    pagos = []
    pagos_node = root.find('.//Pagos')
    if pagos_node is not None:
        for p in pagos_node.findall('Pago'):
            p_dict = {
                'fecha_pago': p.attrib.get('FechaPago', ''),
                'monto': float(p.attrib.get('Monto', 0)),
                'forma_pago': p.attrib.get('FormaDePagoP', ''),
                'moneda': p.attrib.get('MonedaP', 'MXN'),
                'num_operacion': p.attrib.get('NumOperacion', ''),
                'doctos': []
            }
            for d in p.findall('DoctoRelacionado'):
                p_dict['doctos'].append({
                    'id_documento': d.attrib.get('IdDocumento', ''),
                    'serie': d.attrib.get('Serie', ''),
                    'folio': d.attrib.get('Folio', ''),
                    'num_parcialidad': int(d.attrib.get('NumParcialidad', 1)),
                    'saldo_anterior': float(d.attrib.get('ImpSaldoAnt', 0)),
                    'importe_pagado': float(d.attrib.get('ImpPagado', 0)),
                    'saldo_insoluto': float(d.attrib.get('ImpSaldoInsoluto', 0)),
                })
            pagos.append(p_dict)
            
    return {
        'archivo': os.path.basename(path),
        'ruta': path,
        'uuid': uuid_comp,
        'serie': serie,
        'folio': folio,
        'emisor_nom': emisor_nom,
        'emisor_rfc': emisor_rfc,
        'receptor_nom': receptor_nom,
        'receptor_rfc': receptor_rfc,
        'pagos': pagos
    }

def main():
    dfacs, tfacs = obtener_datos_db()
    
    # 3 Complementos de Septiembre
    sept_files = [
        ('11-SEP-2026 (375K)', r'complemnetos de pago mobil\COMPLEMENTO DE PAGO JDJ VARIOS 11-09-2026 375K\dd95413a-e0e8-4244-8ead-f96c05d05192.xml'),
        ('15-SEP-2026 TANQUE PEGASO (435K)', r'complemnetos de pago mobil\COMPLEMENTO DE PAGO JDJ TANQUE PEGASO 15-09-26 VARIOS 435K\03700cb1-441e-4b1b-870b-14159810b799.xml'),
        ('18-SEP-2026 (76K)', r'complemnetos de pago mobil\COMPLEMENTO DE PAGO JDJ VARIOS 18-09-2026 76K\ef400b3a-be52-4ece-b013-b494574da8ef.xml')
    ]
    
    # Históricos
    hist_files = [
        ('28-AGO-2026 (782K)', r'complemnetos de pago mobil\COMPLEMENTO DE PAGO JDJ VARIOS 28-08-2026 782k\25621123-a4cc-481c-90a0-af42290366a7.xml'),
        ('11-SEP-2026 Pago 27-AGO (500K)', r'complemnetos de pago mobil\cf595d57-b344-4700-bc1d-f885ecb62d95.xml')
    ]
    
    print("="*100)
    print("INFORME DE LOS 3 COMPLEMENTOS DE PAGO DE SEPTIEMBRE (GASOLINERA DERIVADOS DE PETROLEO CASTILLA / MOBIL)")
    print("="*100)
    
    tot_sept = 0.0
    todas_partidas_sept = []
    
    for label, fpath in sept_files:
        comp = parse_xml_complement(fpath)
        pago = comp['pagos'][0]
        tot_sept += pago['monto']
        
        print(f"\n==========================================================================================")
        print(f"COMPLEMENTO: {label}")
        print(f"  Archivo XML: {comp['archivo']}")
        print(f"  UUID Fiscal: {comp['uuid']}")
        print(f"  Folio Interno: {comp['serie']}{comp['folio']}")
        print(f"  Emisor (Gasolinera): {comp['emisor_nom']} (RFC: {comp['emisor_rfc']})")
        print(f"  Receptor: {comp['receptor_nom']} (RFC: {comp['receptor_rfc']})")
        print(f"  Fecha de Pago: {pago['fecha_pago']} | Num. Operación / SPEI: {pago['num_operacion']}")
        print(f"  MONTO TOTAL PAGADO: ${pago['monto']:,.2f} {pago['moneda']}")
        print(f"  Facturas Relacionadas Aplicadas: {len(pago['doctos'])}")
        print(f"------------------------------------------------------------------------------------------")
        print(f"{'No.':<4} {'Factura':<12} {'Parc.':<6} {'Saldo Anterior':>16} {'Monto Pagado':>16} {'Saldo Insoluto':>16}  {'Estatus / Destino BD'}")
        print(f"------------------------------------------------------------------------------------------")
        
        suma_pags = 0.0
        for i, d in enumerate(pago['doctos'], 1):
            folio_f = f"{d['serie']}{d['folio']}".strip().upper()
            suma_pags += d['importe_pagado']
            
            # Buscar en BD
            info_bd = dfacs.get(folio_f) or tfacs.get(folio_f) or dfacs.get(d['id_documento'].strip().upper()) or tfacs.get(d['id_documento'].strip().upper())
            origen = ""
            if info_bd:
                dest = info_bd.get('obra_destino') or info_bd.get('destino') or 'BD'
                origen = f"[{dest}]"
            else:
                origen = "[No en BD]"
                
            if d['saldo_insoluto'] == 0:
                st = f"LIQUIDADA 100% {origen}"
            else:
                st = f"PENDIENTE ${d['saldo_insoluto']:,.2f} {origen}"
                
            print(f"{i:<4} {folio_f:<12} #{d['num_parcialidad']:<5} ${d['saldo_anterior']:>15,.2f} ${d['importe_pagado']:>15,.2f} ${d['saldo_insoluto']:>15,.2f}  {st}")
            
            todas_partidas_sept.append({
                'complemento': label,
                'fecha_pago': pago['fecha_pago'],
                'folio_f': folio_f,
                'uuid_f': d['id_documento'],
                'parcialidad': d['num_parcialidad'],
                'saldo_ant': d['saldo_anterior'],
                'pagado': d['importe_pagado'],
                'insoluto': d['saldo_insoluto'],
                'destino': origen
            })
            
        print(f"------------------------------------------------------------------------------------------")
        print(f"Suma Aplicada en Facturas: ${suma_pags:,.2f} | Diferencia vs Monto del Pago: ${pago['monto'] - suma_pags:,.2f}")

    print("\n" + "="*100)
    print(f"RESUMEN EJECUTIVO DE LOS 3 COMPLEMENTOS DE SEPTIEMBRE:")
    print(f"Monto Total Pagado: ${tot_sept:,.2f} MXN")
    print(f"Total Facturas con Aplicación: {len(todas_partidas_sept)}")
    
    # Facturas con saldo insoluto > 0
    con_saldo = [p for p in todas_partidas_sept if p['insoluto'] > 0]
    print(f"\nFACTURAS CON SALDO INSOLUTO (QUEDARON PENDIENTES CON SALDO): {len(con_saldo)}")
    for cs in con_saldo:
        print(f"  * Factura {cs['folio_f']} en {cs['complemento']}: Saldo Ant: ${cs['saldo_ant']:,.2f} | Pagado: ${cs['pagado']:,.2f} | SALDO PENDIENTE: ${cs['insoluto']:,.2f}")
        
    # Verificar si alguna factura fue pagada en partes entre estos complementos
    print("\nTRAZABILIDAD DE FACTURAS CON PAGOS EN MÁS DE UNA PARCIALIDAD:")
    folios_todos = [p['folio_f'] for p in todas_partidas_sept]
    folios_multi = set([f for f in folios_todos if folios_todos.count(f) > 1])
    for fm in sorted(folios_multi):
        parts = [p for p in todas_partidas_sept if p['folio_f'] == fm]
        print(f"  >> Factura {fm}:")
        for pt in parts:
            print(f"     - {pt['complemento']} (Parc #{pt['parcialidad']}): Pagado ${pt['pagado']:,.2f} -> Quedó con Saldo Insoluto: ${pt['insoluto']:,.2f}")

if __name__ == '__main__':
    main()
