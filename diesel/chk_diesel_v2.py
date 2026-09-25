import sqlite3
db = r'c:\Users\JOSE\Desktop\Proyecto fenix\fenix_v2.db'
c = sqlite3.connect(db)
cur = c.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
print('Tables:', [r[0] for r in cur.fetchall()])
for t in ['diesel_consumos','diesel_facturas']:
    cur.execute(f"PRAGMA table_info({t})")
    cols = [r[1] for r in cur.fetchall()]
    print(f"\n{t} cols: {cols}")
    cur.execute(f"SELECT COUNT(*), COALESCE(SUM(importe_total),0) FROM {t}")
    cnt, total = cur.fetchone()
    print(f"  count={cnt}  total={total:,.2f}")
cur.execute("SELECT DISTINCT origen FROM diesel_consumos LIMIT 20")
print("origenes diesel consumos:", [r[0] for r in cur.fetchall()])
cur.execute("SELECT DISTINCT proveedor FROM diesel_facturas LIMIT 20")
print("proveedores diesel facturas:", [r[0] for r in cur.fetchall()])
c.close()
