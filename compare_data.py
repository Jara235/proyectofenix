import openpyxl
import pandas as pd

wb = openpyxl.load_workbook('c:/Users/JOSE/Desktop/Proyecto fenix/MAESTRO_CONTROL_DIESEL_NUEVO.xlsx', data_only=True, read_only=True)

# BD_DIESEL
ws_d = wb['BD_DIESEL']
df_d = pd.DataFrame(ws_d.values)
headers = df_d.iloc[0]
df_d = df_d[1:]
df_d.columns = headers
df_d['LITROS'] = pd.to_numeric(df_d['LITROS'], errors='coerce').fillna(0)
df_d['IMPORTE_TOTAL'] = pd.to_numeric(df_d['IMPORTE_TOTAL'], errors='coerce').fillna(0)
print('--- BD_DIESEL TOTALS ---')
print('Litros:', df_d['LITROS'].sum())
print('Importe:', df_d['IMPORTE_TOTAL'].sum())

# BD_FACTURAS
ws_f = wb['BD_FACTURAS']
df_f = pd.DataFrame(ws_f.values)
headers = df_f.iloc[0]
df_f = df_f[1:]
df_f.columns = headers
df_f['LITROS_FACTURADOS'] = pd.to_numeric(df_f['LITROS_FACTURADOS'], errors='coerce').fillna(0)
df_f['IMPORTE_TOTAL'] = pd.to_numeric(df_f['IMPORTE_TOTAL'], errors='coerce').fillna(0)
print('--- BD_FACTURAS TOTALS ---')
print('Litros:', df_f['LITROS_FACTURADOS'].sum())
print('Importe:', df_f['IMPORTE_TOTAL'].sum())

