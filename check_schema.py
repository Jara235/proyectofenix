from app_admin import get_db

db = get_db()
cur = db.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_schema = 'tags' AND table_name = 'movimientos'
    ORDER BY ordinal_position;
""")
print("=== Columns of tags.movimientos ===")
for col in cur.fetchall():
    print(dict(col))

cur = db.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_schema = 'tags' AND table_name = 'autorizaciones'
    ORDER BY ordinal_position;
""")
print("\n=== Columns of tags.autorizaciones ===")
for col in cur.fetchall():
    print(dict(col))

db.close()
