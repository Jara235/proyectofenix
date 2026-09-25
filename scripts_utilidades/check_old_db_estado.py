import sqlite3

try:
    c = sqlite3.connect(r'c:\Users\JOSE\Desktop\Proyecto fenix\fenix.db')
    cur = c.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%estado%'")
    print("Tablas en fenix.db con estado:", [r[0] for r in cur.fetchall()])
    c.close()
except Exception as e:
    print(e)
