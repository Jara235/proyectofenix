import sqlite3
db = sqlite3.connect('c:/Users/JOSE/Desktop/Proyecto fenix/fenix_v2.db')
query = '''
SELECT 
    semana,
    SUM(CASE WHEN origen != 'FACTURA' THEN litros ELSE 0 END) as litros_consumidos,
    SUM(CASE WHEN origen != 'FACTURA' THEN importe_total ELSE 0 END) as importe_consumido,
    SUM(CASE WHEN origen == 'FACTURA' THEN litros ELSE 0 END) as litros_facturados,
    SUM(CASE WHEN origen == 'FACTURA' THEN importe_total ELSE 0 END) as importe_facturado
FROM diesel_consumos
GROUP BY semana
ORDER BY semana DESC
'''
res = db.execute(query).fetchall()
print(res)

