import pandas as pd
df = pd.read_excel('c:/Users/JOSE/Desktop/Proyecto fenix/MAESTRO_CONTROL_DIESEL_NUEVO.xlsx', sheet_name='CATALOGOS')
print(df['OPERADORES'].dropna().head(10))

