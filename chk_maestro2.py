import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')
file_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\gasolina\Maestro_Conciliacion_Gasolina.xlsx'
df = pd.read_excel(file_path, sheet_name='autorizaciones por unidad')
print(f'Total rows in autorizaciones: {len(df)}')
for idx, row in df.iterrows():
    print(f"{row.get('UNIDAD / EQUIPO', '')[:15]:<15} | Importe: {row.get('IMPORTE SEMANAL AUTORIZADO', 0)}")
