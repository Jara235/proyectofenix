import pandas as pd

# Revisar el JDJ PROVISIONAL que tiene las cargas reales por gasolinera
df_jdj = pd.read_excel(r'c:\Users\JOSE\Desktop\Proyecto fenix\gasolina\CONTROL JDJ PROVISIONAL.xlsx', sheet_name='JUNIO 2026', header=None)
print("=== CONTROL JDJ PROVISIONAL ===")
print("Shape:", df_jdj.shape)
print(df_jdj.head(30).to_string())
