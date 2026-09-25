from app_admin import get_db
import re

db = get_db()
cur = db.conn.cursor()

cur.execute("""
    SELECT DISTINCT semana::int as sem_int, semana 
    FROM gasolina.consumos 
    WHERE semana ~ '^[0-9]+$' 
    ORDER BY sem_int
""")
semanas = [r[1] for r in cur.fetchall()]

for s in semanas:
    cur.execute("""
        SELECT id, folio_conciliacion, fecha, conductor, placa, vehiculo, obra_destino,
               litros, costo_por_litro, importe_total, gasolineria
        FROM gasolina.consumos
        WHERE semana = %s AND (gasolineria ILIKE '%%MOBIL%%' OR gasolineria ILIKE '%%HUIX%%')
        ORDER BY id
    """, (s,))
    cargas = cur.fetchall()
    
    cur.execute("""
        SELECT id, folio_conciliacion, folio_factura, fecha_factura, proveedor,
               litros_facturados, importe_total, uuid_cfdi, estatus_revision,
               archivo_pdf IS NOT NULL as has_pdf, archivo_xml IS NOT NULL as has_xml
        FROM gasolina.facturas
        WHERE semana = %s
        ORDER BY id
    """, (s,))
    facs = cur.fetchall()
    
    print(f"\n================ SEMANA {s} ================")
    print(f"Cargas Mobil ({len(cargas)}):")
    tot_cargas_imp = sum(c[9] for c in cargas) if cargas else 0
    tot_cargas_lts = sum(c[7] for c in cargas) if cargas else 0
    print(f"  Total Cargado: ${tot_cargas_imp:,.2f} | {tot_cargas_lts:,.2f} L")
    
    print(f"Facturas en BD ({len(facs)}):")
    tot_facs_imp = sum(f[6] for f in facs) if facs else 0
    tot_facs_lts = sum(f[5] for f in facs) if facs else 0
    print(f"  Total Facturado: ${tot_facs_imp:,.2f} | {tot_facs_lts:,.2f} L")
    
    # Matching check
    matched_fac_ids = set()
    for c in cargas:
        c_folio = (c[1] or '').strip().upper()
        # extract A\d+
        m_folio = re.search(r'A\d+', c_folio)
        f_num = m_folio.group(0) if m_folio else ''
        
        match = None
        for f in facs:
            f_folio = (f[2] or '').strip().upper()
            if (f_num and f_num in f_folio) or (f_folio and f_folio in c_folio):
                match = f
                break
            if abs(float(f[6]) - float(c[9])) < 0.5:
                match = f
                break
                
        if match:
            matched_fac_ids.add(match[0])
            print(f"  [MATCH] Carga #{c[0]} ({c[3]} | {c[4]} | ${c[9]:,.2f}) <=> Factura #{match[0]} (Folio: {match[2]} | ${match[6]:,.2f} | PDF:{match[9]} XML:{match[10]})")
        else:
            print(f"  [SIN FACTURA] Carga #{c[0]} ({c[3]} | {c[4]} | Folio:{c[1]} | ${c[9]:,.2f})")
            
    unmatched_facs = [f for f in facs if f[0] not in matched_fac_ids]
    if unmatched_facs:
        print(f"  Facturas no asignadas a ticket individual ({len(unmatched_facs)}):")
        for uf in unmatched_facs:
            print(f"    Factura #{uf[0]}: Folio {uf[2]} | Fecha: {uf[3]} | ${uf[6]:,.2f} ({uf[5]} L)")

db.close()
