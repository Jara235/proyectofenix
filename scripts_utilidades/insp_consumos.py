import pandas as pd
file_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_GASOLINA_NUEVO.xlsx'
df = pd.read_excel(file_path, sheet_name='BD_GASOLINA')
print(df[['FECHA', 'ORIGEN', 'OBRA_DESTINO', 'VEHICULO', 'IMPORTE_TOTAL']].head(20).to_string())
