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

current_mode = None # 'money' for tables 1,2,3; 'liters' for table 4
date_columns = []
last_responsable = ''
last_obra = ''

# Parse row by row
i = 0
while i < len(df_raw):
    row = df_raw.iloc[i].tolist()
    val_0 = str(row[0]).strip()
    
    if 'RESONSABLE' in val_0 or 'RESPONSABLE' in val_0:
        # We found a header row
        # Determine mode by looking at the sub-headers in the next row (i+1)
        sub_row = df_raw.iloc[i+1].tolist()
        if 'LITROS' in str(sub_row):
            current_mode = 'liters'
        else:
            current_mode = 'money'
            
        # Parse dates
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
        
        i += 2 # Skip header and sub-header
        continue
        
    if val_0 == 'TOTALES':
        current_mode = None
        
    # If we are inside a table block
    if current_mode is not None:
        if val_0 != 'nan' and val_0 != '':
            last_responsable = val_0
            
        obra_val = str(row[2]).strip()
        if obra_val != 'nan' and obra_val != '':
            last_obra = obra_val
            
        vehiculo = str(row[3]).strip()
        if vehiculo != 'nan' and vehiculo != '' and vehiculo != 'UNIDAD / EQUIPO':
            placa = str(row[4]).strip()
            if placa.lower() == 'nan': placa = ''
            
            # Process consumptions based on mode
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
                            'CONDUCTOR': '',
                            'ESTATUS_CONCILIACION': 'EN ESPERA',
                            'OBSERVACIONES': ''
                        })
                    except:
                        pass
                        
            elif current_mode == 'liters':
                # Group subheaders by date to find LITROS and #FACTURA pairs
                # or just iterate through date_columns and if it's LITROS, look ahead for #FACTURA
                for idx_dc, dc in enumerate(date_columns):
                    if dc['sub'] == 'LITROS':
                        val = row[dc['col_idx']]
                        try:
                            litros = float(val)
                            if math.isnan(litros) or litros <= 0:
                                continue
                            
                            # Find factura in the next column if exists
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
                                'CONDUCTOR': '',
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
