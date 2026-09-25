import sqlite3
db = r'c:\Users\JOSE\Desktop\Proyecto fenix\fenix_v2.db'
c = sqlite3.connect(db)
cur = c.cursor()

# Check how semana is stored in each table
for t in ['diesel_consumos','diesel_facturas','gasolina_consumos','gasolina_facturas']:
    cur.execute(f"SELECT DISTINCT semana FROM {t} ORDER BY semana LIMIT 10")
    rows = [r[0] for r in cur.fetchall()]
    print(f"{t}.semana: {rows}")
    
# Check the /api/semanas endpoint data
cur.execute("SELECT DISTINCT semana FROM diesel_consumos ORDER BY semana")
print("Semanas type sample:", type(cur.fetchone()[0]))
c.close()
