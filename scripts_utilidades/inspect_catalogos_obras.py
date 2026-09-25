import psycopg2
from psycopg2.extras import DictCursor
import pandas as pd

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

print("=== ESTRUCTURA DE TABLA CATALOGOS.OBRAS ===")
cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_schema = 'catalogos' AND table_name = 'obras'
    ORDER BY ordinal_position;
""")
for r in cur.fetchall():
    print(r)

print("\n=== REGISTROS ACTUALES EN CATALOGOS.OBRAS ===")
cur.execute("SELECT * FROM catalogos.obras ORDER BY id;")
rows = cur.fetchall()
df_obras = pd.DataFrame([dict(r) for r in rows])
print(df_obras.to_string())

print("\n=== OBRAS REFERENCIADAS EN DIESEL.CONSUMOS ===")
cur.execute("""
    SELECT obra_destino, COUNT(*) as conteo, SUM(litros) as total_litros 
    FROM diesel.consumos 
    GROUP BY obra_destino 
    ORDER BY obra_destino;
""")
for r in cur.fetchall():
    print(dict(r))

print("\n=== OBRAS REFERENCIADAS EN GASOLINA.CONSUMOS (si existe) ===")
try:
    cur.execute("""
        SELECT obra_destino, COUNT(*) as conteo 
        FROM gasolina.consumos 
        GROUP BY obra_destino 
        ORDER BY obra_destino;
    """)
    for r in cur.fetchall():
        print(dict(r))
except Exception as e:
    print("Gasolina error:", e)

conn.close()
