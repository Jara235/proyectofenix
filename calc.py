import sqlite3, pandas as pd
db = sqlite3.connect('c:/Users/JOSE/Desktop/Proyecto fenix/fenix.db')
df = pd.read_sql("SELECT folio, destino_suministro, fecha_emision, total FROM fenix_facturas_documentos WHERE tipo_combustible='Diesel' AND (semana=26 OR fecha_emision LIKE '2026-06-22%' OR fecha_emision LIKE '2026-06-23%' OR fecha_emision LIKE '2026-06-24%' OR fecha_emision LIKE '2026-06-25%' OR fecha_emision LIKE '2026-06-26%' OR fecha_emision LIKE '2026-06-27%' OR fecha_emision LIKE '2026-06-28%')", db)
print(df)
print('Total:', df['total'].sum())

