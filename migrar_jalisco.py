import pandas as pd
import psycopg2
import math
import re

excel_file = 'c:/Users/JOSE/Desktop/Proyecto fenix/MAESTRO_CONTROL_DIESEL_NUEVO.xlsx'

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor()

def clean_semana(s):
    if pd.isna(s): return None
    if isinstance(s, (int, float)): return int(s)
    m = re.search(r'\d+', str(s))
    return int(m.group()) if m else None

print("Creando tabla de vales...")
cur.execute("""
    CREATE TABLE IF NOT EXISTS diesel.control_vales_jalisco (
        id SERIAL PRIMARY KEY,
        semana INTEGER NOT NULL UNIQUE,
        ajuste_semanal DECIMAL DEFAULT 0,
        creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
""")

print("Insertando catálogos...")
cur.execute("SELECT 1 FROM catalogos.obras WHERE nombre = 'BD_JALISCO'")
if not cur.fetchone():
    cur.execute("INSERT INTO catalogos.obras (nombre, codigo, responsable_default) VALUES ('BD_JALISCO', 'BDJAL', 'BRYAN')")

cur.execute("SELECT 1 FROM catalogos.operadores WHERE nombre = 'BRYAN'")
if not cur.fetchone():
    cur.execute("INSERT INTO catalogos.operadores (nombre) VALUES ('BRYAN')")

print("Leyendo Excel BD_JALISCO...")
df = pd.read_excel(excel_file, sheet_name='BD_JALISCO')

consumos_inserted = 0
ajustes_inserted = 0

ajustes_por_semana = {}

# Clean previous consumos for BD_JALISCO to avoid duplicates
cur.execute("DELETE FROM diesel.consumos WHERE obra_destino = 'BD_JALISCO'")

for index, row in df.iterrows():
    if pd.isna(row['Fecha']):
        continue
    
    fecha = pd.to_datetime(row['Fecha']).date()
    semana = clean_semana(row['Semana'])
    
    if not semana:
        continue
        
    salida_l = row['Salida (L)']
    importe = row['Importe']
    equipo = str(row['Equipo']) if not pd.isna(row['Equipo']) else None
    eco = str(row['Económico']) if not pd.isna(row['Económico']) else None
    
    if pd.notna(row['Ajuste']) and float(row['Ajuste']) > 0:
        ajustes_por_semana[semana] = ajustes_por_semana.get(semana, 0) + float(row['Ajuste'])
        
    if pd.notna(salida_l) and float(salida_l) > 0:
        litros = float(salida_l)
        imp = float(importe) if pd.notna(importe) else 0.0
        
        folio = f"JAL-S{semana}-{index}"
        cur.execute("""
            INSERT INTO diesel.consumos 
            (fecha, semana, obra_destino, equipo, litros, importe_total, estatus_revision, folio_conciliacion)
            VALUES (%s, %s, %s, %s, %s, %s, 'APROBADO', %s)
        """, (fecha, semana, 'BD_JALISCO', equipo or eco, litros, imp, folio))
        consumos_inserted += 1

print("Insertando ajustes...")
for sem, ajuste in ajustes_por_semana.items():
    cur.execute("""
        INSERT INTO diesel.control_vales_jalisco (semana, ajuste_semanal)
        VALUES (%s, %s)
        ON CONFLICT (semana) DO UPDATE SET ajuste_semanal = EXCLUDED.ajuste_semanal
    """, (sem, ajuste))
    ajustes_inserted += 1

conn.commit()
cur.close()
conn.close()

print(f"Migración completada. Consumos insertados: {consumos_inserted}. Ajustes insertados: {ajustes_inserted}")
