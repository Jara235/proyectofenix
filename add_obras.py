import psycopg2
conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor()
nuevas_obras = [
    ('PAH', 'Planta Asfalto Huixquilucan'),
    ('PAP', 'Planta Asfalto Pegaso'),
    ('TP', 'Tanque Pegaso'),
    ('MP', 'Maquinaria Pegaso')
]
for c, n in nuevas_obras:
    try:
        cur.execute("INSERT INTO catalogos.obras (codigo, nombre) VALUES (%s, %s)", (c, n))
    except Exception as e:
        conn.rollback()
conn.commit()
print('Obras agregadas')
