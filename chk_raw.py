import pandas as pd
file_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\gasolina\SEMANA 26.xlsx'
df = pd.read_excel(file_path, sheet_name='SEMANA 26', skiprows=3)
df_auth = df.iloc[:, [1, 2, 3, 4, 5]].copy()
df_auth.columns = ['RESPONSABLE', 'CENTRO', 'UNIDAD', 'PLACAS', 'IMPORTE']
df_auth = df_auth.dropna(subset=['UNIDAD'])
df_auth = df_auth[df_auth['UNIDAD'] != 'UNIDAD / EQUIPO']
print('Total valid units:', len(df_auth))
print(df_auth[df_auth['PLACAS'].isna()][['UNIDAD', 'IMPORTE']])
