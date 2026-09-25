# -*- coding: utf-8 -*-
import os
import psycopg2
import sqlite3

def export_postgres():
    print("Exporting PostgreSQL fenix_db...")
    os.makedirs("database", exist_ok=True)
    out_sql = os.path.join("database", "fenix_postgres_full.sql")
    
    try:
        conn = psycopg2.connect("dbname=fenix_db user=postgres password=Bupito*268 host=localhost port=5432")
        cur = conn.cursor()
        
        # Get all schemas
        cur.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name NOT IN ('pg_catalog', 'information_schema')")
        schemas = [r[0] for r in cur.fetchall()]
        print(f"Schemas found: {schemas}")
        
        with open(out_sql, "w", encoding="utf-8") as f:
            f.write("-- ==========================================\n")
            f.write("-- DUMP COMPLETO BASE DE DATOS POSTGRESQL: fenix_db\n")
            f.write("-- SISTEMA FÉNIX 2.0 - GRUPO TRUJANO\n")
            f.write("-- ==========================================\n\n")
            
            for schema in schemas:
                f.write(f"CREATE SCHEMA IF NOT EXISTS {schema};\n")
            f.write("\n")
            
            # Fetch all tables
            cur.execute("""
                SELECT table_schema, table_name 
                FROM information_schema.tables 
                WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
                ORDER BY table_schema, table_name;
            """)
            tables = cur.fetchall()
            print(f"Total PostgreSQL tables: {len(tables)}")
            
            for schema, table in tables:
                f.write(f"-- ------------------------------------------\n")
                f.write(f"-- Tabla: {schema}.{table}\n")
                f.write(f"-- ------------------------------------------\n")
                
                # Fetch columns
                cur.execute("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_schema = %s AND table_name = %s
                    ORDER BY ordinal_position;
                """, (schema, table))
                cols = cur.fetchall()
                
                # Count rows
                cur.execute(f'SELECT COUNT(*) FROM "{schema}"."{table}";')
                count = cur.fetchone()[0]
                f.write(f"-- Registros totales: {count}\n\n")
                
                # Dump rows as INSERTs if count > 0 and count < 5000
                if 0 < count <= 5000:
                    cur.execute(f'SELECT * FROM "{schema}"."{table}";')
                    col_names = [desc[0] for desc in cur.description]
                    col_list_str = ", ".join([f'"{c}"' for c in col_names])
                    
                    rows = cur.fetchall()
                    for row in rows:
                        vals = []
                        for v in row:
                            if v is None:
                                vals.append("NULL")
                            elif isinstance(v, (int, float)):
                                vals.append(str(v))
                            else:
                                clean_v = str(v).replace("'", "''")
                                vals.append(f"'{clean_v}'")
                        val_str = ", ".join(vals)
                        f.write(f'INSERT INTO "{schema}"."{table}" ({col_list_str}) VALUES ({val_str}) ON CONFLICT DO NOTHING;\n')
                    f.write("\n")
                    
        conn.close()
        print(f"PostgreSQL dump saved successfully to {out_sql} ({os.path.getsize(out_sql)} bytes)")
    except Exception as e:
        print(f"Error exporting PostgreSQL: {e}")

def export_sqlite():
    print("\nExporting SQLite databases...")
    for db_name in ["fenix.db", "fenix_v2.db", "servidor/fenix.db"]:
        if os.path.exists(db_name):
            out_name = os.path.join("database", f"dump_{os.path.basename(db_name)}.sql")
            try:
                sconn = sqlite3.connect(db_name)
                with open(out_name, "w", encoding="utf-8") as f:
                    for line in sconn.iterdump():
                        f.write(f"{line}\n")
                sconn.close()
                print(f"Exported {db_name} -> {out_name} ({os.path.getsize(out_name)} bytes)")
            except Exception as e:
                print(f"Error exporting {db_name}: {e}")

if __name__ == "__main__":
    export_postgres()
    export_sqlite()
