import sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

conn = sqlite3.connect('fenix.db')
cur = conn.cursor()

print("=== CONSUMOS DIESEL SIN OBRA ASIGNADA ===")
print(f"{'Folio':<20} {'Fecha':<12} {'Origen':<18} {'Equipo/Destino':<35} {'Litros':>8} {'Semana':>7}")
print("-"*102)
cur.execute("""
    SELECT folio_vale, fecha, semana, origen_nombre, destino_nombre, litros
    FROM fenix_movimientos_combustible
    WHERE tipo_movimiento='CONSUMO' AND obra_id IS NULL
    ORDER BY semana, fecha
""")
for r in cur.fetchall():
    print(f"  {str(r[0]):<18} {str(r[1]):<12} {str(r[2]):<6} {str(r[3]):<18} {str(r[4]):<35} {float(r[5] or 0):>8.1f}")

print()
cur.execute("SELECT COUNT(*), ROUND(SUM(litros),1) FROM fenix_movimientos_combustible WHERE tipo_movimiento='CONSUMO' AND obra_id IS NULL")
r = cur.fetchone()
print(f"  TOTAL: {r[0]} registros = {r[1]} litros sin obra asignada")

print()
print("=== CONSUMOS POR SEMANA (TODOS) ===")
cur.execute("""
    SELECT m.semana,
           COALESCE(o.nombre,'-- SIN OBRA --') as obra,
           ROUND(SUM(m.litros),1) as litros,
           COUNT(*) as regs
    FROM fenix_movimientos_combustible m
    LEFT JOIN fenix_obras o ON o.id = m.obra_id
    WHERE m.tipo_movimiento = 'CONSUMO'
    GROUP BY m.semana, m.obra_id
    ORDER BY m.semana, litros DESC
""")
sem_actual = None
for r in cur.fetchall():
    if r[0] != sem_actual:
        print(f"\n  --- SEMANA {r[0]} ---")
        sem_actual = r[0]
    print(f"    {str(r[1]):<35} {r[2]:>8.1f} L  ({r[3]} registros)")
conn.close()
