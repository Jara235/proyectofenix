import psycopg2
conn=psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
conn.autocommit = True
cur=conn.cursor()

# ============================================================
# 1. MERGE Lerma - Tenango -> Lerma - Tres Marías
# ============================================================
obras_merge = {
    'Lerma - Tenango': 'Lerma - Tres Marías',
}

for tabla in ['diesel.solicitudes', 'diesel.consumos']:
    for old, new in obras_merge.items():
        cur.execute(f"UPDATE {tabla} SET obra_destino = %s WHERE obra_destino = %s", (new, old))
        print(f"  {tabla}: '{old}' -> '{new}' ({cur.rowcount} rows)")

# Also update facturas
for old, new in obras_merge.items():
    cur.execute("UPDATE diesel.facturas SET obra_destino = %s WHERE obra_destino = %s", (new, old))
    print(f"  diesel.facturas: '{old}' -> '{new}' ({cur.rowcount} rows)")

# Also update autorizaciones
for old, new in obras_merge.items():
    cur.execute("UPDATE catalogos.autorizaciones SET referencia = %s WHERE referencia = %s", (new, old))
    print(f"  catalogos.autorizaciones: '{old}' -> '{new}' ({cur.rowcount} rows)")

# ============================================================
# 2. IDENTIFY GASOLINA facturas mixed into diesel
# ============================================================
print("\n=== CHECKING GASOLINA ENTRIES IN DIESEL FACTURAS ===")
cur.execute("""
    SELECT folio_factura, folio_conciliacion, punto_de_carga, litros_facturados, semana
    FROM diesel.facturas
    WHERE LOWER(punto_de_carga) LIKE '%gasolina%' 
       OR LOWER(punto_de_carga) LIKE '%gas%'
       OR LOWER(punto_de_carga) LIKE '%magna%'
       OR LOWER(punto_de_carga) LIKE '%premium%'
""")
gas_in_diesel = cur.fetchall()
print(f"  Found {len(gas_in_diesel)} possible gasolina entries in diesel.facturas:")
for r in gas_in_diesel:
    print(f"    {r}")

# ============================================================
# 3. RE-MAP obras from punto_de_carga description for DPC facturas
# ============================================================
print("\n=== RE-MAPPING DPC FACTURAS TO CORRECT OBRAS ===")
cur.execute("SELECT id, folio_factura, folio_conciliacion, punto_de_carga, litros_facturados FROM diesel.facturas WHERE obra_destino = 'Desasolve' ORDER BY id")
dpc_facturas = cur.fetchall()

# Map from description keywords to obra
keyword_map = [
    ('planta.*asfalto.*huix', 'Planta Huixquilucan'),
    ('planta.*huix', 'Planta Huixquilucan'),
    ('planta de asfalto', 'Planta Pegaso'),
    ('planta pegaso', 'Planta Pegaso'),
    ('planta asfalto', 'Planta Pegaso'),
    ('tanque pegaso', 'Planta Pegaso'),
    ('maquinaria pegaso', 'Maquinaria Pegaso'),
    ('m.xico.*toluca', 'México - Toluca'),
    ('mexico.*toluca', 'México - Toluca'),
    ('bacheo', 'Bacheo Toluca'),
    ('lerma.*tenango', 'Lerma - Tres Marías'),
    ('lerma', 'Lerma - Tres Marías'),
    ('vicente lombardo', 'Vicente Lombardo'),
    ('providencia', 'Providencia'),
    ('alfredo del mazo', 'Alfredo del Mazo'),
    ('desasolve', 'Desasolve'),
    ('dezazolve', 'Desasolve'),
    ('colegio militar', 'Colegio Militar'),
]

import re
reclassified = 0
unclear = []
for fac_id, folio_fac, folio_con, descripcion, litros in dpc_facturas:
    desc_lower = (descripcion or '').lower()
    matched = None
    for kw, obra in keyword_map:
        if re.search(kw, desc_lower):
            matched = obra
            break
    if matched:
        cur.execute("UPDATE diesel.facturas SET obra_destino = %s WHERE id = %s", (matched, fac_id))
        reclassified += 1
        print(f"  {folio_fac} -> '{matched}' [{descripcion[:60]}]")
    else:
        unclear.append((folio_fac, descripcion, litros))

print(f"\n  Reclassified: {reclassified}")
print(f"  Unclear (manual review needed): {len(unclear)}")
for r in unclear:
    print(f"    {r}")

print("\nDone!")
