import psycopg2
conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor()

try:
    cur.execute("INSERT INTO catalogos.equipos (numero_economico, descripcion) VALUES ('PL-01', 'PAYLOADER')")
    conn.commit()
    print("PAYLOADER agregado exitosamente con PL-01")
except Exception as e:
    conn.rollback()
    print("Error:", e)
