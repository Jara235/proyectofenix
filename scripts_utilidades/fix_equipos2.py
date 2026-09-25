import sqlite3, openpyxl, pandas as pd

wb = openpyxl.load_workbook('c:/Users/JOSE/Desktop/Proyecto fenix/MAESTRO_CONTROL_DIESEL_NUEVO.xlsx', data_only=True, read_only=True)
ws = wb['CATALOGOS']
df = pd.DataFrame(ws.values)
headers = df.iloc[0]
df = df[1:]
df.columns = headers

db = sqlite3.connect('c:/Users/JOSE/Desktop/Proyecto fenix/fenix_v2.db')
c = db.cursor()

c.execute('DELETE FROM catalogos_equipos')

operadores = df['OPERADORES'].dropna().tolist()

for index, row in df.iterrows():
    equipo = str(row.get('EQUIPOS', '')).strip()
    eco = str(row.get('NUMERO_ECONOMICO', '')).strip()
    
    if equipo == 'None' or equipo == 'nan': equipo = ''
    if eco == 'None' or eco == 'nan': eco = ''
    
    # Use the same row index for operators as a default fallback
    op = operadores[index-1] if (index-1) < len(operadores) else (operadores[0] if operadores else '')
    
    if eco:
        c.execute('INSERT OR IGNORE INTO catalogos_equipos (numero_economico, descripcion, tipo_equipo, operador_default) VALUES (?, ?, ?, ?)', (eco, equipo, 'Maquinaria', str(op).strip()))
    elif equipo:
        eco_generado = equipo[:3].upper() + '-NA-' + str(index)
        c.execute('INSERT OR IGNORE INTO catalogos_equipos (numero_economico, descripcion, tipo_equipo, operador_default) VALUES (?, ?, ?, ?)', (eco_generado, equipo, 'Maquinaria', str(op).strip()))

db.commit()
db.close()
print('Maquinaria recargada correctamente fila por fila.')

