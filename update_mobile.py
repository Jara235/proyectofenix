import sqlite3

db = r'c:\Users\JOSE\Desktop\Proyecto fenix\fenix_v2.db'
c = sqlite3.connect(db)
cur = c.cursor()

print("=== ACTUALIZANDO ORIGEN/PROVEEDOR A 'MOBILE' ===")

# gasolina_consumos
cur.execute("""
    UPDATE gasolina_consumos
    SET origen = 'MOBILE'
    WHERE UPPER(origen) LIKE '%MOBILE%' OR UPPER(origen) LIKE '%MOBIL%'
""")
print("gasolina_consumos actualizados:", cur.rowcount)

# gasolina_facturas
cur.execute("""
    UPDATE gasolina_facturas
    SET proveedor = 'MOBILE'
    WHERE UPPER(proveedor) LIKE '%MOBILE%' OR UPPER(proveedor) LIKE '%MOBIL%'
""")
print("gasolina_facturas actualizados:", cur.rowcount)

# estados_cuenta_gasolina
cur.execute("""
    UPDATE estados_cuenta_gasolina
    SET gasolinera = 'MOBILE'
    WHERE UPPER(gasolinera) LIKE '%MOBILE%' OR UPPER(gasolinera) LIKE '%MOBIL%'
""")
print("estados_cuenta_gasolina actualizados:", cur.rowcount)

c.commit()

print("\n=== RESUMEN GASOLINA_CONSUMOS (Semana 26) ===")
cur.execute("""
    SELECT origen, COUNT(*) regs, ROUND(SUM(litros),2) lts, ROUND(SUM(importe_total),2) imp
    FROM gasolina_consumos WHERE semana='Semana 26'
    GROUP BY origen ORDER BY imp DESC
""")
for r in cur.fetchall():
    print("  %-25s | %3d regs | %8.2f lts | $%10.2f" % (str(r[0]), r[1], float(r[2]), float(r[3])))

c.close()
