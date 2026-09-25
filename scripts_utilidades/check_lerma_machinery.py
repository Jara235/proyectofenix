import psycopg2
from psycopg2.extras import DictCursor
import pandas as pd

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

print("=== MAQUINARIA REGISTRADA EN DIESEL (LERMA - TRES MARÍAS) ===")
cur.execute("""
    SELECT DISTINCT equipo_maquinaria, obra_destino, COUNT(*) as tickets, SUM(litros) as total_litros
    FROM diesel.consumos
    WHERE LOWER(obra_destino) LIKE '%lerma%'
    GROUP BY equipo_maquinaria, obra_destino
    ORDER BY total_litros DESC;
""")
rows = cur.fetchall()
for r in rows:
    print(f"Equipo: {r['equipo_maquinaria']} | Tickets: {r['tickets']} | Litros: {r['total_litros']}")

print("\n=== CATÁLOGO DE MAQUINARIA DISPONIBLE ===")
cur.execute("""
    SELECT DISTINCT equipo_maquinaria, tipo_equipo, consumo_prom_hora 
    FROM catalogos.maquinaria_equipos
    LIMIT 20;
""")
try:
    cats = cur.fetchall()
    for c in cats:
        print(dict(c))
except Exception as e:
    print("Catalog query error/table not found, checking raw distinct:", e)
    cur.execute("SELECT DISTINCT equipo_maquinaria FROM diesel.consumos;")
    all_eq = cur.fetchall()
    for eq in all_eq:
        print(eq[0])

conn.close()
