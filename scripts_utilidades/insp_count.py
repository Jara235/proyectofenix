import pandas as pd
maestro_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_GASOLINA_NUEVO.xlsx'
df = pd.read_excel(maestro_path, sheet_name='BD_FACTURAS')
print(f"Total rows in BD_FACTURAS: {len(df)}")
