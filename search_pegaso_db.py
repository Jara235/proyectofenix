from app_admin import get_db

db = get_db()

print("--- SEARCH TANQUE PEGASO IN DIESEL TABLES ---")
# Check tables in diesel schema
tables = db.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'diesel'").fetchall()
for t in tables:
    tname = t['table_name']
    try:
        rows = db.execute(f"SELECT * FROM diesel.{tname} WHERE CAST(to_jsonb({tname}.*) AS text) ILIKE '%pegaso%' LIMIT 5").fetchall()
        if rows:
            print(f"Table diesel.{tname} has {len(rows)} matching rows:")
            for r in rows:
                print("  ", dict(r))
    except Exception as e:
        # not all tables can be jsonb or might error
        pass

print("\n--- SEARCH IN GASOLINA SCHEMA ---")
gtables = db.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'gasolina'").fetchall()
for t in gtables:
    tname = t['table_name']
    try:
        rows = db.execute(f"SELECT * FROM gasolina.{tname} WHERE CAST(to_jsonb({tname}.*) AS text) ILIKE '%pegaso%' LIMIT 5").fetchall()
        if rows:
            print(f"Table gasolina.{tname} has {len(rows)} matching rows:")
            for r in rows:
                print("  ", dict(r))
    except Exception as e:
        pass

db.close()
