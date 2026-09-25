import psycopg2
from psycopg2.extras import DictCursor

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

for tbl in ['autorizaciones_semanal', 'autorizaciones', 'autorizaciones_maestro', 'estados_cuenta']:
    print(f"\n=== COLUMNAS DE gasolina.{tbl} ===")
    cur.execute(f"""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema = 'gasolina' AND table_name = '{tbl}'
    """)
    cols = [f"{r[0]} ({r[1]})" for r in cur.fetchall()]
    print(', '.join(cols))
    
    print(f"--- Muestra de {tbl} para Semana 33 o recientes ---")
    try:
        cur.execute(f"SELECT * FROM gasolina.{tbl} ORDER BY 1 DESC LIMIT 3")
        for r in cur.fetchall():
            print(dict(r))
    except Exception as e:
        print("Error al consultar:", e)
