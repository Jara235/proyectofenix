import os, re, psycopg2
from psycopg2.extras import DictCursor

# Buscar en base de datos
conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

# Ver tablas en la BD
cur.execute("""
    SELECT table_schema, table_name 
    FROM information_schema.tables 
    WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
    ORDER BY table_schema, table_name;
""")
tables = cur.fetchall()
print("=== TABLAS EN LA BASE DE DATOS ===")
for t in tables:
    print(f"  {t['table_schema']}.{t['table_name']}")

# Buscar referencias a tags o bryan en las tablas
print("\n=== BUSCANDO 'BRYAN' EN TABLAS ===")
for t in tables:
    s = t['table_schema']
    tb = t['table_name']
    try:
        cur.execute(f"SELECT * FROM {s}.{tb} LIMIT 1;")
        cols = [desc[0] for desc in cur.description]
        text_cols = []
        for c in cols:
            # check if string column
            text_cols.append(c)
        if text_cols:
            where_clauses = [f"CAST({c} AS TEXT) ILIKE '%BRYAN%'" for c in text_cols]
            q = f"SELECT * FROM {s}.{tb} WHERE " + " OR ".join(where_clauses) + " LIMIT 10;"
            cur.execute(q)
            res = cur.fetchall()
            if res:
                print(f"\n>> Coincidencia en {s}.{tb} ({len(res)} registros):")
                for r in res:
                    print(dict(r))
    except Exception as e:
        conn.rollback()
