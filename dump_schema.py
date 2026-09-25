import sqlite3

db = r'c:\Users\JOSE\Desktop\Proyecto fenix\fenix_v2.db'
c = sqlite3.connect(db)
cur = c.cursor()

cur.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
for row in cur.fetchall():
    print(f"-- Table: {row[0]}")
    print(row[1])
    print()

c.close()
