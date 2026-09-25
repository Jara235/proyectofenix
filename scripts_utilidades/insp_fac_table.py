import sqlite3
conn = sqlite3.connect(r'c:\Users\JOSE\Desktop\Proyecto fenix\fenix.db')
cur = conn.cursor()
cur.execute("PRAGMA table_info(fenix_facturas_combustible)")
cols = cur.fetchall()
for c in cols:
    print(f"  {c[1]} ({c[2]})")
