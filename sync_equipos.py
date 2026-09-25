import pandas as pd
import psycopg2

MAESTRO_PATH = r"c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_DIESEL_NUEVO.xlsx"

print("Leyendo Excel...")
df = pd.read_excel(MAESTRO_PATH, sheet_name="CATALOGOS")

# Las columnas son D (EQUIPOS) y E (NUMERO_ECONOMICO)
# En pandas, D es index 3, E es index 4 si A=0. O podemos usar los nombres de las columnas.
# Imprimimos las columnas para asegurar
print("Columnas en CATALOGOS:", df.columns.tolist())

# Filtrar vacios
equipos_df = df[['EQUIPOS', 'NUMERO_ECONOMICO']].dropna(subset=['EQUIPOS'])

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor()

print("Conectado a PostgreSQL. Sincronizando equipos...")

# Leer existentes
cur.execute("SELECT descripcion FROM catalogos.equipos")
existentes = set(r[0].strip().upper() for r in cur.fetchall())

nuevos = 0
for idx, row in equipos_df.iterrows():
    equipo = str(row['EQUIPOS']).strip()
    num_eco = str(row['NUMERO_ECONOMICO']).strip() if pd.notnull(row['NUMERO_ECONOMICO']) else ""
    
    # Combinar nombre y num eco si num_eco no esta ya en el nombre
    if num_eco and num_eco != 'nan' and num_eco not in equipo:
        nombre_completo = f"{equipo} - {num_eco}"
    else:
        nombre_completo = equipo
        
        
    if equipo.upper() not in existentes:
        print(f"  [NUEVO] Agregando: {equipo} ({num_eco})")
        try:
            cur.execute("INSERT INTO catalogos.equipos (descripcion, numero_economico) VALUES (%s, %s)", (equipo, num_eco))
            existentes.add(equipo.upper())
            nuevos += 1
        except Exception as e:
            print(f"Error con {equipo}: {e}")
            conn.rollback()

conn.commit()
cur.close()
conn.close()

print(f"\nSincronizacion de equipos terminada. {nuevos} equipos nuevos agregados.")
