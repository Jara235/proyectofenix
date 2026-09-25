import sqlite3
db = r'c:\Users\JOSE\Desktop\Proyecto fenix\fenix_v2.db'
c = sqlite3.connect(db)
cur = c.cursor()

print("=== CONSUMOS POR ORIGEN/GASOLINERA ===")
cur.execute("""
    SELECT semana, origen, COUNT(*) regs, 
           COALESCE(SUM(litros),0) lts, 
           COALESCE(SUM(importe_total),0) imp
    FROM gasolina_consumos 
    GROUP BY semana, origen 
    ORDER BY semana, imp DESC
""")
for r in cur.fetchall():
    print(f"  {r[0]} | {str(r[1]):<30} | {r[2]:>3} regs | {r[3]:>8.1f} lts | ")

print()
print("=== MUESTRA DE REGISTROS CON origen='MOBILE HUIXQUILUCAN' ===")
cur.execute("""
    SELECT semana, fecha, placa, vehiculo, obra_destino, origen, litros, importe_total
    FROM gasolina_consumos 
    WHERE UPPER(origen) LIKE '%MOBILE%' OR UPPER(origen) LIKE '%MOBIL%'
    LIMIT 20
""")
for r in cur.fetchall():
    print(f"  {r[0]} | {str(r[1]):<12} | {str(r[2]):<12} | {str(r[4]):<25} | {str(r[5]):<20} | {r[6]:>6.1f}lts | ")

print()
print("=== MUESTRA DE REGISTROS CON origen='LEVET' ===")
cur.execute("""
    SELECT semana, fecha, placa, vehiculo, obra_destino, origen, litros, importe_total
    FROM gasolina_consumos 
    WHERE UPPER(origen) LIKE '%LEVET%'
    LIMIT 20
""")
for r in cur.fetchall():
    print(f"  {r[0]} | {str(r[1]):<12} | {str(r[2]):<12} | {str(r[4]):<25} | {str(r[5]):<20} | {r[6]:>6.1f}lts | ")

c.close()
