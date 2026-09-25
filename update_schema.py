import psycopg2

PG_CONN = "dbname='fenix_db' user='postgres' password='Bupito*268' host='localhost'"

tables = [
    'diesel.consumos', 'diesel.facturas', 'diesel.solicitudes',
    'gasolina.consumos', 'gasolina.facturas', 'gasolina.autorizaciones', 'gasolina.estados_cuenta',
    'acarreos.viajes', 'acarreos.facturas',
    'mezcla.materia_prima', 'mezcla.produccion', 'mezcla.tendido'
]

try:
    conn = psycopg2.connect(PG_CONN)
    cur = conn.cursor()
    
    for table in tables:
        print(f"Actualizando {table}...")
        # Agregar columna si no existe
        cur.execute(f"""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                               WHERE table_schema = '{table.split('.')[0]}' 
                               AND table_name = '{table.split('.')[1]}' 
                               AND column_name = 'estatus_revision') THEN
                    ALTER TABLE {table} ADD COLUMN estatus_revision VARCHAR(20) DEFAULT 'PENDIENTE';
                END IF;
            END $$;
        """)
        
        # Marcar historial existente como APROBADO
        cur.execute(f"UPDATE {table} SET estatus_revision = 'APROBADO' WHERE estatus_revision = 'PENDIENTE' OR estatus_revision IS NULL;")
        
    conn.commit()
    print("\nModificaciones a la base de datos completadas con éxito.")

except Exception as e:
    print(f"Error: {e}")
    conn.rollback()
finally:
    if 'cur' in locals(): cur.close()
    if 'conn' in locals(): conn.close()
