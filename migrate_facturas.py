import sqlite3
db = sqlite3.connect('fenix_v2.db')
db.row_factory = sqlite3.Row

# Read the wrong records from diesel_consumos
rows = db.execute("SELECT * FROM diesel_consumos WHERE origen='FACTURA'").fetchall()
print(f'Found {len(rows)} wrong records to migrate:')
for r in rows:
    print(f"  {r['folio_conciliacion']} | {r['fecha']} | {r['obra_destino']} | {r['litros']} Lts | Importe: {r['importe_total']}")
    obs = r['observaciones'] or ''
    uuid = obs.replace('UUID: ', '').split(' |')[0].strip() if 'UUID:' in obs else ''
    # Insert into diesel_facturas
    db.execute("""INSERT INTO diesel_facturas
        (folio_conciliacion, folio_factura, fecha_factura, semana, proveedor,
         punto_de_carga, litros_facturados, precio_unitario, importe, iva, importe_total, uuid_cfdi)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
        r['folio_conciliacion'],
        uuid,
        r['fecha'],
        r['semana'],
        r['equipo'] or 'DIESEL',
        r['obra_destino'],
        r['litros'],
        r['costo_por_litro'] or 0,
        round((r['litros'] or 0) * (r['costo_por_litro'] or 0), 2),
        0,
        r['importe_total'],
        uuid
    ))

# Remove wrong records from diesel_consumos
deleted = db.execute("DELETE FROM diesel_consumos WHERE origen='FACTURA'").rowcount
db.commit()
print(f'\nMigrated {len(rows)} records to diesel_facturas')
print(f'Deleted {deleted} wrong records from diesel_consumos')

# Verify
total_fac = db.execute('SELECT COUNT(*) FROM diesel_facturas').fetchone()[0]
print(f'diesel_facturas now has {total_fac} records')
db.close()
