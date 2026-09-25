import psycopg2
from psycopg2.extras import DictCursor
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 1000)

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

print("=== REGISTROS ACTUALES EN CATALOGOS.OBRAS ===")
cur.execute("SELECT * FROM catalogos.obras ORDER BY LOWER(nombre);")
rows = cur.fetchall()
df_obras = pd.DataFrame([dict(r) for r in rows])
print(df_obras)

print(f"\nTotal registros en catalogos.obras: {len(df_obras)}")

print("\n=== TODAS LAS TABLAS QUE USAN OBRAS / OBRA_DESTINO / OBRA ===")
cur.execute("""
    SELECT table_schema, table_name, column_name 
    FROM information_schema.columns 
    WHERE column_name ILIKE '%obra%'
    ORDER BY table_schema, table_name;
""")
for r in cur.fetchall():
    print(dict(r))

print("\n=== VALORES DISTINTOS EN DIESEL.CONSUMOS.OBRA_DESTINO ===")
cur.execute("""
    SELECT obra_destino, COUNT(*) as registros, SUM(litros) as total_litros 
    FROM diesel.consumos 
    GROUP BY obra_destino 
    ORDER BY LOWER(obra_destino);
""")
for r in cur.fetchall():
    print(dict(r))

print("\n=== VALORES DISTINTOS EN GASOLINA.REGISTROS / CONSUMOS (si existen) ===")
cur.execute("""
    SELECT table_schema, table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'gasolina';
""")
gas_tables = cur.fetchall()
print("Tablas en schema gasolina:", [dict(t) for t in gas_tables])

for t in gas_tables:
    tname = t['table_name']
    try:
        cur.execute(f"SELECT obra_destino, COUNT(*) FROM gasolina.{tname} GROUP BY obra_destino;")
        print(f"Valores en gasolina.{tname}:", [dict(r) for r in cur.fetchall()])
    except Exception as e:
        pass

conn.close()
