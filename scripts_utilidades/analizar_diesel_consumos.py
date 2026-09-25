import psycopg2
from psycopg2.extras import DictCursor

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

print("=== 1. DIESEL CONSUMOS POR SEMANA ===")
cur.execute("""
    SELECT semana, count(*) as total_cargas, sum(litros) as total_litros, count(DISTINCT equipo_economico) as total_equipos
    FROM diesel.consumos
    GROUP BY semana
    ORDER BY semana;
""")
for r in cur.fetchall():
    tot_l = float(r['total_litros'] or 0)
    print(f"Semana {str(r['semana']):<5} | Cargas: {r['total_cargas']:<4} | Litros: {tot_l:>10.2f} L | Equipos Unicos: {r['total_equipos']}")

print("\n=== 2. TOP 20 EQUIPOS CON MAYOR CONSUMO DE DIESEL ===")
cur.execute("""
    SELECT equipo_economico, equipo, count(*) as cargas, sum(litros) as total_litros, avg(litros) as prom_por_carga
    FROM diesel.consumos
    WHERE equipo_economico IS NOT NULL AND equipo_economico != ''
    GROUP BY equipo_economico, equipo
    ORDER BY total_litros DESC
    LIMIT 20;
""")
for r in cur.fetchall():
    tot_l = float(r['total_litros'] or 0)
    prom_l = float(r['prom_por_carga'] or 0)
    eq_nom = str(r['equipo'] or '')[:32]
    print(f"{str(r['equipo_economico']):<8} | {eq_nom:<32} | Cargas: {r['cargas']:<3} | Total: {tot_l:>8.2f} L | Prom/Carga: {prom_l:>6.2f} L")

print("\n=== 3. CONSUMOS DE DIESEL POR OBRA ===")
cur.execute("""
    SELECT obra_destino, count(*) as cargas, sum(litros) as total_litros
    FROM diesel.consumos
    WHERE obra_destino IS NOT NULL AND obra_destino != ''
    GROUP BY obra_destino
    ORDER BY total_litros DESC;
""")
for r in cur.fetchall():
    tot_l = float(r['total_litros'] or 0)
    print(f"{str(r['obra_destino']):<35} | Cargas: {r['cargas']:<4} | Total: {tot_l:>10.2f} L")
