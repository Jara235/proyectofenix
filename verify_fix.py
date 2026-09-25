import sqlite3
db = r'c:\Users\JOSE\Desktop\Proyecto fenix\fenix_v2.db'
c = sqlite3.connect(db)
cur = c.cursor()

print("=== RESUMEN FINAL POR GASOLINERA - Semana 26 ===")
cur.execute("""
    SELECT origen, COUNT(*) regs, 
           ROUND(SUM(litros),2) lts, 
           ROUND(SUM(importe_total),2) imp,
           ROUND(SUM(litros)/NULLIF(SUM(importe_total),0)*1000,2) as lts_por_mil
    FROM gasolina_consumos WHERE semana='Semana 26'
    GROUP BY origen ORDER BY imp DESC
""")
for r in cur.fetchall():
    print(f"  {str(r[0]):<25} | {r[1]:>3} regs | {r[2]:>8.2f} lts | ")

print()
print("=== VERIFICACION TOTAL ===")
cur.execute("SELECT ROUND(SUM(litros),2), ROUND(SUM(importe_total),2), COUNT(*) FROM gasolina_consumos WHERE semana='Semana 26'")
r = cur.fetchone()
print(f"  Total: {r[2]} registros | {r[0]} litros | ")

# Los 8 sin match necesitan update manual por solo buscar por placa+fecha sin importe
print()
print("=== REGISTROS AUN SIN LITROS (LEVET) ===")
cur.execute("SELECT id, fecha, placa, vehiculo, origen, litros, importe_total FROM gasolina_consumos WHERE semana='Semana 26' AND litros=0 AND importe_total>0")
for r in cur.fetchall():
    print(f"  id={r[0]} | {r[1]} | {str(r[2]):<12} | {str(r[3]):<25} | {str(r[4]):<8} | ")
c.close()
