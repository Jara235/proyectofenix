import pandas as pd
import sqlite3
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

db = sqlite3.connect('fenix_v2.db')
cursor = db.cursor()

# Clear existing week 26
cursor.execute('DELETE FROM gasolina_autorizaciones WHERE semana = 26')

hoy = datetime.now().strftime('%Y-%m-%d')
semana = 26
count = 0

for idx, row in df.iterrows():
    responsable = str(row['responsable']).strip() if pd.notna(row['responsable']) else 'DESCONOCIDO'
    obra = str(row['obra']).strip() if pd.notna(row['obra']) else 'Sin Obra'
    vehiculo = str(row['vehiculo']).strip()
    placa = str(row['placa']).strip() if pd.notna(row['placa']) else ''
    
    importe_val = row['importe']
    try:
        importe = float(importe_val)
        if math.isnan(importe):
            importe = 0.0
    except:
        importe = 0.0
        
    estatus = "autorizado" if importe > 0 else "en espera"
    
    # Generate folio
    count += 1
    folio = f"AUTH-GAS-26-{count:03d}"
    
    cursor.execute('''
        INSERT INTO gasolina_autorizaciones 
        (folio_conciliacion, fecha, semana, origen, obra_destino, vehiculo, placa, importe_autorizado, responsable, estatus_autorizacion)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (folio, hoy, semana, 'SEMANA 26.xlsx', obra, vehiculo, placa, importe, responsable, estatus))

db.commit()
print(f"Imported {count} authorizations into fenix_v2.db")
db.close()
