import psycopg2
import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor()
print("Conectado a PostgreSQL")

# Corregir facturas del 13 de julio que son Semana 29
print("\n=== CORRIGIENDO SEMANA DE FACTURAS DEL 13/07/2026 ===")

cur.execute("""
    UPDATE diesel.facturas 
    SET semana = 'Semana 29'
    WHERE fecha_factura = '2026-07-13'
    AND semana = 'Semana 28'
    RETURNING folio_conciliacion, folio_factura, litros_facturados, punto_de_carga
""")
corregidas = cur.fetchall()

for r in corregidas:
    print(f"  Corregido: {r[0]} | Folio {r[1]} | {r[2]} Lts | {(r[3] or '')[:50]}")

conn.commit()
print(f"\n  Total corregidas: {len(corregidas)} facturas -> Semana 29")

# Actualizar tambien el SEMANA_MAP para futuras clasificaciones
# 2026-07-13 = inicio de Semana 29

# Verificar totales por semana
print("\n=== VERIFICACION FINAL POR SEMANA ===")
cur.execute("""
    SELECT semana, COUNT(*) facturas, ROUND(SUM(litros_facturados),1) litros, ROUND(SUM(importe_total),2) importe
    FROM diesel.facturas
    GROUP BY semana ORDER BY semana
""")
print(f"\n{'Semana':<12} {'Facturas':>9} {'Litros':>10} {'Importe':>15}")
print("=" * 50)
for r in cur.fetchall():
    print(f"  {r[0]:<10} {r[1]:>9} {r[2]:>10} ${r[3]:>14,.2f}")

# Verificar Semana 28 y 29 especificamente
print("\n--- Semana 28 por Obra ---")
cur.execute("""
    SELECT folio_factura, fecha_factura, litros_facturados
    FROM diesel.facturas WHERE semana = 'Semana 28'
    ORDER BY fecha_factura
""")
rows = cur.fetchall()
print(f"Fechas en Semana 28:")
fechas = {}
for r in rows:
    fecha = str(r[1])
    fechas[fecha] = fechas.get(fecha, 0) + 1
for fecha, cnt in sorted(fechas.items()):
    print(f"  {fecha}: {cnt} facturas")

print("\n--- Semana 29 por Obra ---")
cur.execute("""
    SELECT folio_factura, fecha_factura, litros_facturados, punto_de_carga
    FROM diesel.facturas WHERE semana = 'Semana 29'
    ORDER BY fecha_factura
""")
rows29 = cur.fetchall()
print(f"Facturas en Semana 29:")
for r in rows29:
    print(f"  Folio {r[1]} | {r[2]} Lts | {(r[3] or '')[:50]}")

cur.close()
conn.close()
print("\nCorrecion completada!")
