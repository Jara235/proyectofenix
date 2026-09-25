import sqlite3
db = r'c:\Users\JOSE\Desktop\Proyecto fenix\fenix_v2.db'
c = sqlite3.connect(db)
cur = c.cursor()

cur.execute("PRAGMA table_info(gasolina_consumos)")
print("Columnas gasolina_consumos:", [r[1] for r in cur.fetchall()])

print()
print("=== LEVET - detalle completo ===")
cur.execute("""
    SELECT fecha, placa, vehiculo, obra_destino, litros, importe_total
    FROM gasolina_consumos 
    WHERE UPPER(origen) = 'LEVET' AND semana='Semana 26'
    ORDER BY fecha
""")
for r in cur.fetchall():
    print(f"  {str(r[0]):<12} | {str(r[1]):<12} | {str(r[2]):<25} | {str(r[3]):<30} | {r[4]:>7.1f}lts | ")

print()
print("=== MOBILE/MOBILE HUIXQUILUCAN - detalle completo ===")
cur.execute("""
    SELECT fecha, placa, vehiculo, obra_destino, origen, litros, importe_total
    FROM gasolina_consumos 
    WHERE (UPPER(origen) LIKE '%MOBILE%' OR UPPER(origen) LIKE '%MOBIL%') AND semana='Semana 26'
    ORDER BY fecha, origen
""")
for r in cur.fetchall():
    print(f"  {str(r[0]):<12} | {str(r[1]):<12} | {str(r[2]):<25} | {str(r[3]):<25} | {str(r[4]):<22} | {r[5]:>7.1f}lts | ")

c.close()
