import sqlite3, pandas as pd
db = sqlite3.connect('c:/Users/JOSE/Desktop/Proyecto fenix/fenix.db')
df = pd.read_sql("SELECT folio, litros_totales, nota_leyenda FROM fenix_facturas_documentos WHERE tipo_combustible='Diesel'", db)
df['LTS'] = df['litros_totales'].round()
print(df[df['LTS'] == 200])

