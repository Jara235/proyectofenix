import psycopg2
from psycopg2.extras import DictCursor

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

# Ver constraints de la tabla
cur.execute("""
    SELECT constraint_name, constraint_type 
    FROM information_schema.table_constraints 
    WHERE table_schema='diesel' AND table_name='control_vales_jalisco'
""")
print("Constraints:", cur.fetchall())

cur.execute("SELECT * FROM diesel.control_vales_jalisco ORDER BY semana")
print("Datos actuales:", cur.fetchall())
conn.close()
