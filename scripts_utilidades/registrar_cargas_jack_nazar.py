import psycopg2
from psycopg2.extras import DictCursor

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

print("=== 1. INSERTANDO CONSUMOS EN gasolina.consumos ===")

# 1. Carga de $893.08 para Juan Carlos Nazar (Ticket 416727)
cur.execute("""
    INSERT INTO gasolina.consumos (
        folio_conciliacion, fecha, semana, origen, obra_destino, vehiculo, placa,
        kilometraje, litros, costo_por_litro, importe_total, conductor,
        observaciones, estatus_revision, gasolineria
    ) VALUES (
        'GAS-S33-LEV-416727', '2026-08-10', '33', 'Gasolineria', 'MAQUINARIA', 'DODGE RAM 700', 'PCW9238',
        0, 39.016, 22.89, 893.08, 'JUAN CARLOS NAZAR CHAVEZ',
        'Ticket 416727 Levet (Asignado a Juan Carlos Nazar)', 'APROBADO', 'LEVET'
    ) RETURNING id;
""")
id_nazar = cur.fetchone()[0]
print(f"[OK] Carga Juan Carlos Nazar insertada con ID: {id_nazar}")

# 2. Carga 1 Jack Planta Pegaso (Ticket 417998 - $1,000.00 - PCU7482)
cur.execute("""
    INSERT INTO gasolina.consumos (
        folio_conciliacion, fecha, semana, origen, obra_destino, vehiculo, placa,
        kilometraje, litros, costo_por_litro, importe_total, conductor,
        observaciones, estatus_revision, gasolineria
    ) VALUES (
        'GAS-S33-LEV-417998', '2026-08-13', '33', 'Gasolineria', 'Planta Pegaso', 'FORD RANGER', 'PCU7482',
        0, 43.687, 22.89, 1000.00, 'JOSÉ CABELLO / JACK',
        'Ticket 417998 Levet - Jack Planta Pegaso (Placa PCU7482)', 'APROBADO', 'LEVET'
    ) RETURNING id;
""")
id_jack1 = cur.fetchone()[0]
print(f"[OK] Carga Jack Ticket 417998 (PCU7482) insertada con ID: {id_jack1}")

# 3. Carga 2 Jack Planta Pegaso (Ticket 418541 - $700.00 - PAT8298)
cur.execute("""
    INSERT INTO gasolina.consumos (
        folio_conciliacion, fecha, semana, origen, obra_destino, vehiculo, placa,
        kilometraje, litros, costo_por_litro, importe_total, conductor,
        observaciones, estatus_revision, gasolineria
    ) VALUES (
        'GAS-S33-LEV-418541', '2026-08-14', '33', 'Gasolineria', 'Planta Pegaso', 'CHEVROLET S10', 'PAT8298',
        0, 30.581, 22.89, 700.00, 'JOSÉ CABELLO / JACK',
        'Ticket 418541 Levet - Jack Planta Pegaso (Placa PAT8298)', 'APROBADO', 'LEVET'
    ) RETURNING id;
""")
id_jack2 = cur.fetchone()[0]
print(f"[OK] Carga Jack Ticket 418541 (PAT8298) insertada con ID: {id_jack2}")

print("\n=== 2. ACTUALIZANDO / INSERTANDO AUTORIZACIONES PARA JACK (PLANTA PEGASO) ===")

# Actualizar en gasolina.autorizaciones_semanal Semana 33
cur.execute("""
    UPDATE gasolina.autorizaciones_semanal
    SET placas = 'PCU7482, PAT8298, LHB176D',
        importe_semanal = 1500.00,
        centro_trabajo = 'Planta Pegaso'
    WHERE semana = 33 AND responsable ILIKE '%JACK%';
""")
print(f"[OK] Filas actualizadas en autorizaciones_semanal: {cur.rowcount}")

# Actualizar en gasolina.autorizaciones_maestro
cur.execute("""
    UPDATE gasolina.autorizaciones_maestro
    SET placas = 'PCU7482, PAT8298, LHB176D',
        importe_semanal = 1500.00,
        centro_trabajo = 'Planta Pegaso'
    WHERE responsable ILIKE '%JACK%';
""")
print(f"[OK] Filas actualizadas en autorizaciones_maestro: {cur.rowcount}")

# Insertar / Actualizar en gasolina.autorizaciones (tabla general)
cur.execute("""
    INSERT INTO gasolina.autorizaciones (
        folio_conciliacion, fecha, semana, origen, obra_destino, vehiculo, placa,
        litros_autorizados, importe_autorizado, responsable, estatus_autorizacion, estatus_revision
    ) VALUES (
        'AUTH-GAS-S33-JACK', '2026-08-10', '33', 'AUTORIZACION_SEMANAL', 'Planta Pegaso', 'CAMIONETA', 'PCU7482, PAT8298',
        65.53, 1500.00, 'JOSÉ CABELLO / JACK', 'AUTORIZADO', 'APROBADO'
    );
""")
print(f"[OK] Autorizacion de $1,500.00 registrada en gasolina.autorizaciones")

conn.commit()
print("\n[OK] TRANSACCION COMPLETADA Y GUARDADA CON EXITO EN POSTGRESQL!")
conn.close()
