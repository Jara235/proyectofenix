import sqlite3

try:
    c = sqlite3.connect(r'c:\Users\JOSE\Desktop\Proyecto fenix\fenix.db')
    cur = c.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    print("Tablas en fenix.db:")
    for r in cur.fetchall():
        print(r[0])
except Exception as e:
    print(e)
