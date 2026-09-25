import pandas as pd
file_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\gasolina\SEMANA 26.xlsx'
df = pd.read_excel(file_path, sheet_name='SEMANA 26', header=None, nrows=5)
print('Row 0 (Dates):')
print(df.iloc[1].values.tolist()[:30])
print('Row 1 (Gas stations):')
print(df.iloc[2].values.tolist()[:30])
