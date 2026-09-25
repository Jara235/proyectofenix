import pandas as pd
excel_path = 'c:/Users/JOSE/Desktop/Proyecto fenix/MAESTRO_CONTROL_DIESEL_NUEVO.xlsx'
print(pd.ExcelFile(excel_path).sheet_names)

