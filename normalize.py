import psycopg2

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor()

tables = [
    'diesel.consumos', 'diesel.facturas', 'diesel.solicitudes',
    'gasolina.consumos', 'gasolina.facturas'
]

for t in tables:
    cur.execute(f"UPDATE {t} SET semana = REPLACE(semana, 'Semana ', '') WHERE semana LIKE 'Semana %'")

conn.commit()
print("Database normalized.")
