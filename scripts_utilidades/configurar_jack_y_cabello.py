import psycopg2
from psycopg2.extras import DictCursor

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

print("=== 1. AGREGANDO / ACTUALIZANDO OBRAS EN catalogos.obras ===")

# Asegurar que ESTIMACIONES esté en catalogos.obras
cur.execute("SELECT codigo FROM catalogos.obras WHERE nombre = 'ESTIMACIONES';")
if not cur.fetchone():
    cur.execute("""
        INSERT INTO catalogos.obras (codigo, nombre, ingeniero_responsable, responsable_default)
        VALUES ('ESTM', 'ESTIMACIONES', 'JOSE CABELLO', 'JOSE CABELLO');
    """)
    print("[OK] Obra ESTIMACIONES agregada a catalogos.obras")

# Actualizar Planta Pegaso en catalogos.obras
cur.execute("""
    UPDATE catalogos.obras 
    SET ingeniero_responsable = 'JACK', responsable_default = 'JACK'
    WHERE nombre IN ('Planta Pegaso', 'ESTIMACIONES /PLANTA PEGASO');
""")
print("[OK] Responsable de Planta Pegaso actualizado a JACK en catalogos.obras")

print("\n=== 2. ACTUALIZANDO CATÁLOGO MAESTRO (gasolina.autorizaciones_maestro) ===")

# Actualizar José Cabello (LHB176D - $1,500.00 - ESTIMACIONES)
cur.execute("""
    UPDATE gasolina.autorizaciones_maestro
    SET responsable = 'JOSE CABELLO',
        centro_trabajo = 'ESTIMACIONES',
        unidad_equipo = 'Vehículo',
        placas = 'LHB176D',
        importe_semanal = 1500.00,
        activo = true
    WHERE id = 274;
""")
print(f"[OK] Fila maestro José Cabello (ID 274) actualizada: {cur.rowcount}")

# Verificar/Actualizar Jack (PCU7482 - $1,500.00 - PLANTA PEGASO)
cur.execute("SELECT id FROM gasolina.autorizaciones_maestro WHERE responsable = 'JACK';")
r_jack = cur.fetchone()
if r_jack:
    jack_maestro_id = r_jack[0]
    cur.execute("""
        UPDATE gasolina.autorizaciones_maestro
        SET centro_trabajo = 'Planta Pegaso',
            unidad_equipo = 'FORD RANGER',
            placas = 'PCU7482',
            importe_semanal = 1500.00,
            activo = true
        WHERE id = %s;
    """, (jack_maestro_id,))
    print(f"[OK] Fila maestro Jack (ID {jack_maestro_id}) actualizada")
else:
    cur.execute("SELECT COALESCE(MAX(num_renglon), 0) + 1 FROM gasolina.autorizaciones_maestro WHERE empresa = 'JDJ';")
    next_renglon = cur.fetchone()[0]
    cur.execute("""
        INSERT INTO gasolina.autorizaciones_maestro (
            empresa, num_renglon, responsable, centro_trabajo, unidad_equipo, placas, importe_semanal, activo
        ) VALUES (
            'JDJ', %s, 'JACK', 'Planta Pegaso', 'FORD RANGER', 'PCU7482', 1500.00, true
        ) RETURNING id;
    """, (next_renglon,))
    jack_maestro_id = cur.fetchone()[0]
    print(f"[OK] Fila maestro Jack insertada con ID {jack_maestro_id}")

print("\n=== 3. ACTUALIZANDO AUTORIZACIONES SEMANAL SEMANA 33 ===")

# Actualizar José Cabello en Semana 33
cur.execute("""
    UPDATE gasolina.autorizaciones_semanal
    SET responsable = 'JOSE CABELLO',
        centro_trabajo = 'ESTIMACIONES',
        unidad_equipo = 'Vehículo',
        placas = 'LHB176D',
        importe_semanal = 1500.00
    WHERE semana = 33 AND maestro_id = 274;
""")
print(f"[OK] Fila semanal José Cabello actualizada: {cur.rowcount}")

# Actualizar / Insertar Jack en Semana 33
cur.execute("SELECT id FROM gasolina.autorizaciones_semanal WHERE semana = 33 AND (responsable = 'JACK' OR maestro_id = %s);", (jack_maestro_id,))
r_jack_sem = cur.fetchone()
if r_jack_sem:
    cur.execute("""
        UPDATE gasolina.autorizaciones_semanal
        SET responsable = 'JACK',
            centro_trabajo = 'Planta Pegaso',
            unidad_equipo = 'FORD RANGER',
            placas = 'PCU7482',
            importe_semanal = 1500.00
        WHERE id = %s;
    """, (r_jack_sem[0],))
    print(f"[OK] Fila semanal Jack (ID {r_jack_sem[0]}) actualizada")
else:
    cur.execute("""
        INSERT INTO gasolina.autorizaciones_semanal (
            semana, maestro_id, empresa, num_renglon, responsable, centro_trabajo, unidad_equipo, placas, importe_semanal
        ) VALUES (
            33, %s, 'JDJ', 49, 'JACK', 'Planta Pegaso', 'FORD RANGER', 'PCU7482', 1500.00
        );
    """, (jack_maestro_id,))
    print(f"[OK] Fila semanal Jack insertada para Semana 33")

print("\n=== 4. ACTUALIZANDO TABLA GENERAL gasolina.autorizaciones ===")
cur.execute("DELETE FROM gasolina.autorizaciones WHERE semana IN ('33', 'Semana 33') AND responsable IN ('JOSÉ CABELLO / JACK', 'JACK', 'JOSE CABELLO');")

cur.execute("""
    INSERT INTO gasolina.autorizaciones (
        folio_conciliacion, fecha, semana, origen, obra_destino, vehiculo, placa,
        litros_autorizados, importe_autorizado, responsable, estatus_autorizacion, estatus_revision
    ) VALUES 
    ('AUTH-GAS-S33-CABELLO', '2026-08-10', '33', 'AUTORIZACION_SEMANAL', 'ESTIMACIONES', 'Vehículo', 'LHB176D', 65.53, 1500.00, 'JOSE CABELLO', 'AUTORIZADO', 'APROBADO'),
    ('AUTH-GAS-S33-JACK', '2026-08-10', '33', 'AUTORIZACION_SEMANAL', 'Planta Pegaso', 'FORD RANGER', 'PCU7482', 65.53, 1500.00, 'JACK', 'AUTORIZADO', 'APROBADO');
""")
print(f"[OK] Autorizaciones individuales creadas en gasolina.autorizaciones")

print("\n=== 5. ACTUALIZANDO CONSUMOS EN gasolina.consumos ===")

# Actualizar consumos de LHB176D para José Cabello
cur.execute("""
    UPDATE gasolina.consumos
    SET conductor = 'JOSE CABELLO',
        obra_destino = 'ESTIMACIONES'
    WHERE semana IN ('33', 'Semana 33') AND placa = 'LHB176D';
""")
print(f"[OK] Consumos actualizados para José Cabello (LHB176D): {cur.rowcount}")

# Actualizar consumo ID 453 para Jack (PCU7482)
cur.execute("""
    UPDATE gasolina.consumos
    SET conductor = 'JACK',
        obra_destino = 'Planta Pegaso'
    WHERE id = 453;
""")
print(f"[OK] Consumo ID 453 actualizado para Jack (PCU7482): {cur.rowcount}")

conn.commit()
print("\n[OK] ¡TODOS LOS CAMBIOS FUERON GUARDADOS EXITOSAMENTE EN POSTGRESQL!")
conn.close()
