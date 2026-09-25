import psycopg2
from psycopg2.extras import DictCursor

def check_autorizaciones():
    conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
    cur = conn.cursor(cursor_factory=DictCursor)

    cur.execute("SELECT * FROM catalogos.autorizaciones ORDER BY semana, referencia")
    rows = cur.fetchall()

    print("=== CATALOGOS.AUTORIZACIONES ===")
    for r in rows:
        print(f"Semana: {r['semana']} | Referencia: '{r['referencia']}' | Tipo: {r['tipo']} | Litros/Monto: {r['litros_autorizados']}")

    conn.close()

if __name__ == '__main__':
    check_autorizaciones()
