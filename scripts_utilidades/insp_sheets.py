import pandas as pd
maestro_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_GASOLINA_NUEVO.xlsx'
xl = pd.ExcelFile(maestro_path)
print("Sheets in Maestro Excel:")
for name in xl.sheet_names:
    print(f"- {name}")
