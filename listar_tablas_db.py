import psycopg2
from psycopg2.extras import DictCursor

def list_tables_and_check_route():
    conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
    cur = conn.cursor(cursor_factory=DictCursor)

    cur.execute("""
        SELECT table_schema, table_name 
        FROM information_schema.tables 
        WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
        ORDER BY table_schema, table_name
    """)
    tables = cur.fetchall()
    print("=== TABLES IN DATABASE ===")
    for t in tables:
        print(f" - {t['table_schema']}.{t['table_name']}")

    conn.close()

if __name__ == '__main__':
    list_tables_and_check_route()
