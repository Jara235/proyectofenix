import openpyxl, pandas as pd
wb = openpyxl.load_workbook('c:/Users/JOSE/Desktop/Proyecto fenix/MAESTRO_CONTROL_DIESEL_NUEVO.xlsx', data_only=True, read_only=True)
ws = wb['CATALOGOS']
df = pd.DataFrame(ws.values)
print(df.head(5))

