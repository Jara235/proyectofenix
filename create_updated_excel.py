import pandas as pd
import sqlite3

db = sqlite3.connect('fenix.db')
cur = db.cursor()

tickets_interes = ['398820', '398474', '398454', '398197', '398196', '398189', '398173', '398160', '398294', '398068', '398052', '397296', '394749', '398202', '398182', '398179', '398175', '398161', '398456']

ticket_list = ','.join(["'" + t + "'" for t in tickets_interes])
cur.execute('SELECT ticket, litros, importe, placa, unidad, fecha FROM fenix_gas_tickets_reales WHERE ticket IN (' + ticket_list + ')')
rows = cur.fetchall()
db.close()

data = []
for r in rows:
    data.append({
        'Ticket': r[0],
        'Litros': r[1],
        'Importe (MXN)': r[2],
        'Placa en DB': r[3],
        'Unidad en DB': r[4],
        'Fecha Asignada': r[5]
    })

df = pd.DataFrame(data)
df.sort_values(by=['Placa en DB', 'Ticket'], inplace=True)

with pd.ExcelWriter('Resumen_Tickets_Perdidos_Actualizado.xlsx', engine='openpyxl') as writer:
    df.to_excel(writer, index=False)

print('Updated excel created')
