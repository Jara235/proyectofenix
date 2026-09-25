import psycopg2
import json
import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

JSON_PATH = r"c:\Users\JOSE\Desktop\Proyecto fenix\facturas_sem28_clasificadas.json"

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor()
print("Conectado a PostgreSQL")

# Leer las facturas clasificadas del JSON
with open(JSON_PATH, 'r', encoding='utf-8') as f:
    facturas = json.load(f)

facturas_diesel = [f for f in facturas if f['tipo'] == 'diesel']
print(f"Facturas diesel de Semana 28: {len(facturas_diesel)}")

# Ver cuantas ya estan en Postgres por UUID o folio
cur.execute("SELECT uuid_cfdi, folio_factura FROM diesel.facturas WHERE semana = 'Semana 28'")
existentes_sem28 = cur.fetchall()
uuids_existentes = set([r[0] for r in existentes_sem28 if r[0]])
folios_existentes = set([str(r[1]) for r in existentes_sem28 if r[1]])
print(f"Facturas Semana 28 ya en Postgres: {len(existentes_sem28)}")

# Resetear secuencia por si acaso
cur.execute("SELECT MAX(id) FROM diesel.facturas")
max_id = cur.fetchone()[0] or 0
cur.execute("SELECT pg_get_serial_sequence('diesel.facturas', 'id')")
seq = cur.fetchone()[0]
cur.execute(f"SELECT setval('{seq}', {max_id})")
conn.commit()
print(f"Secuencia ID reseteada a {max_id}")

insertadas = 0
saltadas = 0
errores = 0

print("\nInsertando facturas...")
for i, fac in enumerate(facturas_diesel):
    uuid = fac.get('uuid', '') or ''
    folio_fac = fac.get('folio', '') or ''
    
    # Saltar si ya existe por UUID o por folio
    if uuid and uuid in uuids_existentes:
        saltadas += 1
        continue
    if folio_fac and folio_fac in folios_existentes:
        saltadas += 1
        continue
    
    try:
        # Generar folio de conciliacion
        num = max_id + insertadas + 1
        folio_conc = f"FA-DPC-28-{str(num).zfill(3)}"
        
        fecha = fac.get('fecha', '') or None
        semana = fac.get('semana', 'Semana 28')
        proveedor = fac.get('emisor_nombre', 'DERIVADOS DE PETROLEO CASTILLA').strip() or 'DERIVADOS DE PETROLEO CASTILLA'
        
        # Detectar punto de carga por descripcion
        desc = fac.get('descripcion', '').upper()
        num_despacho = ''
        import re
        m = re.search(r'Despacho (\d+)', fac.get('descripcion', ''), re.IGNORECASE)
        num_despacho = m.group(1) if m else ''
        
        # Por ahora usamos la descripcion como punto de carga hasta que se asigne manualmente
        if 'BACHEO' in desc:
            punto = 'Bacheo Toluca'
        elif 'EXTRA' in desc or 'SUPREME' in desc:
            punto = 'Por Asignar (Gasolina)'
        else:
            punto = 'Por Asignar'
        
        litros         = float(fac.get('cantidad', 0) or 0)
        precio_unit    = float(fac.get('precio_unitario', 0) or 0)
        importe        = float(fac.get('importe', 0) or 0)
        iva            = float(fac.get('iva', 0) or 0)
        total          = float(fac.get('total', 0) or 0)
        descripcion    = fac.get('descripcion', '') or ''
        archivo_xml    = fac.get('archivo_xml', '') or ''
        
        cur.execute("""
            INSERT INTO diesel.facturas (
                folio_conciliacion, folio_factura, fecha_factura, semana, proveedor,
                punto_de_carga, litros_facturados, precio_unitario, importe, iva,
                importe_total, uuid_cfdi, estatus_revision
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (folio_conc, folio_fac or None, fecha, semana, proveedor,
              punto, litros, precio_unit, importe, iva, total,
              uuid or None, 'PENDIENTE'))
        
        insertadas += 1
        print(f"  [{insertadas:2d}] {folio_conc} | {fecha} | {litros:7.2f} Lts | ${total:12,.2f} | {desc[:40]}")
        
    except Exception as e:
        errores += 1
        conn.rollback()
        print(f"  ERROR en factura {i} ({fac.get('archivo_xml', '')}): {e}")

conn.commit()

print(f"\n{'='*50}")
print(f"RESULTADO FINAL:")
print(f"  Insertadas:  {insertadas}")
print(f"  Saltadas:    {saltadas} (ya existian)")
print(f"  Errores:     {errores}")

cur.execute("SELECT COUNT(*) FROM diesel.facturas")
total = cur.fetchone()[0]
print(f"\ndiesel.facturas total ahora: {total}")

cur.execute("SELECT semana, COUNT(*), ROUND(SUM(litros_facturados),1) FROM diesel.facturas GROUP BY semana ORDER BY semana")
print("\nFacturas por semana:")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]} facturas | {r[2]} Lts")

cur.close()
conn.close()
print("\nListo!")
