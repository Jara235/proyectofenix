import pandas as pd
from openpyxl import load_workbook
import math
from datetime import datetime

file_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\gasolina\SEMANA 26.xlsx'
df_raw = pd.read_excel(file_path, sheet_name='SEMANA 26', header=None)

semana = 26
count_by_table = []
current_count = 0

current_mode = None 
date_columns = []

i = 0
while i < len(df_raw):
    row = df_raw.iloc[i].tolist()
    val_0 = str(row[0]).strip()
    
    if 'RESONSABLE' in val_0 or 'RESPONSABLE' in val_0:
        if current_count > 0:
            count_by_table.append(current_count)
            current_count = 0
            
        sub_row = df_raw.iloc[i+1].tolist()
        if 'LITROS' in str(sub_row):
            current_mode = 'liters'
        else:
            current_mode = 'money'
            
        date_columns = []
        for col_idx in range(6, len(row)):
            d = row[col_idx]
            sub = str(sub_row[col_idx]).strip()
            if sub != 'nan' and sub != '':
                date_columns.append({'col_idx': col_idx, 'sub': sub})
        
        i += 2
        continue
        
    if val_0 == 'TOTALES':
        current_mode = None
        count_by_table.append(current_count)
        current_count = 0
        
    if current_mode is not None:
        vehiculo = str(row[3]).strip()
        
        # NOTE: Table 3 has no UNIDAD/EQUIPO (it has PLACAS in row[4])
        # If Table 3 is skipped because vehiculo is nan, that's a bug!
        if vehiculo == 'nan' or vehiculo == '':
            # Try to see if it's Table 3 or 4 which might use row[4] as primary
            if current_mode == 'money' and str(row[4]).strip() != 'nan':
                pass # Allow it!
            elif current_mode == 'liters':
                pass # Allow it
            else:
                i += 1
                continue
                
        if current_mode == 'money':
            for dc in date_columns:
                val = row[dc['col_idx']]
                try:
                    importe = float(val)
                    if not math.isnan(importe) and importe > 0:
                        current_count += 1
                except:
                    pass
                    
        elif current_mode == 'liters':
            for dc in date_columns:
                if dc['sub'] == 'LITROS':
                    val = row[dc['col_idx']]
                    try:
                        litros = float(val)
                        if not math.isnan(litros) and litros > 0:
                            current_count += 1
                    except:
                        pass
    i += 1

if current_count > 0:
    count_by_table.append(current_count)

print("Counts by table:", count_by_table)
