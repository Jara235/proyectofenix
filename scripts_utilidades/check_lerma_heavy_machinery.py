import psycopg2
from psycopg2.extras import DictCursor

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

print("=== EQUIPOS EN DIESEL.CONSUMOS CON LERMA ===")
cur.execute("""
    SELECT DISTINCT equipo, equipo_economico, COUNT(*) as cargas, SUM(litros) as total_litros
    FROM diesel.consumos
    WHERE LOWER(obra_destino) LIKE '%lerma%'
    GROUP BY equipo, equipo_economico
    ORDER BY total_litros DESC;
""")
for r in cur.fetchall():
    print(dict(r))

print("\n=== TODOS LOS EQUIPOS DE PAVIMENTACION/ASFALTO REGISTRADOS ===")
cur.execute("""
    SELECT DISTINCT equipo, COUNT(*) as cargas, SUM(litros) as total_litros
    FROM diesel.consumos
    WHERE LOWER(equipo) LIKE '%vogele%' 
       OR LOWER(equipo) LIKE '%perfiladora%' 
       OR LOWER(equipo) LIKE '%rodatec%' 
       OR LOWER(equipo) LIKE '%hamm%' 
       OR LOWER(equipo) LIKE '%caterpillar%'
       OR LOWER(equipo) LIKE '%volvo%'
       OR LOWER(equipo) LIKE '%dynapac%'
       OR LOWER(equipo) LIKE '%dinapac%'
       OR LOWER(equipo) LIKE '%retroexcavadora%'
       OR LOWER(equipo) LIKE '%case%'
       OR LOWER(equipo) LIKE '%barredora%'
       OR LOWER(equipo) LIKE '%laymor%'
       OR LOWER(equipo) LIKE '%broom%'
    GROUP BY equipo
    ORDER BY total_litros DESC;
""")
for r in cur.fetchall():
    print(dict(r))

conn.close()
