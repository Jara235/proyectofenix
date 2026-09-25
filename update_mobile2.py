import sqlite3

db = r'c:\Users\JOSE\Desktop\Proyecto fenix\fenix_v2.db'
c = sqlite3.connect(db)
cur = c.cursor()

# estados_cuenta_gasolina -> gasolina_estados_cuenta
cur.execute("""
    UPDATE gasolina_estados_cuenta
    SET gasolinera = 'MOBILE'
    WHERE UPPER(gasolinera) LIKE '%MOBILE%' OR UPPER(gasolinera) LIKE '%MOBIL%'
""")
print("gasolina_estados_cuenta actualizados:", cur.rowcount)

c.commit()

print("\n=== RESUMEN FINAL ===")
cur.execute("""
    SELECT origen, COUNT(*) regs, ROUND(SUM(litros),2) lts, ROUND(SUM(importe_total),2) imp
    FROM gasolina_consumos WHERE semana='Semana 26'
    GROUP BY origen ORDER BY imp DESC
""")
for r in cur.fetchall():
    print("  %-25s | %3d regs | %8.2f lts | $%10.2f" % (str(r[0]), r[1], float(r[2]), float(r[3])))

c.close()
