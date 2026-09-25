import pandas as pd
excel_path = 'c:/Users/JOSE/Desktop/Proyecto fenix/MAESTRO_CONTROL_DIESEL_NUEVO.xlsx'
try:
    df = pd.read_excel(excel_path, sheet_name='TABLAS_DINAMICAS', header=None)
    print(df.head(20).to_string())
except Exception as e:
    print(e)

