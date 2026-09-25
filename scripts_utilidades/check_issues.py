import sqlite3
db = sqlite3.connect('c:/Users/JOSE/Desktop/Proyecto fenix/fenix_v2.db')

# Check folio semana inconsistency - 'Semana 27' vs '28' (no prefix)
print('=== Semanas sin formato uniforme ===')
rows = db.execute("SELECT DISTINCT semana FROM diesel_consumos ORDER BY semana").fetchall()
for r in rows:
    print(f"  '{r[0]}'")
print()

# importe_total nulls?
nulls = db.execute("SELECT COUNT(*) FROM diesel_consumos WHERE importe_total IS NULL OR importe_total=0").fetchone()[0]
total = db.execute("SELECT COUNT(*) FROM diesel_consumos").fetchone()[0]
print(f'Records with NULL/0 importe: {nulls}/{total}')

# Check if costo_por_litro is filled
null_price = db.execute("SELECT COUNT(*) FROM diesel_consumos WHERE costo_por_litro IS NULL OR costo_por_litro=0").fetchone()[0]
print(f'Records with NULL/0 costo_por_litro: {null_price}/{total}')

db.close()
