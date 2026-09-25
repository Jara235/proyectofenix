import sqlite3

db = r'c:\Users\JOSE\Desktop\Proyecto fenix\fenix_v2.db'
c = sqlite3.connect(db)
cur = c.cursor()

# Normalize gasolina_consumos semana from int to "Semana XX"
cur.execute("SELECT COUNT(*) FROM gasolina_consumos WHERE semana NOT LIKE 'Semana%'")
print("Rows to fix in gasolina_consumos:", cur.fetchone()[0])

cur.execute("UPDATE gasolina_consumos SET semana = 'Semana ' || CAST(CAST(semana AS INTEGER) AS TEXT) WHERE semana NOT LIKE 'Semana%'")
print("Updated gasolina_consumos:", cur.rowcount)

# Normalize gasolina_facturas semana
cur.execute("SELECT COUNT(*) FROM gasolina_facturas WHERE semana NOT LIKE 'Semana%'")
print("Rows to fix in gasolina_facturas:", cur.fetchone()[0])

cur.execute("UPDATE gasolina_facturas SET semana = 'Semana ' || CAST(CAST(semana AS INTEGER) AS TEXT) WHERE semana NOT LIKE 'Semana%'")
print("Updated gasolina_facturas:", cur.rowcount)

# Normalize gasolina_autorizaciones semana
cur.execute("PRAGMA table_info(gasolina_autorizaciones)")
cols = [r[1] for r in cur.fetchall()]
if 'semana' in cols:
    cur.execute("SELECT COUNT(*) FROM gasolina_autorizaciones WHERE semana NOT LIKE 'Semana%'")
    print("Rows to fix in gasolina_autorizaciones:", cur.fetchone()[0])
    cur.execute("UPDATE gasolina_autorizaciones SET semana = 'Semana ' || CAST(CAST(semana AS INTEGER) AS TEXT) WHERE semana NOT LIKE 'Semana%'")
    print("Updated gasolina_autorizaciones:", cur.rowcount)

# Normalize gasolina_estados_cuenta semana
cur.execute("PRAGMA table_info(gasolina_estados_cuenta)")
cols = [r[1] for r in cur.fetchall()]
if 'semana' in cols:
    cur.execute("SELECT COUNT(*) FROM gasolina_estados_cuenta WHERE semana NOT LIKE 'Semana%'")
    print("Rows to fix in gasolina_estados_cuenta:", cur.fetchone()[0])
    cur.execute("UPDATE gasolina_estados_cuenta SET semana = 'Semana ' || CAST(CAST(semana AS INTEGER) AS TEXT) WHERE semana NOT LIKE 'Semana%'")
    print("Updated gasolina_estados_cuenta:", cur.rowcount)

c.commit()

# Verify
for t in ['gasolina_consumos','gasolina_facturas']:
    cur.execute(f"SELECT DISTINCT semana FROM {t} ORDER BY semana")
    print(f"{t}.semana:", [r[0] for r in cur.fetchall()])

c.close()
print("Done.")
