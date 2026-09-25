import psycopg2
from psycopg2.extras import DictCursor
import pandas as pd

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

cur.execute("SELECT codigo, nombre, ingeniero_responsable, responsable_default FROM catalogos.obras ORDER BY codigo;")
rows = cur.fetchall()

df = pd.DataFrame([dict(r) for r in rows])
print(df.to_string())

conn.close()
