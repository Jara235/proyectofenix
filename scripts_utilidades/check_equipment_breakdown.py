import psycopg2
from psycopg2.extras import DictCursor
import pandas as pd

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

print("=== EQUIPOS DIESEL MÉXICO-TOLUCA ===")
cur.execute("""
    SELECT equipo, COUNT(*) as cargas, SUM(litros) as total_litros, SUM(importe_total) as total_importe
    FROM diesel.consumos
    WHERE obra_destino ILIKE '%TOLUCA%' AND obra_destino NOT ILIKE '%BACHEO%'
    GROUP BY equipo
    ORDER BY total_litros DESC;
""")
for r in cur.fetchall():
    print(dict(r))

print("\n=== EQUIPOS DIESEL LERMA-TRES MARÍAS ===")
cur.execute("""
    SELECT equipo, COUNT(*) as cargas, SUM(litros) as total_litros, SUM(importe_total) as total_importe
    FROM diesel.consumos
    WHERE obra_destino ILIKE '%LERMA%'
    GROUP BY equipo
    ORDER BY total_litros DESC;
""")
for r in cur.fetchall():
    print(dict(r))

print("\n=== VEHÍCULOS GASOLINA MÉXICO-TOLUCA ===")
cur.execute("""
    SELECT vehiculo, conductor, COUNT(*) as cargas, SUM(litros) as total_litros, SUM(importe_total) as total_importe
    FROM gasolina.consumos
    WHERE (obra_destino ILIKE '%TOLUCA%' AND obra_destino NOT ILIKE '%BACHEO%')
      AND (costo_por_litro > 0 OR importe_total > 0)
      AND (vehiculo != 'S/P' OR vehiculo IS NULL)
    GROUP BY vehiculo, conductor
    ORDER BY total_litros DESC;
""")
for r in cur.fetchall():
    print(dict(r))

print("\n=== VEHÍCULOS GASOLINA LERMA-TRES MARÍAS ===")
cur.execute("""
    SELECT vehiculo, conductor, COUNT(*) as cargas, SUM(litros) as total_litros, SUM(importe_total) as total_importe
    FROM gasolina.consumos
    WHERE obra_destino ILIKE '%LERMA%'
      AND (costo_por_litro > 0 OR importe_total > 0)
      AND (vehiculo != 'S/P' OR vehiculo IS NULL)
    GROUP BY vehiculo, conductor
    ORDER BY total_litros DESC;
""")
for r in cur.fetchall():
    print(dict(r))

conn.close()
