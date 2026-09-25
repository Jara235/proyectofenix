import sqlite3

db = r'c:\Users\JOSE\Desktop\Proyecto fenix\fenix_v2.db'
c = sqlite3.connect(db)
cur = c.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
print("=== TABLAS EN fenix_v2.db ===")
for r in cur.fetchall():
    print(" - " + r[0])

cur.execute("SELECT COUNT(*) FROM gasolina_estados_cuenta")
print("\nRegistros en gasolina_estados_cuenta:", cur.fetchone()[0])
c.close()
