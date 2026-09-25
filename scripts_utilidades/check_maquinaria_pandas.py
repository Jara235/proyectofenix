import pandas as pd

try:
    df = pd.read_excel('c:/Users/JOSE/Desktop/Proyecto fenix/MAQUINARÍA 2026.xlsx', engine='calamine')
    print("Read with calamine:")
    print(df.head(20))
except Exception as e:
    print("Calamine failed:", e)
    try:
        df = pd.read_excel('c:/Users/JOSE/Desktop/Proyecto fenix/MAQUINARÍA 2026.xlsx')
        print(df.head(20))
    except Exception as e2:
        print("Default engine failed:", e2)
