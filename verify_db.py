import sqlite3
conn = sqlite3.connect('fenix.db')
cur = conn.cursor()
tipo = 'CONSUMO'
cur.execute('SELECT tipo_combustible, COUNT(*), ROUND(SUM(litros),1) FROM fenix_movimientos_combustible WHERE tipo_movimiento=? GROUP BY tipo_combustible', (tipo,))
print('Consumos por tipo:')
for r in cur.fetchall(): print(f'  {r[0]}: {r[1]} registros, {r[2]} litros')
cur.execute('SELECT estatus_validacion, COUNT(*), ROUND(SUM(litros_totales),1) FROM fenix_facturas_documentos GROUP BY estatus_validacion')
print('\nFacturas documentales:')
for r in cur.fetchall(): print(f'  {r[0]}: {r[1]} facturas, {r[2]} litros')
conn.close()
print('\nOK - Base de datos lista')
