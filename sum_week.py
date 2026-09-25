import sqlite3
import pandas as pd
db = sqlite3.connect('c:/Users/JOSE/Desktop/Proyecto fenix/fenix.db')
df = pd.read_sql("SELECT folio, fecha_emision, litros_totales, total, semana, destino_suministro FROM fenix_facturas_documentos WHERE tipo_combustible='Diesel' AND semana=26", db)
print('--- DIESEL SEMANA 26 ---')
print(df.to_string())
print('Total Lts:', df['litros_totales'].sum())
print('Total MXN:', df['total'].sum())
db.close()

