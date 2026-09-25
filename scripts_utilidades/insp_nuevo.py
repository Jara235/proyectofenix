import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')
file_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_GASOLINA_NUEVO.xlsx'
xl = pd.ExcelFile(file_path)
print('Sheets in MAESTRO_CONTROL_GASOLINA_NUEVO:', xl.sheet_names)
for s in xl.sheet_names:
    df = xl.parse(s)
    print(f'\n--- {s} ---')
    print('Columns:', df.columns.tolist())
    print('Count:', len(df))
