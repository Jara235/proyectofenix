import psycopg2
import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor()
print("Conectado a PostgreSQL")

print("\n=== CORRIGIENDO FACTURAS DEL 06/07 -> SEMANA 27 ===")
cur.execute("""
    UPDATE diesel.facturas 
    SET semana = 'Semana 27'
    WHERE fecha_factura = '2026-07-06'
    AND semana = 'Semana 28'
    RETURNING folio_conciliacion, folio_factura, litros_facturados, punto_de_carga
""")
corregidas = cur.fetchall()
for r in corregidas:
    print(f"  Semana 27 <- {r[0]} | Folio {r[1]} | {r[2]} Lts | {(r[3] or '')[:45]}")

conn.commit()
print(f"\n  Total corregidas: {len(corregidas)} facturas -> Semana 27")

# Verificar resumen final
print("\n=== TABLA RESUMEN FINAL POR SEMANA ===")
cur.execute("""
    SELECT semana, COUNT(*) facturas, ROUND(SUM(litros_facturados),1) litros, ROUND(SUM(importe_total),2) importe
    FROM diesel.facturas
    GROUP BY semana ORDER BY semana
""")
print(f"\n{'Semana':<12} {'Facturas':>9} {'Litros':>10} {'Importe':>15}")
print("=" * 52)
for r in cur.fetchall():
    print(f"  {r[0]:<10} {r[1]:>9} {r[2]:>10} ${r[3]:>14,.2f}")

# Validar fechas en cada semana
print("\n=== VALIDACION DE FECHAS POR SEMANA ===")
cur.execute("""
    SELECT semana, MIN(fecha_factura), MAX(fecha_factura), COUNT(*)
    FROM diesel.facturas
    GROUP BY semana ORDER BY semana
""")
print(f"\n{'Semana':<12} {'Fecha Inicio':>14} {'Fecha Fin':>12} {'Facturas':>10}")
print("-" * 52)
for r in cur.fetchall():
    print(f"  {r[0]:<10} {str(r[1]):>14} {str(r[2]):>12} {r[3]:>10}")

cur.close()
conn.close()
print("\nCorreccion completada!")
