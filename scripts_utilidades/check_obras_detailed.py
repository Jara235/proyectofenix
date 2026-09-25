import psycopg2
from psycopg2.extras import DictCursor

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

print("=== 1. DIESEL.CONSUMOS: MEXICO-TOLUCA & LERMA-TRES MARIAS ===")
cur.execute("""
    SELECT 
        CASE 
            WHEN obra_destino ILIKE '%TOLUCA%' AND obra_destino NOT ILIKE '%BACHEO%' THEN 'MEXICO-TOLUCA'
            WHEN obra_destino ILIKE '%LERMA%' THEN 'LERMA-TRES MARIAS'
            ELSE obra_destino 
        END as obra_norm,
        fecha,
        semana,
        litros,
        costo_por_litro,
        importe_total,
        equipo,
        responsable
    FROM diesel.consumos
    WHERE (obra_destino ILIKE '%TOLUCA%' AND obra_destino NOT ILIKE '%BACHEO%')
       OR obra_destino ILIKE '%LERMA%'
    ORDER BY fecha;
""")
diesel_consumos = cur.fetchall()
print(f"Total registros: {len(diesel_consumos)}")
for r in diesel_consumos[:10]:
    print(dict(r))

print("\n=== 2. GASOLINA.CONSUMOS: MEXICO-TOLUCA & LERMA-TRES MARIAS ===")
cur.execute("""
    SELECT 
        CASE 
            WHEN obra_destino ILIKE '%TOLUCA%' AND obra_destino NOT ILIKE '%BACHEO%' THEN 'MEXICO-TOLUCA'
            WHEN obra_destino ILIKE '%LERMA%' THEN 'LERMA-TRES MARIAS'
            ELSE obra_destino 
        END as obra_norm,
        fecha,
        semana,
        litros,
        costo_por_litro,
        importe_total,
        vehiculo,
        conductor
    FROM gasolina.consumos
    WHERE (obra_destino ILIKE '%TOLUCA%' AND obra_destino NOT ILIKE '%BACHEO%')
       OR obra_destino ILIKE '%LERMA%'
    ORDER BY fecha;
""")
gas_consumos = cur.fetchall()
print(f"Total registros: {len(gas_consumos)}")
for r in gas_consumos[:10]:
    print(dict(r))

print("\n=== 3. DIESEL.FACTURAS: MEXICO-TOLUCA & LERMA-TRES MARIAS ===")
cur.execute("""
    SELECT 
        CASE 
            WHEN obra_destino ILIKE '%TOLUCA%' AND obra_destino NOT ILIKE '%BACHEO%' THEN 'MEXICO-TOLUCA'
            WHEN obra_destino ILIKE '%LERMA%' THEN 'LERMA-TRES MARIAS'
            ELSE obra_destino 
        END as obra_norm,
        fecha_factura,
        semana,
        litros_facturados,
        precio_unitario,
        importe_total,
        proveedor,
        folio_factura
    FROM diesel.facturas
    WHERE (obra_destino ILIKE '%TOLUCA%' AND obra_destino NOT ILIKE '%BACHEO%')
       OR obra_destino ILIKE '%LERMA%'
    ORDER BY fecha_factura;
""")
diesel_facts = cur.fetchall()
print(f"Total registros: {len(diesel_facts)}")
for r in diesel_facts[:10]:
    print(dict(r))

print("\n=== 4. GASOLINA.FACTURAS: MEXICO-TOLUCA & LERMA-TRES MARIAS ===")
cur.execute("""
    SELECT 
        CASE 
            WHEN obra_destino ILIKE '%TOLUCA%' AND obra_destino NOT ILIKE '%BACHEO%' THEN 'MEXICO-TOLUCA'
            WHEN obra_destino ILIKE '%LERMA%' THEN 'LERMA-TRES MARIAS'
            ELSE obra_destino 
        END as obra_norm,
        fecha_factura,
        semana,
        litros_facturados,
        importe_total,
        proveedor,
        folio_factura
    FROM gasolina.facturas
    WHERE (obra_destino ILIKE '%TOLUCA%' AND obra_destino NOT ILIKE '%BACHEO%')
       OR obra_destino ILIKE '%LERMA%'
    ORDER BY fecha_factura;
""")
gas_facts = cur.fetchall()
print(f"Total registros: {len(gas_facts)}")
for r in gas_facts[:10]:
    print(dict(r))

conn.close()
