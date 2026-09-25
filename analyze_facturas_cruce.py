from app_admin import get_db

db = get_db()
facturas = db.execute("""
    SELECT id, folio_conciliacion, folio_factura, fecha_factura, semana, proveedor,
           litros_facturados, importe_total, uuid_cfdi, estatus_revision, estatus_pago,
           archivo_pdf IS NOT NULL as has_pdf, archivo_xml IS NOT NULL as has_xml,
           placa, obra_destino
    FROM gasolina.facturas
    ORDER BY semana ASC, id ASC
""").fetchall()

print(f"Total facturas in gasolina.facturas: {len(facturas)}")
for f in facturas:
    print(f"ID:{f['id']:2d} | Sem:{f['semana']} | Folio:{f['folio_factura']} | Fecha:{f['fecha_factura']} | Prov:{f['proveedor']} | Lts:{f['litros_facturados']} | Tot:${f['importe_total']} | PDF:{f['has_pdf']} | XML:{f['has_xml']} | Est:{f['estatus_revision']}")

# Check distinct providers in facturas
provs = db.execute("""
    SELECT proveedor, COUNT(*) as cnt, SUM(importe_total) as tot_imp, SUM(litros_facturados) as tot_lts
    FROM gasolina.facturas
    GROUP BY proveedor
""").fetchall()
print("\nProviders in facturas:")
for p in provs:
    print(f"  {p['proveedor']}: {p['cnt']} facturas | ${p['tot_imp']} | {p['tot_lts']} L")

# Check consumos folios vs facturas folios
print("\nCheck folio matches between consumos and facturas:")
matches = db.execute("""
    SELECT c.id as consumo_id, c.semana, c.fecha, c.gasolineria, c.folio_conciliacion as c_folio,
           c.importe_total as c_imp, c.litros as c_lts, c.conductor, c.placa,
           f.id as factura_id, f.folio_factura, f.proveedor, f.importe_total as f_imp, f.litros_facturados as f_lts
    FROM gasolina.consumos c
    LEFT JOIN gasolina.facturas f ON (
        f.folio_factura = c.folio_conciliacion 
        OR c.folio_conciliacion ILIKE '%' || f.folio_factura || '%'
        OR f.folio_factura ILIKE '%' || c.folio_conciliacion || '%'
        OR (c.folio_conciliacion IS NOT NULL AND f.folio_conciliacion = c.folio_conciliacion)
    )
    WHERE c.gasolineria ILIKE '%mobil%' OR c.gasolineria ILIKE '%huixquilucan%' OR f.id IS NOT NULL
    ORDER BY c.semana, c.id
""").fetchall()

print(f"Found {len(matches)} matches / Mobil loads:")
for m in matches[:30]:
    print(f"  Consumo:{m['consumo_id']} (Sem {m['semana']}) | Gas:{m['gasolineria']} | C_Folio:{m['c_folio']} | ${m['c_imp']} | Factura:{m['folio_factura']} (${m['f_imp']})")

db.close()
