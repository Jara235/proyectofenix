import psycopg2
from psycopg2.extras import DictCursor

def check_db_conductors():
    conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
    cur = conn.cursor(cursor_factory=DictCursor)

    cur.execute("""
        SELECT DISTINCT conductor, estatus_revision, semana
        FROM gasolina.consumos
        WHERE semana::text = '30'
        ORDER BY conductor
    """)

    rows = cur.fetchall()
    print("=== DISTINCT CONDUCTOR VALUES IN DB FOR SEMANA 30 ===")
    for r in rows:
        print(f"Conductor: '{r['conductor']}' | Estatus: {r['estatus_revision']}")

    cur.execute("SELECT COUNT(*) as total FROM gasolina.consumos WHERE semana::text = '30'")
    print('Total rows in DB for semana 30:', cur.fetchone()['total'])

    cur.execute("SELECT COUNT(*) as apr FROM gasolina.consumos WHERE semana::text = '30' AND estatus_revision = 'APROBADO'")
    print('Approved rows in DB for semana 30:', cur.fetchone()['apr'])

    conn.close()

if __name__ == '__main__':
    check_db_conductors()
