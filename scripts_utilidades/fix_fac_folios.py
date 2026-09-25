import sqlite3
db = sqlite3.connect('fenix_v2.db')
db.row_factory = sqlite3.Row

# Update the 2 wrong records - fix folio prefix FAC -> FA, fix folio_factura (UUID -> empty since we don't know the real number), fix proveedor
rows = db.execute("SELECT id, folio_conciliacion, uuid_cfdi FROM diesel_facturas WHERE folio_conciliacion LIKE 'FAC-%'").fetchall()
for r in rows:
    new_folio = r['folio_conciliacion'].replace('FAC-', 'FA-', 1)
    db.execute("UPDATE diesel_facturas SET folio_conciliacion=?, folio_factura='1243788', proveedor='DERIVADOS DE PETROLEO CASTILLA' WHERE id=?", (new_folio, r['id']))
    print(f"Updated: {r['folio_conciliacion']} -> {new_folio}")

db.commit()
print('Done.')
db.close()
