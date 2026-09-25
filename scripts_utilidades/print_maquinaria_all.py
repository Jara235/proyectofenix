import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 1000)

df = pd.read_excel('c:/Users/JOSE/Desktop/Proyecto fenix/MAQUINARÍA 2026.xlsx', engine='calamine')
print(df)
