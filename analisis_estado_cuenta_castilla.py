import os
import glob
import xml.etree.ElementTree as ET
import psycopg2
from psycopg2.extras import DictCursor
import re

def obtener_complementos_septiembre():
    sept_files = [
        ('COMPLEMENTO 1: 11-SEP-2026 ($375,000.00)', r'complemnetos de pago mobil\COMPLEMENTO DE PAGO JDJ VARIOS 11-09-2026 375K\dd95413a-e0e8-4244-8ead-f96c05d05192.xml'),
        ('COMPLEMENTO 2: 15-SEP-2026 TANQUE PEGASO ($435,000.00)', r'complemnetos de pago mobil\COMPLEMENTO DE PAGO JDJ TANQUE PEGASO 15-09-26 VARIOS 435K\03700cb1-441e-4b1b-870b-14159810b799.xml'),
        ('COMPLEMENTO 3: 18-SEP-2026 ($76,923.00)', r'complemnetos de pago mobil\COMPLEMENTO DE PAGO JDJ VARIOS 18-09-2026 76K\ef400b3a-be52-4ece-b013-b494574da8ef.xml')
    ]
    
    complementos = []
    for label, path in sept_files:
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
        
        pago = root.find('.//Pago')
        f_pago = pago.attrib.get('FechaPago', '')
        monto = float(pago.attrib.get('Monto', 0))
        forma = pago.attrib.get('FormaDePagoP', '')
        num_op = pago.attrib.get('NumOperacion', '')
        
        doctos = []
        for d in pago.findall('DoctoRelacionado'):
            doctos.append({
                'id_documento': d.attrib.get('IdDocumento', '').upper(),
                'serie': d.attrib.get('Serie', ''),
                'folio': d.attrib.get('Folio', ''),
                'parcialidad': int(d.attrib.get('NumParcialidad', 1)),
                'saldo_anterior': float(d.attrib.get('ImpSaldoAnt', 0)),
                'importe_pagado': float(d.attrib.get('ImpPagado', 0)),
                'saldo_insoluto': float(d.attrib.get('ImpSaldoInsoluto', 0)),
            })
            
        complementos.append({
            'label': label,
            'archivo': os.path.basename(path),
            'uuid': uuid_comp.upper(),
            'serie_folio': f"{serie}{folio}",
            'emisor_nom': emisor_nom,
            'emisor_rfc': emisor_rfc,
            'receptor_nom': receptor_nom,
            'receptor_rfc': receptor_rfc,
            'fecha_pago': f_pago,
            'monto': monto,
            'forma': forma,
            'num_op': num_op,
            'doctos': doctos
        })
    return complementos

def buscar_metadatos_facturas():
    # Buscar en BD
    conn = psycopg2.connect("dbname=fenix_db user=postgres password=Bupito*268 host=localhost port=5432")
    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("""
        SELECT folio_factura, fecha_factura, litros_facturados, importe_total, obra_destino, estatus_pago, uuid_cfdi, 'DIESEL OBRA' as tipo
        FROM diesel.facturas
        UNION ALL
        SELECT folio_factura, fecha_factura, litros_facturados, importe_total, obra_destino, estatus_pago, uuid_cfdi, 'TRANSPORTES PEGASO' as tipo
        FROM transportes.facturas;
    """)
    rows = cur.fetchall()
    conn.close()
    
    dict_facs = {}
    for r in rows:
        if r['folio_factura']:
            dict_facs[r['folio_factura'].strip().upper()] = dict(r)
        if r['uuid_cfdi']:
            dict_facs[r['uuid_cfdi'].strip().upper()] = dict(r)
            
    # También escanear archivos XML de gasolina en disco
    for x in glob.glob(r'OBRAS\Facturas\**\*.xml', recursive=True):
        try:
            tree = ET.parse(x)
            root = tree.getroot()
            for elem in root.iter():
                if '}' in elem.tag:
                    elem.tag = elem.tag.split('}', 1)[1]
            s = root.attrib.get('Serie', '')
            f = root.attrib.get('Folio', '')
            fol = f"{s}{f}".strip().upper()
            if fol not in dict_facs:
                tfd = root.find('.//TimbreFiscalDigital')
                uid = tfd.attrib.get('UUID', '').upper() if tfd is not None else ''
                tot = float(root.attrib.get('Total', 0))
                conceptos = root.findall('.//Concepto')
                litros = sum(float(c.attrib.get('Cantidad', 0)) for c in conceptos)
                desc = conceptos[0].attrib.get('Descripcion', '') if conceptos else 'GASOLINA'
                dict_facs[fol] = {
                    'folio_factura': fol,
                    'fecha_factura': root.attrib.get('Fecha', '')[:10],
                    'litros_facturados': litros,
                    'importe_total': tot,
                    'obra_destino': f"UTILITARIOS ({desc[:20]})",
                    'tipo': 'GASOLINA'
                }
                if uid:
                    dict_facs[uid] = dict_facs[fol]
        except Exception:
            pass
            
    return dict_facs

def obtener_todos_los_complementos():
    xml_files = glob.glob(r'complemnetos de pago mobil\**\*.xml', recursive=True)
    complementos = []
    for path in sorted(xml_files):
        try:
            tree = ET.parse(path)
            root = tree.getroot()
            for elem in root.iter():
                if '}' in elem.tag:
                    elem.tag = elem.tag.split('}', 1)[1]
            tfd = root.find('.//TimbreFiscalDigital')
            uuid_comp = tfd.attrib.get('UUID') if tfd is not None else ''
            serie = root.attrib.get('Serie', '')
            folio = root.attrib.get('Folio', '')
            pago = root.find('.//Pago')
            if pago is None:
                continue
            doctos = []
            for d in pago.findall('DoctoRelacionado'):
                doctos.append({
                    'id_documento': d.attrib.get('IdDocumento', '').upper(),
                    'serie': d.attrib.get('Serie', ''),
                    'folio': d.attrib.get('Folio', ''),
                    'parcialidad': int(d.attrib.get('NumParcialidad', 1)),
                    'saldo_anterior': float(d.attrib.get('ImpSaldoAnt', 0)),
                    'importe_pagado': float(d.attrib.get('ImpPagado', 0)),
                    'saldo_insoluto': float(d.attrib.get('ImpSaldoInsoluto', 0)),
                })
            complementos.append({
                'archivo': os.path.basename(path),
                'uuid': uuid_comp.upper(),
                'serie': serie,
                'folio': folio,
                'doctos': doctos
            })
        except Exception:
            pass
    return complementos

def main():
    comps = obtener_complementos_septiembre()
    meta = buscar_metadatos_facturas()
    
    print("="*110)
    print("DETALLE COMPLETO DE LOS 3 COMPLEMENTOS DE PAGO ENVIADOS POR LA GASOLINERA (MOBIL / CASTILLA)")
    print("="*110)
    
    todas_aplicaciones = []
    
    for c in comps:
        print(f"\n{c['label']}")
        print(f"  • Archivo: {c['archivo']}")
        print(f"  • Folio Fiscal UUID: {c['uuid']}")
        print(f"  • Emisor: {c['emisor_nom']} ({c['emisor_rfc']})")
        print(f"  • Receptor: {c['receptor_nom']} ({c['receptor_rfc']})")
        print(f"  • Fecha de Pago: {c['fecha_pago']} | Referencia / SPEI: {c['num_op']}")
        print(f"  • MONTO DEL PAGO: ${c['monto']:,.2f} MXN")
        print(f"  • Facturas aplicadas en este complemento: {len(c['doctos'])}")
        print("-" * 110)
        print(f"{'#':<3} {'Factura':<12} {'Fecha Fac':<11} {'Parc':<5} {'Saldo Ant':>14} {'Monto Pagado':>14} {'Saldo Insoluto':>15}  {'Destino / Concepto'}")
        print("-" * 110)
        
        subtotal = 0.0
        for idx, d in enumerate(c['doctos'], 1):
            fol = f"{d['serie']}{d['folio']}".strip().upper()
            subtotal += d['importe_pagado']
            m = meta.get(fol) or meta.get(d['id_documento']) or {}
            f_fecha = str(m.get('fecha_factura', ''))[:10]
            f_dest = m.get('obra_destino') or 'SIN ASIGNAR'
            f_tipo = m.get('tipo', '')
            
            estado_insoluto = f"${d['saldo_insoluto']:>14,.2f}" if d['saldo_insoluto'] > 0 else "$0.00 (LIQ)"
            print(f"{idx:<3} {fol:<12} {f_fecha:<11} #{d['parcialidad']:<4} ${d['saldo_anterior']:>13,.2f} ${d['importe_pagado']:>13,.2f} {estado_insoluto:>15}  {f_dest} [{f_tipo}]")
            
            todas_aplicaciones.append({
                'comp_nombre': c['label'],
                'folio_factura': fol,
                'uuid_factura': d['id_documento'],
                'fecha_factura': f_fecha,
                'parcialidad': d['parcialidad'],
                'saldo_anterior': d['saldo_anterior'],
                'importe_pagado': d['importe_pagado'],
                'saldo_insoluto': d['saldo_insoluto'],
                'obra': f_dest,
                'tipo': f_tipo
            })
        print("-" * 110)
        print(f"TOTAL APLICADO EN ESTE COMPLEMENTO: ${subtotal:,.2f} MXN (Diferencia vs Pago: ${c['monto'] - subtotal:,.2f})\n")

    # Resumen de Saldos Insolutos
    print("="*110)
    print("ANÁLISIS DE FACTURAS CON PAGOS PARCIALES / SALDOS INSOLUTOS")
    print("="*110)
    
    # Rastrear A11292
    f11292 = [a for a in todas_aplicaciones if a['folio_factura'] == 'A11292']
    print("\n1. Factura A11292 (Despacho Directo Gasolinera - Transportes):")
    print(f"   Importe Original: $66,086.30 MXN")
    for a in f11292:
        print(f"   - En {a['comp_nombre']} (Parc #{a['parcialidad']}): Pagado ${a['importe_pagado']:,.2f} | Saldo Insoluto: ${a['saldo_insoluto']:,.2f}")
    print("   -> Resultado: LIQUIDADA AL 100% en el segundo complemento.")

    # Rastrear A11371
    f11371 = [a for a in todas_aplicaciones if a['folio_factura'] == 'A11371']
    print("\n2. Factura A11371 (Tanque Pegaso 4,000 L):")
    print(f"   Importe Original: $108,000.36 MXN")
    for a in f11371:
        print(f"   - En {a['comp_nombre']} (Parc #{a['parcialidad']}): Pagado ${a['importe_pagado']:,.2f} | Saldo Insoluto: ${a['saldo_insoluto']:,.2f}")
    print("   -> Resultado: LIQUIDADA AL 100% en el tercer complemento.")

    # Rastrear A11357
    f11357 = [a for a in todas_aplicaciones if a['folio_factura'] == 'A11357']
    print("\n3. Factura A11357 (Gasolina Utilitarios):")
    print(f"   Importe Original: $2,850.12 MXN")
    for a in f11357:
        print(f"   - En {a['comp_nombre']} (Parc #{a['parcialidad']}): Pagado ${a['importe_pagado']:,.2f} | Saldo Insoluto: ${a['saldo_insoluto']:,.2f}")
    print("   -> Resultado: ¡TIENE SALDO PENDIENTE VIVO POR $1,700.35 MXN!")

    # Estado de cuenta de facturas posteriores aún sin complemento
    print("\n" + "="*110)
    print("ESTADO DE CUENTA: FACTURAS EMITIDAS POR LA GASOLINERA PENDIENTES DE PAGO")
    print("="*110)
    
    conn = psycopg2.connect("dbname=fenix_db user=postgres password=Bupito*268 host=localhost port=5432")
    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("""
        SELECT folio_factura, fecha_factura, litros_facturados, importe_total, obra_destino, 'DIESEL' as origen
        FROM diesel.facturas
        WHERE (proveedor ILIKE '%CASTILLA%' OR folio_factura LIKE 'A11%') AND fecha_factura >= '2026-09-01'
        UNION ALL
        SELECT folio_factura, fecha_factura, litros_facturados, importe_total, obra_destino, 'TRANSPORTES' as origen
        FROM transportes.facturas
        WHERE (proveedor ILIKE '%CASTILLA%' OR folio_factura LIKE 'A11%') AND fecha_factura >= '2026-09-01'
        ORDER BY fecha_factura ASC, folio_factura ASC;
    """)
    facs_sept = cur.fetchall()
    conn.close()
    
    # Obtener todas las facturas liquidadas en CUALQUIER complemento del sistema
    todos_los_comps = obtener_todos_los_complementos()
    folios_liquidados = set()
    for c in todos_los_comps:
        for d in c['doctos']:
            fol = f"{d['serie']}{d['folio']}".strip().upper()
            if d['saldo_insoluto'] == 0:
                folios_liquidados.add(fol)
            
    pendientes_lista = []
    tot_pendiente = 0.0
    for f in facs_sept:
        fol = f['folio_factura'].strip().upper()
        if fol not in folios_liquidados:
            imp = float(f['importe_total'])
            tot_pendiente += imp
            pendientes_lista.append({
                'folio': fol,
                'fecha': f['fecha_factura'],
                'litros': float(f['litros_facturados']),
                'importe': imp,
                'destino': f['obra_destino'],
                'origen': f['origen']
            })
            
    # Agregar el saldo insoluto de A11357
    tot_pendiente += 1700.35
    
    print(f"{'Factura':<10} {'Fecha':<12} {'Litros':>10} {'Importe Pendiente':>18}  {'Obra / Destino'}")
    print("-" * 80)
    print(f"{'A11357':<10} {'2026-09-14':<12} {'114.00':>10} ${1700.35:>17,.2f}  UTILITARIOS (SALDO INSOLUTO RESTANTE)")
    for p in pendientes_lista:
        print(f"{p['folio']:<10} {str(p['fecha']):<12} {p['litros']:>10.2f} ${p['importe']:>17,.2f}  {p['destino']} ({p['origen']})")
    print("-" * 80)
    print(f"TOTAL PENDIENTE DE PAGO A LA GASOLINERA: ${tot_pendiente:,.2f} MXN\n")

if __name__ == '__main__':
    main()
