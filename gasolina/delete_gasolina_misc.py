import sqlite3
conn = sqlite3.connect('fenix.db')
cur = conn.cursor()

print("Borrando Gasolina de fenix_movimientos_combustible...")
cur.execute("DELETE FROM fenix_movimientos_combustible WHERE tipo_combustible='Gasolina'")
print(f"Borradas {cur.rowcount} filas.")
conn.commit()

# Revisar los kpis en totals de api
cur.execute("SELECT tipo_combustible, COUNT(*) FROM fenix_movimientos_combustible GROUP BY tipo_combustible")
print("Combustibles restantes en fenix_movimientos_combustible:")
for row in cur.fetchall():
    print(row)

conn.close()
