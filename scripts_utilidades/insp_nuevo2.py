import pandas as pd
file_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_GASOLINA_NUEVO.xlsx'
df = pd.read_excel(file_path, sheet_name='BD_AUTORIZACIONES')
print(df[['OBRA_DESTINO', 'VEHICULO', 'LITROS_AUTORIZADOS', 'IMPORTE_AUTORIZADO', 'ESTATUS_AUTORIZACION']].head(20).to_string())
