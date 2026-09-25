import sys, psycopg2, psycopg2.extras
sys.path.append(r'c:\Users\JOSE\Desktop\Proyecto fenix')

conn = psycopg2.connect(
    host='localhost', port=5432,
    dbname='fenix_db', user='postgres', password='admin',
    options='-c search_path=public'
)
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

tables = [
    ('diesel', 'solicitudes'),
    ('diesel', 'facturas'),
    ('diesel', 'consumos'),
    ('gasolina', 'consumos'),
    ('gasolina', 'facturas'),
]
for schema, table in tables:
    try:
        cur.execute("SELECT COUNT(*) as n FROM " + schema + "." + table + " WHERE semana::text ILIKE 'Semana%'")
        row = cur.fetchone()
        n = row['n']
        if n > 0:
            print("DIRTY: " + schema + "." + table + " -> " + str(n) + " filas")
            cur.execute("SELECT DISTINCT semana FROM " + schema + "." + table + " WHERE semana::text ILIKE 'Semana%' LIMIT 5")
            for s in cur.fetchall():
                print("  -> " + str(s['semana']))
        else:
            print("OK: " + schema + "." + table)
    except Exception as e:
        print("Error: " + schema + "." + table + " - " + str(e))
        conn.rollback()
cur.close()
conn.close()
