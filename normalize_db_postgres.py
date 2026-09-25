import psycopg2

conn=psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
conn.autocommit = True
cur=conn.cursor()

# 1. Delete BD_JALISCO
for table in ['diesel.solicitudes', 'diesel.consumos', 'gasolina.consumos']:
    cur.execute(f"DELETE FROM {table} WHERE obra_destino = 'BD_JALISCO'")
    print(f"Deleted BD_JALISCO from {table}: {cur.rowcount} rows")

# 2. Normalize Names
replacements = {
    'México-Toluca': 'México - Toluca',
    'Vicente Lomabrdo': 'Vicente Lombardo',
    'Planta Asflato Huixquilucan': 'Planta Huixquilucan',
    'Planta Asfalto Pegaso': 'Planta Pegaso',
    'NaN': 'Obra sin asignar'
}

for table in ['diesel.solicitudes', 'diesel.consumos', 'gasolina.consumos']:
    for old, new in replacements.items():
        cur.execute(f"UPDATE {table} SET obra_destino = %s WHERE obra_destino = %s", (new, old))
        if cur.rowcount > 0:
            print(f"Normalized {old} to {new} in {table}: {cur.rowcount} rows")

# 3. Add obra_destino to diesel.facturas if it doesn't exist
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema='diesel' AND table_name='facturas' AND column_name='obra_destino'")
if not cur.fetchone():
    cur.execute("ALTER TABLE diesel.facturas ADD COLUMN obra_destino TEXT;")
    print("Added obra_destino to diesel.facturas")

# 4. Populate obra_destino in diesel.facturas based on Folio
# Prefixes mapping
folio_mapping = {
    'MT': 'México - Toluca',
    'L3M': 'Lerma - Tres Marías',
    'PRO': 'Providencia',
    'BT': 'Bacheo Toluca',
    'MP': 'Maquinaria Pegaso',
    'DPC': 'Desasolve',
    'XX': 'Obra sin asignar'
}

# Fetch all facturas to update
cur.execute("SELECT id, folio_conciliacion FROM diesel.facturas")
facturas = cur.fetchall()
updated = 0
for fac_id, folio in facturas:
    if folio and '-' in folio:
        parts = folio.split('-')
        if len(parts) > 1:
            prefix = parts[1]
            obra = folio_mapping.get(prefix, 'Obra sin asignar')
            cur.execute("UPDATE diesel.facturas SET obra_destino = %s WHERE id = %s", (obra, fac_id))
            updated += 1
print(f"Populated obra_destino for {updated} diesel.facturas")

conn.close()
print("Normalization completed.")
