import psycopg2
from psycopg2.extras import DictCursor

conn = psycopg2.connect(
    dbname="fenix_db",
    user="postgres",
    password="Bupito*268",
    host="localhost"
)
cur = conn.cursor(cursor_factory=DictCursor)

cur.execute("""
    SELECT table_schema, table_name 
    FROM information_schema.tables 
    WHERE table_schema NOT IN ('information_schema', 'pg_catalog') 
    ORDER BY table_schema, table_name;
""")
tables = cur.fetchall()
print("Total tables:", len(tables))
for t in tables:
    cur.execute(f"SELECT COUNT(*) as c FROM {t['table_schema']}.{t['table_name']}")
    cnt = cur.fetchone()['c']
    print(f"- {t['table_schema']}.{t['table_name']}: {cnt} rows")

cur.close()
conn.close()
