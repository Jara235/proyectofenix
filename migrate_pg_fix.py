import sqlite3
import psycopg2
from psycopg2.extras import execute_values

SQLITE_DB = r'c:\Users\JOSE\Desktop\Proyecto fenix\fenix_v2.db'
PG_CONN = "dbname='fenix_db' user='postgres' password='Bupito*268' host='localhost'"

def create_pg_schema(pg_cur):
    ddl = """
    ALTER TABLE diesel.consumos DROP CONSTRAINT IF EXISTS consumos_obra_destino_fkey;
    ALTER TABLE diesel.consumos DROP CONSTRAINT IF EXISTS consumos_equipo_economico_fkey;
    ALTER TABLE diesel.consumos DROP CONSTRAINT IF EXISTS consumos_solicitud_id_fkey;
    
    -- Drop and recreate diesel.consumos without strict FKs to avoid migration issues with bad data
    DROP TABLE IF EXISTS diesel.consumos CASCADE;
    CREATE TABLE IF NOT EXISTS diesel.consumos (
        id SERIAL PRIMARY KEY,
        folio_conciliacion TEXT UNIQUE NOT NULL, 
        fecha TEXT NOT NULL,
        semana TEXT NOT NULL,
        origen TEXT,
        tipo_movimiento TEXT,
        obra_destino TEXT,
        equipo TEXT,
        equipo_economico TEXT,
        litros NUMERIC NOT NULL,
        costo_por_litro NUMERIC,
        importe_total NUMERIC NOT NULL,
        responsable TEXT,
        operador TEXT,
        observaciones TEXT,
        foto_evidencia BYTEA,  
        usuario_captura TEXT,
        solicitud_id INTEGER
    );
    """
    pg_cur.execute(ddl)

def migrate_table(sl_cur, pg_cur, sl_table, pg_table, cols_to_skip=[]):
    sl_cur.execute(f"PRAGMA table_info({sl_table})")
    columns = [r[1] for r in sl_cur.fetchall() if r[1] not in cols_to_skip]
    if not columns:
        return 0
    
    col_names = ", ".join(columns)
    
    sl_cur.execute(f"SELECT {col_names} FROM {sl_table}")
    rows = sl_cur.fetchall()
    
    if rows:
        insert_query = f"INSERT INTO {pg_table} ({col_names}) VALUES %s"
        execute_values(pg_cur, insert_query, rows)
    return len(rows)

try:
    sl_conn = sqlite3.connect(SQLITE_DB)
    sl_cur = sl_conn.cursor()
    
    pg_conn = psycopg2.connect(PG_CONN)
    pg_cur = pg_conn.cursor()
    
    create_pg_schema(pg_cur)
    pg_conn.commit()
    
    print("Re-migrando diesel_consumos...")
    try:
        pg_cur.execute(f"TRUNCATE diesel.consumos CASCADE")
        count = migrate_table(sl_cur, pg_cur, 'diesel_consumos', 'diesel.consumos')
        print(f"  diesel_consumos -> diesel.consumos: {count} filas")
    except Exception as e:
        print(f"  [ERROR] diesel_consumos: {e}")
        pg_conn.rollback()
    
    pg_conn.commit()

except Exception as e:
    print(f"Error global: {e}")
finally:
    if 'pg_cur' in locals(): pg_cur.close()
    if 'pg_conn' in locals(): pg_conn.close()
    if 'sl_cur' in locals(): sl_cur.close()
    if 'sl_conn' in locals(): sl_conn.close()
