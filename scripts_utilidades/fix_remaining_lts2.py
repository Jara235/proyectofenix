import sqlite3

db = r'c:\Users\JOSE\Desktop\Proyecto fenix\fenix_v2.db'
c = sqlite3.connect(db)
cur = c.cursor()

PRECIO_LEVET  = 22.89
PRECIO_MOBILE = 22.89
PRECIO_SIVALE = 22.89

cur.execute("""
    SELECT id, origen, placa, vehiculo, importe_total 
    FROM gasolina_consumos 
    WHERE semana='Semana 26' AND litros=0 AND importe_total>0
""")
sin_litros = cur.fetchall()
print("Registros a completar:", len(sin_litros))

for row in sin_litros:
    rid, origen, placa, veh, imp = row
    imp = float(imp)
    if 'LEVET' in str(origen).upper():
        precio = PRECIO_LEVET
    else:
        precio = PRECIO_MOBILE
    lts = round(imp / precio, 3)
    cur.execute("UPDATE gasolina_consumos SET litros=?, costo_por_litro=? WHERE id=?", (lts, precio, rid))
    print("  id=%d | %-8s | %-10s | $%7.0f / $%.2f = %.3f lts" % (rid, str(origen), str(placa), imp, precio, lts))

c.commit()

print("\n=== RESUMEN FINAL (normalizado) ===")
cur.execute("""
    SELECT 
        CASE 
            WHEN UPPER(origen) LIKE '%LEVET%' THEN 'LEVET'
            WHEN UPPER(origen) LIKE '%MOBILE%' THEN 'MOBILE'
            WHEN UPPER(origen) LIKE '%SI VALE%' THEN 'SI VALE'
            ELSE origen
        END as gaso,
        COUNT(*) regs,
        ROUND(SUM(litros),2) lts, 
        ROUND(SUM(importe_total),2) imp
    FROM gasolina_consumos WHERE semana='Semana 26'
    GROUP BY gaso ORDER BY imp DESC
""")
for r in cur.fetchall():
    print("  %-25s | %3d regs | %8.2f lts | $%10.2f" % (str(r[0]), r[1], float(r[2]), float(r[3])))

c.close()
