import sqlite3, os

db_path = 'c:/Users/JOSE/Desktop/Proyecto fenix/fenix_v2.db'
schema_path = 'c:/Users/JOSE/Desktop/Proyecto fenix/fenix_v2_schema.sql'

# Initialize DB with schema
if not os.path.exists(db_path):
    db = sqlite3.connect(db_path)
    with open(schema_path, 'r', encoding='utf-8') as f:
        db.executescript(f.read())
    db.commit()
    db.close()
    print('Initialized fenix_v2.db')
else:
    print('fenix_v2.db already exists, skipping initialization')

