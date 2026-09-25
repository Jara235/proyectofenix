import pandas as pd
from openpyxl import load_workbook
import math
from datetime import datetime

file_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\gasolina\SEMANA 26.xlsx'
df_raw = pd.read_excel(file_path, sheet_name='SEMANA 26', header=None)

semana = 26
consumos_data = []
count = 0
hoy = datetime.now().strftime('%Y-%m-%d')

current_mode = None 
date_columns = []
last_responsable = 'DESCONOCIDO'
last_obra = 'Sin Obra'

i = 0
while i < len(df_raw):
    row = df_raw.iloc[i].tolist()
    val_0 = str(row[0]).strip()
    
    if 'RESONSABLE' in val_0 or 'RESPONSABLE' in val_0:
        sub_row = df_raw.iloc[i+1].tolist()
        
        # Determine mode
        if 'LITROS' in str(sub_row):
            current_mode = 'liters'
        else:
            current_mode = 'money'
            
        date_columns = []
        current_date = None
        for col_idx in range(6, len(row)):
            d = row[col_idx]
            if pd.notna(d) and isinstance(d, datetime):
                current_date = d.strftime('%Y-%m-%d')
            
            sub = str(sub_row[col_idx]).strip()
            if sub != 'nan' and sub != '':
                date_columns.append({
                    'col_idx': col_idx,
                    'date': current_date,
                    'sub': sub
                })
        
        i += 2
        continue
        
    if val_0 == 'TOTALES':
        current_mode = None
        
    if current_mode is not None:
        if val_0 != 'nan' and val_0 != '' and val_0 != 'nan':
            # It's an index or name, but sometimes responsible is in col 1
            pass
            
        resp_val = str(row[1]).strip()
        if resp_val != 'nan' and resp_val != '':
            last_responsable = resp_val
            
        obra_val = str(row[2]).strip()
        if obra_val != 'nan' and obra_val != '':
            last_obra = obra_val
            
        vehiculo = str(row[3]).strip()
        placa = str(row[4]).strip()
        
        if vehiculo.lower() == 'nan': vehiculo = ''
        if placa.lower() == 'nan': placa = ''
        
        if vehiculo == '' and placa == '' and str(row[1]).strip() == 'nan' and str(row[2]).strip() == 'nan':
            # Truly empty row
            i += 1
            continue
            
        if vehiculo == '':
            vehiculo = 'S/P'
            
        # Extract data
        if current_mode == 'money':
            for dc in date_columns:
                val = row[dc['col_idx']]
                try:
                    importe = float(val)
                    if math.isnan(importe) or importe <= 0:
                        continue
                    
                    count += 1
                    folio = f"CONS-GAS-26-{count:03d}"
                    
                    consumos_data.append({
                        'FOLIO_CONCILIACION': folio,
                        'FECHA': dc['date'],
                        'SEMANA': semana,
                        'ORIGEN': dc['sub'],
                        'TIPO_MOVIMIENTO': 'Consumo',
                        'OBRA_DESTINO': last_obra,
                        'VEHICULO': vehiculo,
                        'PLACA': placa,
                        'KILOMETRAJE': 0,
                        'LITROS': 0,
                        'COSTO_POR_LITRO': 0,
                        'IMPORTE_TOTAL': importe,
                        'CONDUCTOR': last_responsable,
                        'ESTATUS_CONCILIACION': 'EN ESPERA',
                        'OBSERVACIONES': ''
                    })
                except:
                    pass
                    
        elif current_mode == 'liters':
            for idx_dc, dc in enumerate(date_columns):
                if dc['sub'] == 'LITROS':
                    val = row[dc['col_idx']]
                    try:
                        litros = float(val)
                        if math.isnan(litros) or litros <= 0:
                            continue
                        
                        factura = ''
                        if idx_dc + 1 < len(date_columns) and 'FACTURA' in date_columns[idx_dc+1]['sub']:
                            fact_val = str(row[date_columns[idx_dc+1]['col_idx']]).strip()
                            if fact_val != 'nan':
                                factura = f"Factura: {fact_val}"
                        
                        count += 1
                        folio = f"CONS-GAS-26-{count:03d}"
                        
                        consumos_data.append({
                            'FOLIO_CONCILIACION': folio,
                            'FECHA': dc['date'],
                            'SEMANA': semana,
                            'ORIGEN': 'MOBILE HUIXQUILUCAN',
                            'TIPO_MOVIMIENTO': 'Consumo',
                            'OBRA_DESTINO': last_obra,
                            'VEHICULO': vehiculo,
                            'PLACA': placa,
                            'KILOMETRAJE': 0,
                            'LITROS': litros,
                            'COSTO_POR_LITRO': 0,
                            'IMPORTE_TOTAL': 0,
                            'CONDUCTOR': last_responsable,
                            'ESTATUS_CONCILIACION': 'EN ESPERA',
                            'OBSERVACIONES': factura
                        })
                    except:
                        pass
    i += 1

df_consumos = pd.DataFrame(consumos_data)

maestro_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_GASOLINA_NUEVO.xlsx'
with pd.ExcelWriter(maestro_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    df_consumos.to_excel(writer, sheet_name='BD_GASOLINA', index=False)

print(f"Extracted {len(df_consumos)} consumptions into BD_GASOLINA from all tables.")
