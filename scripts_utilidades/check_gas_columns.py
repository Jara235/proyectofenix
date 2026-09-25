import pandas as pd
print('--- CATALOGOS ---')
df1 = pd.read_excel('c:/Users/JOSE/Desktop/Proyecto fenix/MAESTRO_CONTROL_GASOLINA_NUEVO.xlsx', sheet_name='CATALOGOS')
print(df1.columns.tolist())
print('--- BD_AUTORIZACIONES ---')
df2 = pd.read_excel('c:/Users/JOSE/Desktop/Proyecto fenix/MAESTRO_CONTROL_GASOLINA_NUEVO.xlsx', sheet_name='BD_AUTORIZACIONES')
print(df2.columns.tolist())

