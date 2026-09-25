import psycopg2
from psycopg2.extras import DictCursor

def check_gasolina_auth():
    conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
    cur = conn.cursor(cursor_factory=DictCursor)

    cur.execute("SELECT * FROM catalogos.autorizaciones WHERE tipo ILIKE '%GASOLINA%' OR tipo IS NULL OR tipo = '' ORDER BY semana, referencia")
    rows = cur.fetchall()

    print(f"Total Gasoline Auth Rows: {len(rows)}")
    for r in rows:
        print(f"Semana: {r['semana']} | Ref: '{r['referencia']}' | Tipo: {r['tipo']} | Auth: {r['litros_autorizados']}")

    conn.close()

if __name__ == '__main__':
    check_gasolina_auth()
