from app_admin import get_db

db = get_db()

# 1. Insert/Update Tanque Pegaso in gasolina.consumos
existing = db.execute("SELECT id FROM gasolina.consumos WHERE folio_conciliacion = 'GAS-S33-A10922'").fetchone()

if existing:
    print(f"Updating existing consumo ID {existing['id']} for Tanque Pegaso...")
    db.execute("""
        UPDATE gasolina.consumos
        SET fecha = '2026-08-13',
            semana = '33',
            obra_destino = 'Tanque Pegaso',
            conductor = 'TANQUE PEGASO',
            vehiculo = 'TANQUE PEGASO',
            placa = 'S/P',
            litros = 175.07,
            costo_por_litro = 23.90,
            importe_total = 4184.10,
            gasolineria = 'MOBILE',
            observaciones = 'Suministro Tanque Pegaso (Factura A10922 Mobil Huixquilucan)'
        WHERE id = %s
    """, (existing['id'],))
else:
    print("Inserting new consumo for Tanque Pegaso...")
    db.execute("""
        INSERT INTO gasolina.consumos (
            folio_conciliacion, fecha, semana, obra_destino, conductor, vehiculo, placa,
            litros, costo_por_litro, importe_total, gasolineria, observaciones
        ) VALUES (
            'GAS-S33-A10922', '2026-08-13', '33', 'Tanque Pegaso', 'TANQUE PEGASO', 'TANQUE PEGASO', 'S/P',
            175.07, 23.90, 4184.10, 'MOBILE', 'Suministro Tanque Pegaso (Factura A10922 Mobil Huixquilucan)'
        )
    """)

# 2. Update Factura A10922 in gasolina.facturas
print("Updating factura A10922 in gasolina.facturas...")
db.execute("""
    UPDATE gasolina.facturas
    SET obra_destino = 'Tanque Pegaso',
        folio_conciliacion = 'GAS-S33-A10922',
        placa = 'S/P'
    WHERE folio_factura = 'A10922'
""")

db.commit()
print("Done updating DB!")

# Verify
fac = db.execute("SELECT id, folio_factura, folio_conciliacion, obra_destino, importe_total, litros_facturados FROM gasolina.facturas WHERE folio_factura = 'A10922'").fetchone()
print("Factura A10922:", dict(fac))

carg = db.execute("SELECT id, folio_conciliacion, obra_destino, conductor, gasolineria, importe_total, litros FROM gasolina.consumos WHERE folio_conciliacion = 'GAS-S33-A10922'").fetchone()
print("Consumo Tanque Pegaso:", dict(carg))

db.close()
