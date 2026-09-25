import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')
file_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\gasolina\Maestro_Conciliacion_Gasolina.xlsx'
df = pd.read_excel(file_path, sheet_name='autorizaciones por unidad')
print(f'Total rows in autorizaciones: {len(df)}')
count_minor = 0
for idx, row in df.iterrows():
    if 'EQUIPO MENOR' in str(row.get('UNIDAD / EQUIPO', '')) or 'MOTOR' in str(row.get('UNIDAD / EQUIPO', '')):
        print(f"Obra: {row.get('CENTRO DE TRABAJO', '')[:20]:<20} | Vehiculo: {row.get('UNIDAD / EQUIPO', '')[:30]:<30} | Importe: {row.get('IMPORTE SEMANAL AUTORIZADO', 0)}")
        count_minor += 1
print(f'Total minor equipment rows: {count_minor}')
