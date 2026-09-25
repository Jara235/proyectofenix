import sqlite3, pandas as pd

db = sqlite3.connect('c:/Users/JOSE/Desktop/Proyecto fenix/fenix_v2.db')

query = '''
WITH consumos AS (
    SELECT semana, fecha, SUM(litros) as litros_consumidos, SUM(importe_total) as importe_consumido
    FROM diesel_consumos
    GROUP BY semana, fecha
),
facturas AS (
    SELECT semana, fecha_factura as fecha, SUM(litros_facturados) as litros_facturados, SUM(importe_total) as importe_facturado
    FROM diesel_facturas
    GROUP BY semana, fecha_factura
)
SELECT 
    COALESCE(c.semana, f.semana) as semana,
    COALESCE(c.fecha, f.fecha) as fecha,
    COALESCE(c.litros_consumidos, 0) as litros_consumidos,
    COALESCE(c.importe_consumido, 0) as importe_consumido,
    COALESCE(f.litros_facturados, 0) as litros_facturados,
    COALESCE(f.importe_facturado, 0) as importe_facturado,
    COALESCE(f.litros_facturados, 0) - COALESCE(c.litros_consumidos, 0) as diferencia_litros,
    COALESCE(f.importe_facturado, 0) - COALESCE(c.importe_consumido, 0) as diferencia_importe
FROM consumos c
FULL OUTER JOIN facturas f ON c.fecha = f.fecha
ORDER BY semana, fecha;
'''

df = pd.read_sql_query(query, db)
df.to_excel('c:/Users/JOSE/Desktop/Proyecto fenix/REPORTE_CONCILIACION_DIESEL.xlsx', index=False)
print('Reporte generado exitosamente!')

