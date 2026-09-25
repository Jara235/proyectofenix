import pandas as pd
excel_path = 'c:/Users/JOSE/Desktop/Proyecto fenix/MAESTRO_CONTROL_DIESEL_NUEVO.xlsx'
try:
    df = pd.read_excel(excel_path, sheet_name='BD_DIESEL')
    print(f'Excel OK. Rows: {len(df)}')
except Exception as e:
    print(f'Error: {e}')

