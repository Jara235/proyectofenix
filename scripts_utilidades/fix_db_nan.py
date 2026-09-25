import psycopg2
conn=psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
conn.autocommit = True
cur=conn.cursor()

cur.execute("UPDATE diesel.solicitudes SET estatus_conciliacion = 'PENDIENTE' WHERE estatus_conciliacion = 'NaN' OR estatus_conciliacion IS NULL;")
cur.execute("UPDATE diesel.solicitudes SET solicitante = NULL WHERE solicitante = 'NaN';")
cur.execute("UPDATE diesel.solicitudes SET equipo = NULL WHERE equipo = 'NaN';")
cur.execute("UPDATE diesel.solicitudes SET equipo_economico = NULL WHERE equipo_economico = 'NaN';")
cur.execute("UPDATE diesel.solicitudes SET responsable = NULL WHERE responsable = 'NaN';")
cur.execute("UPDATE diesel.solicitudes SET operador = NULL WHERE operador = 'NaN';")
cur.execute("UPDATE diesel.solicitudes SET observaciones = NULL WHERE observaciones = 'NaN';")

print("Datos arreglados en diesel.solicitudes")
