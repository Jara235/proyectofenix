import pandas as pd
import json
import datetime
import sqlite3

# Load missing tickets
with open('extracted_pdf_tickets.json', 'r') as f:
    tickets = json.load(f)
db = sqlite3.connect('fenix.db')
cur = db.cursor()
cur.execute('SELECT ticket FROM fenix_gas_tickets_reales')
existing = {r[0] for r in cur.fetchall()}
missing_tickets = [t for t in tickets if t['ticket'] not in existing]

# Load Matriz
df = pd.read_excel('gasolina/SEMANA 26 (1).xlsx', header=None)

# Find all 'LEVET' columns
levet_cols = []
for i, val in enumerate(df.iloc[2].tolist()):
    if str(val).strip().upper() == 'LEVET':
        levet_cols.append(i)

matriz_deductions = []
for row_idx in range(4, len(df)):
    row = df.iloc[row_idx]
    placa = row[4]
    conductor = row[0]
    obra = row[6]
    unidad = row[3]
    if pd.isna(placa): continue
    for c in levet_cols:
        val = row[c]
        if pd.notna(val) and isinstance(val, (int, float)) and val > 0:
            fecha = None
            for offset in [0, 1, 2, 3]:
                if c-offset >= 0:
                    pot_fecha = df.iloc[1][c-offset]
                    if isinstance(pot_fecha, datetime.datetime):
                        fecha = pot_fecha.strftime('%Y-%m-%d')
                        break
            matriz_deductions.append({
                'monto': float(val), 
                'placa': str(placa).strip(), 
                'fecha': fecha,
                'conductor': str(conductor).strip() if pd.notna(conductor) else '',
                'obra': str(obra).strip() if pd.notna(obra) else '',
                'unidad': str(unidad).strip() if pd.notna(unidad) else ''
            })

print(f'Found {len(matriz_deductions)} LEVET deductions in Matriz')

matched_tickets = []
for t in missing_tickets:
    matches = [d for d in matriz_deductions if abs(d['monto'] - t['total']) < 1.0]
    if len(matches) == 1:
        match = matches[0]
        # Remove from matriz_deductions to avoid double matching
        matriz_deductions.remove(match)
        # Prepare for DB
        matched_tickets.append({
            'ticket': t['ticket'],
            'fecha': match['fecha'],
            'placa': match['placa'],
            'conductor': match['conductor'],
            'obra': match['obra'],
            'unidad': match['unidad'],
            'litros': t['litros'],
            'importe': t['total'],
            'gasolinera': 'LEVET'
        })
    elif len(matches) > 1:
        print(f"Ticket {t['ticket']} - Total: {t['total']} has MULTIPLE matches")
    else:
        print(f"Ticket {t['ticket']} - Total: {t['total']} has NO matches")

print(f'Total perfectly matched: {len(matched_tickets)} / {len(missing_tickets)}')

# Insert into DB
inserted = 0
for t in matched_tickets:
    cur.execute('''INSERT INTO fenix_gas_tickets_reales (
                    folio, ticket, fecha, semana, placa, conductor, responsable, obra, unidad, litros, precio_litro, importe, gasolinera
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                   (f"FACT-LEVET-{t['ticket']}", t['ticket'], t['fecha'], 26, t['placa'], t['conductor'], t['conductor'], t['obra'], t['unidad'], t['litros'], round(t['importe']/t['litros'], 2), t['importe'], t['gasolinera']))
    inserted += 1

db.commit()
print(f'Successfully inserted {inserted} new tickets into fenix_gas_tickets_reales')
db.close()
