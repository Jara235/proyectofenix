import sqlite3, pandas as pd
db = sqlite3.connect('c:/Users/JOSE/Desktop/Proyecto fenix/fenix.db')
df = pd.read_sql("SELECT folio, fecha_emision, litros_totales, total FROM fenix_facturas_documentos WHERE folio IN ('10148', '10198', '10211', '10216', '10226', '10270', '10271', '10320')", db)
print(df)
print('Total Lts:', df['litros_totales'].sum())
print('Total MXN:', df['total'].sum())

