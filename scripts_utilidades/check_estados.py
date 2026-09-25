import sqlite3
db = r'c:\Users\JOSE\Desktop\Proyecto fenix\fenix_v2.db'
c = sqlite3.connect(db)
cur = c.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cur.fetchall()
for t in tables:
    if 'estad' in t[0] or 'cuenta' in t[0]:
        print("Found table:", t[0])
        cur.execute(f"PRAGMA table_info({t[0]})")
        cols = cur.fetchall()
        print(" Columns:", [col[1] for col in cols])
c.close()
