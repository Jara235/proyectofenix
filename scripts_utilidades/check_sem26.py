import pandas as pd, sqlite3

# Leer el archivo SEMANA 26
xl = pd.ExcelFile(r'c:\Users\JOSE\Desktop\Proyecto fenix\gasolina\SEMANA 26.xlsx')
print("Hojas:", xl.sheet_names)
for sh in xl.sheet_names:
    df = xl.parse(sh, header=None)
    print(f"\n=== {sh} ===")
    print(df.head(20).to_string())
