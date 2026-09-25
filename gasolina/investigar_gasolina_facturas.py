import psycopg2
from psycopg2.extras import DictCursor
import os

def check_gasolina_facturas():
    conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
    cur = conn.cursor(cursor_factory=DictCursor)

    # 1. Get columns of gasolina.facturas
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema = 'gasolina' AND table_name = 'facturas'
        ORDER BY ordinal_position
    """)
    cols = cur.fetchall()
    print("=== COLUMNS IN gasolina.facturas ===")
    for c in cols:
        print(f" - {c['column_name']} ({c['data_type']})")

    # 2. Query rows in gasolina.facturas for folio / uuid / pdf
    cur.execute("""
        SELECT *
        FROM gasolina.facturas
        ORDER BY fecha_emision DESC, id DESC
        LIMIT 25
    """)
    rows = [dict(r) for r in cur.fetchall()]
    print(f"\n=== SAMPLE ROWS IN gasolina.facturas (Total sample: {len(rows)}) ===")
    for r in rows:
        print(f"ID: {r.get('id')} | Folio: {r.get('folio')} | Serie: {r.get('serie')} | Fecha: {r.get('fecha_emision')} | Emisor: {r.get('emisor_nombre')} | Total: ${r.get('total')}")
        file_keys = [k for k in r.keys() if any(t in k.lower() for t in ['pdf', 'xml', 'file', 'path', 'ruta', 'archivo', 'url', 'evidencia'])]
        for fk in file_keys:
            val = r[fk]
            val_str = str(val)[:60] if val is not None else 'None'
            print(f"    {fk}: {val_str}")

    conn.close()

if __name__ == '__main__':
    check_gasolina_facturas()
