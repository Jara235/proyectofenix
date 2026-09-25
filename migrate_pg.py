import sqlite3
import psycopg2
from psycopg2.extras import execute_values

SQLITE_DB = r'c:\Users\JOSE\Desktop\Proyecto fenix\fenix_v2.db'
PG_CONN = "dbname='fenix_db' user='postgres' password='Bupito*268' host='localhost'"

def create_pg_schema(pg_cur):
    schemas = ['catalogos', 'diesel', 'gasolina', 'acarreos', 'mezcla']
    for s in schemas:
        pg_cur.execute(f"CREATE SCHEMA IF NOT EXISTS {s};")

    ddl = """
    -- CATALOGOS
    CREATE TABLE IF NOT EXISTS catalogos.obras (
        codigo TEXT PRIMARY KEY,
        nombre TEXT NOT NULL,
        ingeniero_responsable TEXT,
        responsable_default TEXT
    );
    CREATE TABLE IF NOT EXISTS catalogos.equipos (
        numero_economico TEXT PRIMARY KEY,
        descripcion TEXT,
        tipo_equipo TEXT,
        operador_default TEXT
    );
    CREATE TABLE IF NOT EXISTS catalogos.operadores (
        id SERIAL PRIMARY KEY,
        nombre TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS catalogos.responsables (
        id SERIAL PRIMARY KEY,
        nombre TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS catalogos.operaciones (
        id SERIAL PRIMARY KEY,
        tipo_operacion TEXT UNIQUE,
        codigo_operacion TEXT
    );

    -- DIESEL
    CREATE TABLE IF NOT EXISTS diesel.solicitudes (
        id SERIAL PRIMARY KEY,
        semana TEXT NOT NULL,
        fecha_solicitud TEXT NOT NULL,
        ingeniero_solicitante TEXT NOT NULL,
        obra_destino TEXT NOT NULL,
        litros_solicitados NUMERIC NOT NULL,
        estatus TEXT DEFAULT 'Pendiente',
        observaciones TEXT
    );
    CREATE TABLE IF NOT EXISTS diesel.consumos (
        id SERIAL PRIMARY KEY,
        folio_conciliacion TEXT UNIQUE NOT NULL, 
        fecha TEXT NOT NULL,
        semana TEXT NOT NULL,
        origen TEXT,
        tipo_movimiento TEXT,
        obra_destino TEXT REFERENCES catalogos.obras(codigo),
        equipo TEXT,
        equipo_economico TEXT REFERENCES catalogos.equipos(numero_economico),
        litros NUMERIC NOT NULL,
        costo_por_litro NUMERIC,
        importe_total NUMERIC NOT NULL,
        responsable TEXT,
        operador TEXT,
        observaciones TEXT,
        foto_evidencia BYTEA,  
        usuario_captura TEXT,
        solicitud_id INTEGER REFERENCES diesel.solicitudes(id)
    );
    CREATE TABLE IF NOT EXISTS diesel.facturas (
        id SERIAL PRIMARY KEY,
        folio_conciliacion TEXT NOT NULL, 
        folio_factura TEXT NOT NULL,
        fecha_factura TEXT,
        semana TEXT NOT NULL,
        proveedor TEXT,
        punto_de_carga TEXT,
        litros_facturados NUMERIC NOT NULL,
        precio_unitario NUMERIC,
        importe NUMERIC,
        iva NUMERIC,
        importe_total NUMERIC NOT NULL,
        uuid_cfdi TEXT,
        archivo_pdf BYTEA,
        archivo_xml BYTEA
    );

    -- GASOLINA
    CREATE TABLE IF NOT EXISTS gasolina.autorizaciones (
        id SERIAL PRIMARY KEY,
        folio_conciliacion TEXT UNIQUE NOT NULL,
        fecha TEXT,
        semana TEXT,
        origen TEXT,
        obra_destino TEXT,
        vehiculo TEXT,
        placa TEXT,
        litros_autorizados NUMERIC,
        importe_autorizado NUMERIC,
        responsable TEXT,
        estatus_autorizacion TEXT
    );
    CREATE TABLE IF NOT EXISTS gasolina.consumos (
        id SERIAL PRIMARY KEY,
        folio_conciliacion TEXT UNIQUE NOT NULL,
        fecha TEXT NOT NULL,
        semana TEXT NOT NULL,
        origen TEXT,
        obra_destino TEXT,
        vehiculo TEXT,
        placa TEXT,
        kilometraje NUMERIC,
        litros NUMERIC NOT NULL,
        costo_por_litro NUMERIC,
        importe_total NUMERIC NOT NULL,
        conductor TEXT,
        observaciones TEXT,
        foto_evidencia BYTEA, 
        usuario_captura TEXT  
    );
    CREATE TABLE IF NOT EXISTS gasolina.facturas (
        id SERIAL PRIMARY KEY,
        folio_conciliacion TEXT NOT NULL,
        folio_factura TEXT NOT NULL,
        fecha_factura TEXT,
        semana TEXT NOT NULL,
        proveedor TEXT,
        litros_facturados NUMERIC NOT NULL,
        importe_total NUMERIC NOT NULL,
        uuid_cfdi TEXT,
        archivo_pdf BYTEA,
        archivo_xml BYTEA
    );
    CREATE TABLE IF NOT EXISTS gasolina.estados_cuenta (
        id SERIAL PRIMARY KEY,
        semana TEXT NOT NULL,
        responsable TEXT,
        vehiculo TEXT,
        placa TEXT,
        obra_destino TEXT,
        gasolinera TEXT,
        importe_autorizado NUMERIC NOT NULL DEFAULT 0,
        consumo_real NUMERIC NOT NULL DEFAULT 0,
        litros_reales NUMERIC NOT NULL DEFAULT 0,
        diferencia NUMERIC GENERATED ALWAYS AS (importe_autorizado - consumo_real) STORED,
        estatus TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- ACARREOS
    CREATE TABLE IF NOT EXISTS acarreos.viajes (
        id SERIAL PRIMARY KEY,
        folio_viaje TEXT UNIQUE NOT NULL,
        fecha TEXT NOT NULL,
        semana TEXT NOT NULL,
        sindicato TEXT,
        material TEXT,
        origen TEXT,
        obra_destino TEXT,
        placa_camion TEXT,
        capacidad_m3 NUMERIC,
        precio_unitario NUMERIC,
        importe_total NUMERIC NOT NULL,
        observaciones TEXT,
        foto_evidencia BYTEA,
        usuario_captura TEXT
    );
    CREATE TABLE IF NOT EXISTS acarreos.facturas (
        id SERIAL PRIMARY KEY,
        folio_viaje TEXT NOT NULL,
        folio_factura TEXT NOT NULL,
        fecha_factura TEXT,
        semana TEXT NOT NULL,
        sindicato_proveedor TEXT,
        viajes_amparados INTEGER,
        importe_total NUMERIC NOT NULL,
        uuid_cfdi TEXT,
        archivo_pdf BYTEA,
        archivo_xml BYTEA
    );

    -- MEZCLA
    CREATE TABLE IF NOT EXISTS mezcla.materia_prima (
        id SERIAL PRIMARY KEY,
        folio_conciliacion TEXT UNIQUE NOT NULL,
        fecha TEXT NOT NULL,
        semana TEXT NOT NULL,
        mina_origen TEXT,
        planta_destino TEXT,
        material TEXT,
        camion TEXT,
        placa TEXT,
        toneladas NUMERIC NOT NULL,
        costo_material NUMERIC,
        flete NUMERIC,
        importe_total NUMERIC NOT NULL,
        foto_evidencia BYTEA,
        usuario_captura TEXT
    );
    CREATE TABLE IF NOT EXISTS mezcla.produccion (
        id SERIAL PRIMARY KEY,
        folio_conciliacion TEXT UNIQUE NOT NULL,
        fecha TEXT NOT NULL,
        semana TEXT NOT NULL,
        planta TEXT,
        tipo_mezcla TEXT,
        toneladas_producidas NUMERIC NOT NULL,
        emulsion_consumida_lts NUMERIC,
        agregados_consumidos_m3 NUMERIC,
        costo_total_produccion NUMERIC,
        foto_evidencia BYTEA,
        usuario_captura TEXT
    );
    CREATE TABLE IF NOT EXISTS mezcla.tendido (
        id SERIAL PRIMARY KEY,
        folio_conciliacion TEXT UNIQUE NOT NULL,
        fecha TEXT NOT NULL,
        semana TEXT NOT NULL,
        planta_origen TEXT,
        obra_destino TEXT,
        viajes_enviados INTEGER,
        toneladas_tendidas NUMERIC NOT NULL,
        metros_cuadrados_tendidos NUMERIC,
        rendimiento_obra TEXT,
        foto_evidencia BYTEA,
        usuario_captura TEXT
    );
    """
    pg_cur.execute(ddl)

def migrate_table(sl_cur, pg_cur, sl_table, pg_table, cols_to_skip=[]):
    sl_cur.execute(f"PRAGMA table_info({sl_table})")
    columns = [r[1] for r in sl_cur.fetchall() if r[1] not in cols_to_skip]
    if not columns:
        return 0
    
    col_names = ", ".join(columns)
    placeholders = ", ".join(["%s"] * len(columns))
    
    sl_cur.execute(f"SELECT {col_names} FROM {sl_table}")
    rows = sl_cur.fetchall()
    
    if rows:
        # Convert any integers mapped to text 'semana' fields to strings if needed
        # Actually Postgres can cast naturally.
        insert_query = f"INSERT INTO {pg_table} ({col_names}) VALUES %s"
        execute_values(pg_cur, insert_query, rows)
    return len(rows)

try:
    sl_conn = sqlite3.connect(SQLITE_DB)
    sl_cur = sl_conn.cursor()
    
    pg_conn = psycopg2.connect(PG_CONN)
    pg_cur = pg_conn.cursor()
    
    print("Creando esquemas y tablas en PostgreSQL...")
    create_pg_schema(pg_cur)
    pg_conn.commit()
    
    tables_map = {
        'catalogos_obras': 'catalogos.obras',
        'catalogos_equipos': 'catalogos.equipos',
        'catalogos_operadores': 'catalogos.operadores',
        'catalogos_responsables': 'catalogos.responsables',
        'catalogos_operaciones': 'catalogos.operaciones',
        
        'diesel_solicitudes': 'diesel.solicitudes',
        'diesel_consumos': 'diesel.consumos',
        'diesel_facturas': 'diesel.facturas',
        
        'gasolina_autorizaciones': 'gasolina.autorizaciones',
        'gasolina_consumos': 'gasolina.consumos',
        'gasolina_facturas': 'gasolina.facturas',
        'gasolina_estados_cuenta': 'gasolina.estados_cuenta',
        
        'acarreos_viajes': 'acarreos.viajes',
        'acarreos_facturas': 'acarreos.facturas',
        
        'mezcla_materia_prima': 'mezcla.materia_prima',
        'mezcla_produccion': 'mezcla.produccion',
        'mezcla_tendido': 'mezcla.tendido'
    }
    
    print("\nMigrando datos...")
    for sl_t, pg_t in tables_map.items():
        try:
            # Skip generated columns
            skip = []
            if pg_t == 'gasolina.estados_cuenta':
                skip = ['diferencia']
            
            # Delete existing
            pg_cur.execute(f"TRUNCATE {pg_t} CASCADE")
            
            count = migrate_table(sl_cur, pg_cur, sl_t, pg_t, cols_to_skip=skip)
            print(f"  {sl_t} -> {pg_t}: {count} filas")
        except Exception as e:
            print(f"  [ERROR] {sl_t}: {e}")
            pg_conn.rollback()
    
    pg_conn.commit()
    print("\nMigración completada con éxito.")

except Exception as e:
    print(f"Error global: {e}")
finally:
    if 'pg_cur' in locals(): pg_cur.close()
    if 'pg_conn' in locals(): pg_conn.close()
    if 'sl_cur' in locals(): sl_cur.close()
    if 'sl_conn' in locals(): sl_conn.close()
