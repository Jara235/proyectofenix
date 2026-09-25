import sqlite3
conn = sqlite3.connect(r'c:\Users\JOSE\Desktop\Proyecto fenix\fenix.db')
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [r[0] for r in cur.fetchall()]
print(tables)
