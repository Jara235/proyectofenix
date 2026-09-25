import sqlite3
import json
import pandas as pd
import datetime

with open('extracted_pdf_tickets.json', 'r') as f:
    tickets = json.load(f)
    
db = sqlite3.connect('fenix.db')
cur = db.cursor()
cur.execute('SELECT ticket FROM fenix_gas_tickets_reales')
existing = {r[0] for r in cur.fetchall()}
missing_tickets = [t for t in tickets if t['ticket'] not in existing]

df = pd.read_excel('gasolina/SEMANA 26 (1).xlsx', header=None)
levet_cols = [i for i, val in enumerate(df.iloc[2].tolist()) if str(val).strip().upper() == 'LEVET']

m_deductions = []
for row_idx in range(4, len(df)):
    row = df.iloc[row_idx]
    placa = row[4]; conductor = row[0]; obra = row[6]; unidad = row[3]
    if pd.isna(placa): continue
    for c in levet_cols:
        val = row[c]
        if pd.notna(val) and isinstance(val, (int, float)) and val > 0:
            fecha = '2026-06-30'
            for offset in [0, 1, 2, 3]:
                if c-offset >= 0 and isinstance(df.iloc[1][c-offset], datetime.datetime):
                    fecha = df.iloc[1][c-offset].strftime('%Y-%m-%d')
                    break
            m_deductions.append({
                'monto': float(val), 'placa': str(placa).strip(), 'fecha': fecha,
                'conductor': str(conductor).strip() if pd.notna(conductor) else 'DESCONOCIDO',
                'obra': str(obra).strip() if pd.notna(obra) else 'DESCONOCIDA',
                'unidad': str(unidad).strip() if pd.notna(unidad) else 'DESCONOCIDA'
            })

inserted = 0
for t in missing_tickets:
    # Try exact match by monto (+- 2 pesos for rounding)
    matches = [d for d in m_deductions if abs(d['monto'] - t['total']) <= 2.0]
    if matches:
        match = matches[0]
        m_deductions.remove(match) # consume it
        placa = match['placa']; fecha = match['fecha']; conductor = match['conductor']; obra = match['obra']; unidad = match['unidad']
    else:
        placa = 'NO REPORTADA'; fecha = '2026-06-30'; conductor = 'DESCONOCIDO'; obra = 'DESCONOCIDA'; unidad = 'DESCONOCIDA'
        
    cur.execute('''INSERT INTO fenix_gas_tickets_reales (
                    folio, ticket, fecha, semana, placa, conductor, responsable, obra, unidad, litros, precio_litro, importe, gasolinera
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                   (f"FACT-LEVET-{t['ticket']}", t['ticket'], fecha, 26, placa, conductor, conductor, obra, unidad, t['litros'], round(t['total']/t['litros'], 2), t['total'], 'LEVET'))
    inserted += 1

db.commit()
print(f'Inserted {inserted} missing tickets from the PDF invoice.')
db.close()
