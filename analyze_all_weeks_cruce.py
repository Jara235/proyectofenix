from app_admin import get_db

db = get_db()
cur = db.conn.cursor()

# Check all weeks
cur.execute("SELECT DISTINCT semana::int as sem_int, semana FROM gasolina.consumos WHERE semana ~ '^[0-9]+$' ORDER BY sem_int")
semanas = [r[1] for r in cur.fetchall()]

print("=== RESUMEN POR SEMANA: CARGAS VS FACTURAS ===")
for s in semanas:
    # Cargas por gasolinera
    cur.execute("""
        SELECT COALESCE(gasolineria, 'LEVET') as gas, COUNT(*), SUM(importe_total), SUM(litros)
        FROM gasolina.consumos
        WHERE semana = %s
        GROUP BY COALESCE(gasolineria, 'LEVET')
    """, (s,))
    cargas_gas = {r[0].upper(): {'cargas': r[1], 'importe': float(r[2]), 'litros': float(r[3])} for r in cur.fetchall()}
    
    # Facturas por proveedor
    cur.execute("""
        SELECT proveedor, COUNT(*), SUM(importe_total), SUM(litros_facturados)
        FROM gasolina.facturas
        WHERE semana = %s
        GROUP BY proveedor
    """, (s,))
    facs_prov = {r[0]: {'facturas': r[1], 'importe': float(r[2]), 'litros': float(r[3])} for r in cur.fetchall()}
    
    print(f"\n--- SEMANA {s} ---")
    print("  Cargas registradas:")
    for g, d in cargas_gas.items():
        print(f"    {g}: {d['cargas']} cargas | ${d['importe']:,.2f} | {d['litros']:,.2f} L")
    print("  Facturas en BD:")
    for p, d in facs_prov.items():
        print(f"    {p}: {d['facturas']} facturas | ${d['importe']:,.2f} | {d['litros']:,.2f} L")

db.close()
