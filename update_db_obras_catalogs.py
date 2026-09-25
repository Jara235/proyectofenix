import psycopg2
from psycopg2.extras import DictCursor
import sqlite3

active_obras = [
    ("MT", "México - Toluca", "Francisco Javier", "Francisco Javier"),
    ("L3M", "Lerma - Tres Marías", "Apolinar", "Apolinar"),
    ("CL", "Chamapa - Lechería", "Sin responsable", "Sin responsable"),
    ("BT", "Bacheo Toluca", "Diego Carreola", "Diego Carreola"),
    ("PAH", "Planta Huixquilucan", "Luis", "Luis"),
    ("PPE", "Planta Pegaso", "Jack", "Jack"),
    ("DES", "Desasolve", "Diego Carreola", "Diego Carreola"),
    ("PRO", "Providencia", "Samuel", "Samuel"),
    ("ADM", "Alfredo del Mazo", "Variable", "Variable"),
    ("COLMIL", "Colegio Militar", "Apolinar", "Apolinar"),
    ("EXPL", "Explanada Damián Carmona", "Sin responsable", "Sin responsable"),
    ("CALL", "Calle Revolución y Calle Lerdo", "Sin responsable", "Sin responsable"),
    ("CONST", "Constitución", "Sin responsable", "Sin responsable"),
]

def update_postgres():
    print("=== ACTUALIZANDO POSTGRESQL (fenix_db) ===")
    conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
    cur = conn.cursor()
    
    # 1. Truncar / Limpiar tabla de catálogo de obras en Postgres
    cur.execute("DELETE FROM catalogos.obras")
    
    # 2. Insertar las 13 obras limpias
    for codigo, nombre, ing_resp, resp_def in active_obras:
        cur.execute("""
            INSERT INTO catalogos.obras (codigo, nombre, ingeniero_responsable, responsable_default)
            VALUES (%s, %s, %s, %s)
        """, (codigo, nombre, ing_resp, resp_def))
    
    conn.commit()
    print("PostgreSQL catalogos.obras actualizado exitosamente con 13 obras.")
    conn.close()

def update_sqlite(db_name):
    print(f"=== ACTUALIZANDO SQLITE ({db_name}) ===")
    try:
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
        
        # Verificar nombre de la tabla
        tables = [t[0] for t in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        tbl = None
        if 'catalogos_obras' in tables:
            tbl = 'catalogos_obras'
        elif 'obras' in tables:
            tbl = 'obras'
            
        if tbl:
            cur.execute(f"DELETE FROM {tbl}")
            for codigo, nombre, ing_resp, resp_def in active_obras:
                cur.execute(f"""
                    INSERT INTO {tbl} (codigo, nombre, ingeniero_responsable, responsable_default)
                    VALUES (?, ?, ?, ?)
                """, (codigo, nombre, ing_resp, resp_def))
            conn.commit()
            print(f"SQLite {db_name} -> {tbl} actualizado con 13 obras.")
        else:
            print(f"No se encontró tabla de obras en {db_name}.")
            
        conn.close()
    except Exception as e:
        print(f"Error en SQLite {db_name}: {e}")

if __name__ == "__main__":
    update_postgres()
    update_sqlite("fenix_v2.db")
    update_sqlite("fenix.db")
    print("\n[OK] Todas las bases de datos han sido actualizadas con las 13 obras limpias y activas.")
