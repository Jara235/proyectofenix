import pandas as pd
maestro_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_GASOLINA_NUEVO.xlsx'

df_auth = pd.read_excel(maestro_path, sheet_name='BD_AUTORIZACIONES')
df_gas = pd.read_excel(maestro_path, sheet_name='BD_GASOLINA')

print("BD_AUTORIZACIONES columns:")
print(list(df_auth.columns))
print("BD_GASOLINA columns:")
print(list(df_gas.columns))
