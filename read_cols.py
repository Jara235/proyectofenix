import pandas as pd
import openpyxl

excel_path = 'c:/Users/JOSE/Desktop/Proyecto fenix/MAESTRO_CONTROL_DIESEL_NUEVO.xlsx'

df = pd.read_excel(excel_path, sheet_name='BD_DIESEL')
print(df.columns.tolist())

