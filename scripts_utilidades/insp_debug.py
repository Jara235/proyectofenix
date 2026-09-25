import pandas as pd
file_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\gasolina\SEMANA 26.xlsx'
df_raw = pd.read_excel(file_path, sheet_name='SEMANA 26', header=None)

print("Table 2 rows:")
for i in range(37, 48):
    print(df_raw.iloc[i].tolist()[:10])
    
print("\nTable 3 rows:")
for i in range(51, 62):
    print(df_raw.iloc[i].tolist()[:10])
