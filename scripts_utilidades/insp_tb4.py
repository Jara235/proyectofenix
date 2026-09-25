import pandas as pd
file_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\gasolina\SEMANA 26.xlsx'
df = pd.read_excel(file_path, sheet_name='SEMANA 26', header=None, skiprows=64, nrows=5)
print('Table 4 title:', df.iloc[0, 0])
print('Row 1 (Dates):')
print(df.iloc[1].values.tolist()[:15])
print('Row 2 (Subheaders):')
print(df.iloc[2].values.tolist()[:15])
