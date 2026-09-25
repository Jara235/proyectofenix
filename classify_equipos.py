import pandas as pd
import psycopg2

print("Leyendo Excel de Gasolina...")
df = pd.read_excel(r'c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_GASOLINA_NUEVO.xlsx', sheet_name='CATALOGOS')
placas_df = df['PLACA'].dropna().astype(str).str.strip().str.upper()

placas_set = set(placas_df.tolist())

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor()

# 1. Update all to DIESEL by default
cur.execute("UPDATE catalogos.equipos SET tipo_equipo = 'DIESEL'")

# 2. Update to GASOLINA if numero_economico is in placas_set
gasolina_count = 0
for placa in placas_set:
    cur.execute("UPDATE catalogos.equipos SET tipo_equipo = 'GASOLINA' WHERE UPPER(numero_economico) = %s OR UPPER(descripcion) LIKE %s", (placa, f'%{placa}%'))
    if cur.rowcount > 0:
        gasolina_count += cur.rowcount

# Also check for any equipment that might have 'PICK UP', 'CAMIONETA', 'TSURU', 'URBAN', 'AUTO', 'RAM', 'VEHICULO', 'L200', 'S10'
vehiculos_kws = ['PICK UP', 'CAMIONETA', 'TSURU', 'URBAN', 'AUTO', 'RAM', 'VEHICULO', 'L200', 'S10', 'CHEVROLET', 'NISSAN', 'TOYOTA', 'DODGE']
for kw in vehiculos_kws:
    cur.execute("UPDATE catalogos.equipos SET tipo_equipo = 'GASOLINA' WHERE UPPER(descripcion) LIKE %s AND tipo_equipo = 'DIESEL'", (f'%{kw}%',))
    if cur.rowcount > 0:
        gasolina_count += cur.rowcount

# What about the ones in Gasolina Excel but missing in DB?
cur.execute("SELECT UPPER(numero_economico) FROM catalogos.equipos")
db_ecos = set(r[0] for r in cur.fetchall() if r[0])

nuevos = 0
for idx, row in df.iterrows():
    v = str(row['VEHICULOS']).strip()
    p = str(row['PLACA']).strip().upper()
    if pd.notnull(row['PLACA']) and p != 'NAN' and p not in db_ecos:
        desc = f"{v} {p}"
        try:
            cur.execute("INSERT INTO catalogos.equipos (numero_economico, descripcion, tipo_equipo) VALUES (%s, %s, 'GASOLINA')", (p, desc))
            db_ecos.add(p)
            nuevos += 1
        except Exception as e:
            pass

conn.commit()
print(f"Marcados como GASOLINA: {gasolina_count} (aprox. por updates)")
print(f"Nuevos vehiculos insertados de Gasolina: {nuevos}")
conn.close()
