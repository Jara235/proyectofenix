import sqlite3
conn = sqlite3.connect(r'c:\Users\JOSE\Desktop\Proyecto fenix\fenix.db')
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%gas%' ORDER BY name")
for t in [r[0] for r in cur.fetchall()]:
    print(f"\nTable: {t}")
    for c in cur.execute(f"PRAGMA table_info({t})"):
        print(f"  {c[1]} ({c[2]})")
