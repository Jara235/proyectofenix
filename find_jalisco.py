import os
import pandas as pd

directory = "c:\\Users\\JOSE\\Desktop\\Proyecto fenix"
for root, dirs, files in os.walk(directory):
    for file in files:
        if file.endswith('.xlsx'):
            path = os.path.join(root, file)
            try:
                xl = pd.ExcelFile(path, engine='calamine')
                if 'BD_Jalisco' in xl.sheet_names:
                    print(f"FOUND IN: {path}")
            except Exception as e:
                pass
