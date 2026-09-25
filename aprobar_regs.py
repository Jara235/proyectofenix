import psycopg2
conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor()
cur.execute("UPDATE diesel.facturas SET estatus_revision = 'APROBADO' WHERE estatus_revision = 'PENDIENTE'")
print(f'Facturas aprobadas: {cur.rowcount}')
cur.execute("UPDATE diesel.consumos SET estatus_revision = 'APROBADO' WHERE estatus_revision = 'PENDIENTE'")
print(f'Consumos aprobados: {cur.rowcount}')
conn.commit()
