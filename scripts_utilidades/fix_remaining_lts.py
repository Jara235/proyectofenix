import sqlite3, pandas as pd

db = r'c:\Users\JOSE\Desktop\Proyecto fenix\fenix_v2.db'
c = sqlite3.connect(db)
cur = c.cursor()

# Para los registros restantes sin litros, calcular con precio conocido
# LEVET precio: ~22.89/lts (del JDJ). MOBILE: ~22.89/lts. SI VALE: tarjeta (precio aprox 22.89)
PRECIO_LEVET  = 22.89
PRECIO_MOBILE = 22.89
PRECIO_SIVALE = 22.89

cur.execute("""
    SELECT id, origen, placa, vehiculo, importe_total 
    FROM gasolina_consumos 
    WHERE semana='Semana 26' AND litros=0 AND importe_total>0
""")
sin_litros = cur.fetchall()
print(f"Registros a completar con precio estimado: {len(sin_litros)}")

for row in sin_litros:
    rid, origen, placa, veh, imp = row
    imp = float(imp)
    if 'LEVET' in str(origen).upper():
        precio = PRECIO_LEVET
    elif 'MOBILE' in str(origen).upper() or 'MOBIL' in str(origen).upper():
        precio = PRECIO_MOBILE
    else:
        precio = PRECIO_SIVALE
    
    lts = round(imp / precio, 3)
    cur.execute("UPDATE gasolina_consumos SET litros=?, costo_por_litro=? WHERE id=?", (lts, precio, rid))
    print(f"  id={rid} | {str(origen):<8} | {str(placa):<10} |  /  = {lts:.3f} lts")

c.commit()

print("\n=== RESUMEN FINAL POR GASOLINERA - Semana 26 ===")
cur.execute("""
    SELECT origen, COUNT(*) regs, 
           ROUND(SUM(litros),2) lts, 
           ROUND(SUM(importe_total),2) imp
    FROM gasolina_consumos WHERE semana='Semana 26'
    GROUP BY origen ORDER BY imp DESC
""")
for r in cur.fetchall():
    lts_per_km = round(float(r[2])/float(r[3])*1000,2) if r[3] else 0
    print(f"  {str(r[0]):<25} | {r[1]:>3} regs | {r[2]:>8.2f} lts | \")

print()
print("=== CON NORMALIZACION (MOBILE = MOBILE+MOBILE HUIXQUILUCAN) ===")
cur.execute("""
    SELECT 
        CASE 
            WHEN UPPER(origen) LIKE '%LEVET%' THEN 'LEVET'
            WHEN UPPER(origen) LIKE '%MOBILE%' OR UPPER(origen) LIKE '%MOBIL%' THEN 'MOBILE'
            WHEN UPPER(origen) LIKE '%SI VALE%' OR UPPER(origen) LIKE '%SIVALE%' THEN 'SI VALE'
            ELSE origen
        END as gaso_norm,
        COUNT(*) regs,
        ROUND(SUM(litros),2) lts, 
        ROUND(SUM(importe_total),2) imp
    FROM gasolina_consumos WHERE semana='Semana 26'
    GROUP BY gaso_norm ORDER BY imp DESC
""")
for r in cur.fetchall():
    print(f"  {str(r[0]):<25} | {r[1]:>3} regs | {r[2]:>8.2f} lts | \")

c.close()
