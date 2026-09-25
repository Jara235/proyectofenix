import psycopg2
from psycopg2.extras import DictCursor

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

tables = [
    ('catalogos', 'obras'),
    ('diesel', 'consumos'),
    ('diesel', 'facturas'),
    ('gasolina', 'consumos'),
    ('gasolina', 'facturas')
]

for schema, tbl in tables:
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema = %s AND table_name = %s
        ORDER BY ordinal_position;
    """, (schema, tbl))
    cols = [f"{r['column_name']} ({r['data_type']})" for r in cur.fetchall()]
    print(f"\n=== {schema}.{tbl} ===")
    print(", ".join(cols))

conn.close()
