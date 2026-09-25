import pandas as pd
file_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\gasolina\SEMANA 26.xlsx'
df = pd.read_excel(file_path, sheet_name='SEMANA 26', header=None, skiprows=66, nrows=6)
print(df.iloc[:, [1,2,3,4,6]].to_string())
