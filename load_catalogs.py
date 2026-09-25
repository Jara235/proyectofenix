import sqlite3, openpyxl, pandas as pd

wb = openpyxl.load_workbook('c:/Users/JOSE/Desktop/Proyecto fenix/MAESTRO_CONTROL_DIESEL_NUEVO.xlsx', data_only=True, read_only=True)
ws = wb['CATALOGOS']
df = pd.DataFrame(ws.values)
headers = df.iloc[0]
df = df[1:]
df.columns = headers

db = sqlite3.connect('c:/Users/JOSE/Desktop/Proyecto fenix/fenix_v2.db')
c = db.cursor()

# OBRAS
obras = df['OBRAS'].dropna().unique()
for o in obras:
    c.execute('INSERT OR IGNORE INTO catalogos_obras (codigo, nombre) VALUES (?, ?)', (str(o)[:5].upper(), str(o).strip()))

# EQUIPOS Y NUMEROS ECONOMICOS
for _, row in df.iterrows():
    equipo = str(row.get('EQUIPOS', '')).strip()
    eco = str(row.get('NUMEROS ECONOMICOS', '')).strip()
    if eco and eco != 'nan' and eco != 'None':
        c.execute('INSERT OR IGNORE INTO catalogos_equipos (numero_economico, descripcion, tipo_equipo) VALUES (?, ?, ?)', (eco, equipo, 'Maquinaria'))

# OPERADORES
operadores = df['OPERADORES'].dropna().unique()
for op in operadores:
    c.execute('INSERT OR IGNORE INTO catalogos_operadores (nombre) VALUES (?)', (str(op).strip(),))

# RESPONSABLES (Can be placed in a new table or just kept for reference, but let's just create a catalogos_responsables if needed, 
# wait, the DB schema has responsable as TEXT, maybe we should create catalogos_responsables)
# I'll add catalogos_responsables just in case
c.execute('CREATE TABLE IF NOT EXISTS catalogos_responsables (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL)')
resp = df['RESPONSABLE'].dropna().unique()
for r in resp:
    c.execute('INSERT OR IGNORE INTO catalogos_responsables (nombre) VALUES (?)', (str(r).strip(),))

db.commit()
db.close()
print('Catálogos extraídos y guardados en la BD.')

