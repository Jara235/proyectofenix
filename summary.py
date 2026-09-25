import sqlite3, pandas as pd
db = sqlite3.connect('c:/Users/JOSE/Desktop/Proyecto fenix/fenix.db')
df = pd.read_sql('SELECT folio, tipo_combustible, fecha_emision, litros_totales, total FROM fenix_facturas_documentos', db)
print('--- GASOLINA ---')
print(df[df['tipo_combustible'] == 'Gasolina'][['folio', 'fecha_emision', 'litros_totales', 'total']].to_string(index=False))
print('--- DIESEL ---')
print(len(df[df['tipo_combustible'] == 'Diesel']))
db.close()

