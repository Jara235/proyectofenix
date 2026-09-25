import sqlite3
import psycopg2

def migrate_catalogs():
    try:
        sqlite_conn = sqlite3.connect('fenix.db')
        sqlite_cur = sqlite_conn.cursor()
        
        pg_conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
        pg_cur = pg_conn.cursor()
        
        # 1. Obras (fenix_obras)
        sqlite_cur.execute("SELECT codigo, nombre FROM fenix_obras")
        obras = sqlite_cur.fetchall()
        print(f"Migrando {len(obras)} obras...")
        for o in obras:
            pg_cur.execute(
                "INSERT INTO catalogos.obras (codigo, nombre, ingeniero_responsable, responsable_default) VALUES (%s, %s, '', '')",
                (o[0], o[1])
            )
            
        # 2. Equipos (fenix_equipos)
        sqlite_cur.execute("SELECT numero_economico, descripcion FROM fenix_equipos")
        equipos = sqlite_cur.fetchall()
        print(f"Migrando {len(equipos)} equipos...")
        for e in equipos:
            pg_cur.execute(
                "INSERT INTO catalogos.equipos (numero_economico, descripcion, tipo_equipo, operador_default) VALUES (%s, %s, '', '')",
                (e[0], e[1])
            )

        # 3. Operaciones -> Let's insert default ones
        operaciones = [
            ('CMQ', 'CARGA MAQUINARIA'),
            ('CVJ', 'CARGA VIAJE'),
            ('CPL', 'CARGA PLANTA'),
            ('OTR', 'OTRO')
        ]
        print(f"Migrando {len(operaciones)} operaciones...")
        for o in operaciones:
            pg_cur.execute(
                "INSERT INTO catalogos.operaciones (codigo_operacion, tipo_operacion) VALUES (%s, %s)",
                (o[0], o[1])
            )

        # 4. Operadores -> We might just have string names in the old DB, let's just insert 'Sin Registro' and some defaults if we don't have a table
        pg_cur.execute("INSERT INTO catalogos.operadores (nombre) VALUES ('Sin Registro')")
        
        pg_conn.commit()
        print("¡Migración de catálogos completada exitosamente!")
        
    except Exception as e:
        print("Error:", e)
        if 'pg_conn' in locals():
            pg_conn.rollback()
    finally:
        if 'sqlite_conn' in locals(): sqlite_conn.close()
        if 'pg_conn' in locals(): pg_conn.close()

if __name__ == '__main__':
    migrate_catalogs()
