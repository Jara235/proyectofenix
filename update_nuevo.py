import pandas as pd
from openpyxl import load_workbook
import math
from datetime import datetime

file_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\gasolina\SEMANA 26.xlsx'
df = pd.read_excel(file_path, sheet_name='SEMANA 26', header=None, skiprows=3)

# Extract relevant columns
df = df.iloc[:, [1, 2, 3, 4, 5]]
df.columns = ['responsable', 'obra', 'vehiculo', 'placa', 'importe']

# Forward fill merged cells
df['responsable'] = df['responsable'].ffill()
df['obra'] = df['obra'].ffill()

# Drop rows where 'vehiculo' is null or just whitespace
df = df.dropna(subset=['vehiculo'])
df['vehiculo'] = df['vehiculo'].astype(str).str.strip()
df = df[df['vehiculo'] != 'nan']
df = df[df['vehiculo'] != '']
df = df[df['vehiculo'] != 'UNIDAD / EQUIPO']

hoy = datetime.now().strftime('%Y-%m-%d')
semana = 26

auth_data = []
cat_data = []

count = 0
for idx, row in df.iterrows():
    responsable = str(row['responsable']).strip() if pd.notna(row['responsable']) else 'DESCONOCIDO'
    obra = str(row['obra']).strip() if pd.notna(row['obra']) else 'Sin Obra'
    vehiculo = str(row['vehiculo']).strip()
    placa = str(row['placa']).strip() if pd.notna(row['placa']) else ''
    if placa.lower() == 'nan': placa = ''
    
    importe_val = row['importe']
    try:
        importe = float(importe_val)
        if math.isnan(importe):
            importe = 0.0
    except:
        importe = 0.0
        
    estatus = "AUTORIZADO" if importe > 0 else "EN ESPERA"
    
    count += 1
    folio = f"AUTH-GAS-26-{count:03d}"
    
    auth_data.append([
        folio, hoy, semana, 'SEMANA 26.xlsx', obra, vehiculo, placa, 0, importe, responsable, estatus, ''
    ])
    
    cat_data.append([
        obra, '', responsable, vehiculo, placa, '', 'Móvil', 'Gasolina'
    ])

# Remove duplicates from catalogs based on vehiculo and placa
df_cat = pd.DataFrame(cat_data, columns=['FRENTE DE TRABAJO', 'CODIGO_OBRA', 'RESPONSABLE DE FRENTE DE TRABAJO', 'VEHICULOS', 'PLACA', 'CONDUCTORES', 'TIPO_MOVIMIENTO', 'ORIGEN'])
df_cat = df_cat.drop_duplicates(subset=['VEHICULOS', 'PLACA'])

df_auth = pd.DataFrame(auth_data, columns=['FOLIO_CONCILIACION', 'FECHA', 'SEMANA', 'ORIGEN', 'OBRA_DESTINO', 'VEHICULO', 'PLACA', 'LITROS_AUTORIZADOS', 'IMPORTE_AUTORIZADO', 'RESPONSABLE', 'ESTATUS_AUTORIZACION', 'OBSERVACIONES'])

maestro_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_GASOLINA_NUEVO.xlsx'

with pd.ExcelWriter(maestro_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    df_cat.to_excel(writer, sheet_name='CATALOGOS', index=False)
    df_auth.to_excel(writer, sheet_name='BD_AUTORIZACIONES', index=False)

print(f"Updated MAESTRO_CONTROL_GASOLINA_NUEVO.xlsx with {len(df_auth)} auth rows and {len(df_cat)} cat rows.")
