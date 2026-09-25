import sqlite3
conn = sqlite3.connect('fenix.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("--- Gasolina en fenix_movimientos_combustible ---")
cur.execute("SELECT * FROM fenix_movimientos_combustible WHERE tipo_combustible='Gasolina'")
rows = cur.fetchall()
for i, r in enumerate(rows[:5]):
    print(dict(r))
print(f"Total: {len(rows)}")

print("\n--- fenix_gas_tickets_reales ---")
cur.execute("SELECT COUNT(*) FROM fenix_gas_tickets_reales")
print(f"Total tickets: {cur.fetchone()[0]}")

conn.close()
