import pandas as pd
file_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_GASOLINA_NUEVO.xlsx'
df = pd.read_excel(file_path, sheet_name='BD_AUTORIZACIONES')
print(f'Total rows in BD_AUTORIZACIONES: {len(df)}')
count_minor = 0
for idx, row in df.iterrows():
    if 'EQUIPO MENOR' in str(row.get('VEHICULO', '')) or 'MOTOR' in str(row.get('VEHICULO', '')):
        print(f"Obra: {row.get('OBRA_DESTINO', '')[:20]:<20} | Vehiculo: {row.get('VEHICULO', '')[:30]:<30} | Importe: {row.get('IMPORTE_AUTORIZADO', 0)}")
        count_minor += 1
print(f'Total minor equipment rows: {count_minor}')
