import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

try:
    # Conectar a la base por defecto
    conn = psycopg2.connect(dbname='postgres', user='postgres', password='Bupito*268', host='localhost')
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    # Crear la base de datos
    cur.execute("SELECT 1 FROM pg_database WHERE datname='fenix_db'")
    if not cur.fetchone():
        cur.execute('CREATE DATABASE fenix_db')
        print("Base de datos 'fenix_db' creada exitosamente.")
    else:
        print("La base de datos 'fenix_db' ya existe.")
    cur.close()
    conn.close()
    
    # Probar conexión a la nueva base
    conn2 = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
    print("Conexión a 'fenix_db' exitosa.")
    conn2.close()

except Exception as e:
    print(f"Error: {e}")
