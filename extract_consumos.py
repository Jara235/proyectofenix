import pandas as pd
from openpyxl import load_workbook
import math
from datetime import datetime

file_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\gasolina\SEMANA 26.xlsx'
df_raw = pd.read_excel(file_path, sheet_name='SEMANA 26', header=None)

# Extract dates from row 1 (index 1)
row_dates = df_raw.iloc[1].tolist()
# Extract stations from row 2 (index 2)
row_stations = df_raw.iloc[2].tolist()

# Define the date columns
date_columns = []
current_date = None
for i in range(6, 24):
    d = row_dates[i]
    if pd.notna(d) and isinstance(d, datetime):
        current_date = d.strftime('%Y-%m-%d')
    station = str(row_stations[i]).strip()
    date_columns.append({'col_idx': i, 'date': current_date, 'station': station})

# Data rows start at index 3
df = df_raw.iloc[3:].copy()
# Reset columns for easier access to the first few
df_meta = df.iloc[:, [1, 2, 3, 4]]
df_meta.columns = ['responsable', 'obra', 'vehiculo', 'placa']
df_meta['responsable'] = df_meta['responsable'].ffill()
df_meta['obra'] = df_meta['obra'].ffill()

semana = 26
consumos_data = []
count = 0

for i in range(len(df)):
    row_meta = df_meta.iloc[i]
    vehiculo = str(row_meta['vehiculo']).strip()
    if vehiculo == 'nan' or vehiculo == '' or vehiculo == 'UNIDAD / EQUIPO':
        continue
    
    obra = str(row_meta['obra']).strip() if pd.notna(row_meta['obra']) else 'Sin Obra'
    placa = str(row_meta['placa']).strip() if pd.notna(row_meta['placa']) else ''
    if placa.lower() == 'nan': placa = ''
    
    # Check consumptions
    for dc in date_columns:
        val = df.iloc[i, dc['col_idx']]
        try:
            importe = float(val)
            if math.isnan(importe) or importe <= 0:
                continue
        except:
            continue
            
        count += 1
        folio = f"CONS-GAS-26-{count:03d}"
        
        consumos_data.append({
            'FOLIO_CONCILIACION': folio,
            'FECHA': dc['date'],
            'SEMANA': semana,
            'ORIGEN': dc['station'],
            'TIPO_MOVIMIENTO': 'Consumo',
            'OBRA_DESTINO': obra,
            'VEHICULO': vehiculo,
            'PLACA': placa,
            'KILOMETRAJE': 0,
            'LITROS': 0,
            'COSTO_POR_LITRO': 0,
            'IMPORTE_TOTAL': importe,
            'CONDUCTOR': '',
            'ESTATUS_CONCILIACION': 'EN ESPERA',
            'OBSERVACIONES': ''
        })

df_consumos = pd.DataFrame(consumos_data)

maestro_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_GASOLINA_NUEVO.xlsx'
with pd.ExcelWriter(maestro_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    df_consumos.to_excel(writer, sheet_name='BD_GASOLINA', index=False)

print(f"Extracted {len(df_consumos)} consumptions into BD_GASOLINA")
