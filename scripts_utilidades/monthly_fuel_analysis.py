import psycopg2
from psycopg2.extras import DictCursor

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

print("================================================================")
print("  ANALISIS DETALLADO DE DIESEL POR MES Y OBRA")
print("================================================================")

# Diesel Consumos (Vales en campo) por mes
cur.execute("""
    SELECT 
        CASE 
            WHEN obra_destino ILIKE '%TOLUCA%' AND obra_destino NOT ILIKE '%BACHEO%' THEN 'MEXICO-TOLUCA'
            WHEN obra_destino ILIKE '%LERMA%' THEN 'LERMA-TRES MARIAS'
            ELSE obra_destino 
        END as obra_norm,
        TO_CHAR(TO_DATE(fecha, 'YYYY-MM-DD'), 'YYYY-MM') as mes,
        COUNT(*) as total_cargas,
        SUM(litros) as total_litros,
        SUM(importe_total) as total_importe,
        AVG(costo_por_litro) as costo_prom_litro
    FROM diesel.consumos
    WHERE (obra_destino ILIKE '%TOLUCA%' AND obra_destino NOT ILIKE '%BACHEO%')
       OR obra_destino ILIKE '%LERMA%'
    GROUP BY obra_norm, mes
    ORDER BY obra_norm, mes;
""")
print("\n--- DIESEL (VALES DE CAMPO / CONSUMOS) ---")
for r in cur.fetchall():
    print(dict(r))

# Diesel Facturas por mes
cur.execute("""
    SELECT 
        CASE 
            WHEN obra_destino ILIKE '%TOLUCA%' AND obra_destino NOT ILIKE '%BACHEO%' THEN 'MEXICO-TOLUCA'
            WHEN obra_destino ILIKE '%LERMA%' THEN 'LERMA-TRES MARIAS'
            ELSE obra_destino 
        END as obra_norm,
        TO_CHAR(TO_DATE(fecha_factura, 'YYYY-MM-DD'), 'YYYY-MM') as mes,
        COUNT(*) as total_facturas,
        SUM(litros_facturados) as total_litros,
        SUM(importe_total) as total_importe
    FROM diesel.facturas
    WHERE (obra_destino ILIKE '%TOLUCA%' AND obra_destino NOT ILIKE '%BACHEO%')
       OR obra_destino ILIKE '%LERMA%'
    GROUP BY obra_norm, mes
    ORDER BY obra_norm, mes;
""")
print("\n--- DIESEL (FACTURAS PROVEEDOR) ---")
for r in cur.fetchall():
    print(dict(r))

print("\n================================================================")
print("  ANALISIS DETALLADO DE GASOLINA POR MES Y OBRA")
print("================================================================")

# Gasolina Consumos (Vales en campo) por mes
cur.execute("""
    SELECT 
        CASE 
            WHEN obra_destino ILIKE '%TOLUCA%' AND obra_destino NOT ILIKE '%BACHEO%' THEN 'MEXICO-TOLUCA'
            WHEN obra_destino ILIKE '%LERMA%' THEN 'LERMA-TRES MARIAS'
            ELSE obra_destino 
        END as obra_norm,
        TO_CHAR(TO_DATE(fecha, 'YYYY-MM-DD'), 'YYYY-MM') as mes,
        COUNT(*) as total_cargas,
        SUM(litros) as total_litros,
        SUM(importe_total) as total_importe,
        AVG(costo_por_litro) as costo_prom_litro
    FROM gasolina.consumos
    WHERE (obra_destino ILIKE '%TOLUCA%' AND obra_destino NOT ILIKE '%BACHEO%')
       OR obra_destino ILIKE '%LERMA%'
    GROUP BY obra_norm, mes
    ORDER BY obra_norm, mes;
""")
print("\n--- GASOLINA (VALES DE CAMPO / CONSUMOS) ---")
for r in cur.fetchall():
    print(dict(r))

conn.close()
