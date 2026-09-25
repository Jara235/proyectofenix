import psycopg2

try:
    conn = psycopg2.connect(
        dbname="fenix_db",
        user="postgres",
        password="Bupito*268",
        host="localhost"
    )
    cur = conn.cursor()
    
    # 1. Update obra_destino and responsable for 'Dragones'
    cur.execute('''
        UPDATE diesel.consumos 
        SET obra_destino = 'Bacheo Toluca', 
            responsable = 'Diego carreola' 
        WHERE obra_destino ILIKE '%Dragon%' OR obra_destino ILIKE '%Dragones%'
    ''')
    
    print(f'Filas actualizadas: {cur.rowcount}')
    
    conn.commit()
    cur.close()
    conn.close()
    print('Update successful')
except Exception as e:
    print(f'Error: {e}')
