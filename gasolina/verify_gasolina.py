import sys, io, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
conn = sqlite3.connect('fenix.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()
print("=== RESPONSABLES EN PRESUPUESTOS ===")
cur.execute("SELECT DISTINCT responsable FROM fenix_gas_presupuestos ORDER BY responsable")
for r in cur.fetchall():
    print(' ', r[0])
print()
print("=== PRESUPUESTOS POR RESPONSABLE (resumen) ===")
cur.execute("SELECT responsable, COUNT(*) as n, SUM(monto_autorizado) as total FROM fenix_gas_presupuestos GROUP BY responsable ORDER BY total DESC")
for r in cur.fetchall():
    print(f"  {r['responsable']}: {r['n']} unidades, ${r['total']:.2f}")
print()
print("=== TOTALES POR SEMANA ===")
cur.execute("SELECT SUM(monto_autorizado) as total FROM fenix_gas_presupuestos")
print("  Total Autorizado:", cur.fetchone()['total'])
cur.execute("SELECT SUM(monto_reportado) as total FROM fenix_gas_reportes_diarios")
print("  Total Consumido Reportado:", cur.fetchone()['total'])
cur.execute("SELECT SUM(litros) as lts, SUM(importe) as imp FROM fenix_gas_tickets_reales")
r = cur.fetchone()
print(f"  Total Tickets Reales: {r['lts']} L / ${r['imp']:.2f}")
conn.close()
