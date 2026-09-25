import psycopg2
from psycopg2.extras import DictCursor
import os

def check_gasolina_pdfs():
    conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
    cur = conn.cursor(cursor_factory=DictCursor)

    # 1. Get column names of gasolina.consumos
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema = 'gasolina' AND table_name = 'consumos'
        ORDER BY ordinal_position
    """)
    cols = cur.fetchall()
    print("=== COLUMNS IN gasolina.consumos ===")
    for c in cols:
        print(f" - {c['column_name']} ({c['data_type']})")

    # 2. Query sample rows with invoice/folio numbers like A10268, A10272, A10321, etc.
    cur.execute("""
        SELECT id, folio_conciliacion, ticket_factura, fecha, vehiculo, placa, conductor, importe_total,
               archivo_pdf, ruta_pdf, pdf_path, ticket_path, archivo_ticket, url_pdf, observaciones
        FROM (
            SELECT *, 
                   COALESCE(
                       (SELECT column_name FROM information_schema.columns WHERE table_schema='gasolina' AND table_name='consumos' AND column_name='archivo_pdf'), NULL
                   ) as dummy
            FROM gasolina.consumos
        ) sub
        LIMIT 1
    """)
    
    # Query all columns for rows matching ticket/folio A10268, A10272, A10321, A10278, A10274
    folios = ['A10268', 'A10272', 'A10274', 'A10278', 'A10321', 'A10322', 'A10329', 'A10267', 'A10273']
    
    print("\n=== SEARCHING FOR FOLIOS/TICKETS IN gasolina.consumos ===")
    cur.execute("""
        SELECT *
        FROM gasolina.consumos
        WHERE ticket_factura IN %s OR folio_conciliacion IN %s OR id::text IN %s
    """, (tuple(folios), tuple(folios), tuple(folios)))
    
    rows = [dict(r) for r in cur.fetchall()]
    print(f"Found {len(rows)} rows matching specified folios/tickets")
    for r in rows:
        print("\n----------------------------------------")
        print(f"ID: {r.get('id')} | Folio: {r.get('folio_conciliacion')} | Ticket/Factura: {r.get('ticket_factura')}")
        print(f"Fecha: {r.get('fecha')} | Importe: ${r.get('importe_total')}")
        # Print all keys that sound like pdf/file/path
        file_keys = [k for k in r.keys() if any(term in k.lower() for term in ['pdf', 'file', 'path', 'ruta', 'archivo', 'ticket', 'url', 'evidencia'])]
        for fk in file_keys:
            print(f"  {fk}: {r[fk]}")

    conn.close()

if __name__ == '__main__':
    check_gasolina_pdfs()
