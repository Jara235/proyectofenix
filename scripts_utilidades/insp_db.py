import sqlite3
import pandas as pd

conn = sqlite3.connect(r'c:\Users\JOSE\Desktop\Proyecto fenix\fenix.db')
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%gas%' ORDER BY name")
tables = [r[0] for r in cur.fetchall()]
print("Tables with 'gas' in name:", tables)

for t in tables:
    cur.execute(f"PRAGMA table_info({t})")
    cols = cur.fetchall()
    print(f"\nTable {t}:")
    for c in cols:
        print(f"  {c[1]} ({c[2]})")
