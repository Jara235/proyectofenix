from app_admin import get_db

db = get_db()

# 1. Update José Cabello / Jack 700.00 to Mobil A10881
print("Updating José Cabello load to Mobil A10881...")
db.execute("""
    UPDATE gasolina.consumos
    SET fecha = '2026-08-13',
        gasolineria = 'MOBILE',
        folio_conciliacion = 'GAS-S33-A10881',
        litros = 29.29,
        costo_por_litro = 23.90,
        importe_total = 700.00,
        obra_destino = 'ESTIMACIONES /PLANTA PEGASO',
        placa = 'LHB176D'
    WHERE id = 431
""")

# 2. Insert Damian Antonio Puini A10943 if not already exists
row_puini = db.execute("SELECT id FROM gasolina.consumos WHERE folio_conciliacion = 'GAS-S33-A10943'").fetchone()
if not row_puini:
    print("Inserting Damian Antonio Puini A10943...")
    db.execute("""
        INSERT INTO gasolina.consumos (
            folio_conciliacion, fecha, semana, obra_destino, vehiculo, placa, litros, costo_por_litro, importe_total, conductor, gasolineria
        ) VALUES (
            'GAS-S33-A10943', '2026-08-15', '33', 'P. ASFALTO HUIXQUILUCAN', 'FORD RANGER', 'PCU7482', 20.92, 23.90, 500.00, 'DAMIAN ANTONIO PUINI', 'MOBILE'
        )
    """)

# 3. Insert Luis Valdez A10929 if not already exists
row_valdez = db.execute("SELECT id FROM gasolina.consumos WHERE folio_conciliacion = 'GAS-S33-A10929'").fetchone()
if not row_valdez:
    print("Inserting Luis Valdez A10929...")
    db.execute("""
        INSERT INTO gasolina.consumos (
            folio_conciliacion, fecha, semana, obra_destino, vehiculo, placa, litros, costo_por_litro, importe_total, conductor, gasolineria
        ) VALUES (
            'GAS-S33-A10929', '2026-08-14', '33', 'Planta Huixquilucan', 'EQUIPO MENOR', 'S/P', 12.55, 23.90, 300.00, 'LUIS VALDEZ', 'MOBILE'
        )
    """)

# 4. Fix Conductor on ID 417 if empty
db.execute("""
    UPDATE gasolina.consumos
    SET conductor = 'CORTADORA DE CONCRETO',
        obra_destino = 'LERMA TENANGO'
    WHERE id = 417 AND (conductor IS NULL OR conductor = '')
""")

db.commit()
print("Database successfully synchronized!")

# Verify new state of Semana 33
consumos = db.execute("""
    SELECT id, folio_conciliacion, fecha, conductor, gasolineria, importe_total, litros
    FROM gasolina.consumos
    WHERE semana = '33'
    ORDER BY id
""").fetchall()

print(f"\nTotal consumos in DB for Semana 33 now: {len(consumos)}")
tot_m = sum(float(c['importe_total']) for c in consumos if c['gasolineria'] == 'MOBILE')
tot_l = sum(float(c['importe_total']) for c in consumos if c['gasolineria'] == 'LEVET')
tot_s = sum(float(c['importe_total']) for c in consumos if c['gasolineria'] == 'SI VALE')
print(f"Mobil Total: ${tot_m:,.2f} ({len([c for c in consumos if c['gasolineria']=='MOBILE'])} cargas)")
print(f"Levet Total: ${tot_l:,.2f} ({len([c for c in consumos if c['gasolineria']=='LEVET'])} cargas)")
print(f"Si Vale Total: ${tot_s:,.2f} ({len([c for c in consumos if c['gasolineria']=='SI VALE'])} cargas)")
print(f"Grand Total: ${tot_m + tot_l + tot_s:,.2f}")

db.close()
