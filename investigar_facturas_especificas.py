import psycopg2
from psycopg2.extras import DictCursor
import os

def check_specific_facturas():
    conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
    cur = conn.cursor(cursor_factory=DictCursor)

    folios = ['A10268', 'A10272', 'A10274', 'A10278', 'A10321', 'A10322', 'A10329', 'A10267', 'A10273']

    cur.execute("""
        SELECT id, folio_conciliacion, folio_factura, fecha_factura, semana, proveedor, 
               importe_total, uuid_cfdi,
               CASE WHEN archivo_pdf IS NOT NULL THEN LENGTH(archivo_pdf) ELSE 0 END as len_pdf,
               CASE WHEN archivo_xml IS NOT NULL THEN LENGTH(archivo_xml) ELSE 0 END as len_xml
        FROM gasolina.facturas
        WHERE folio_factura IN %s OR folio_conciliacion IN %s
        ORDER BY folio_factura
    """, (tuple(folios), tuple(folios)))

    rows = cur.fetchall()
    print(f"=== MATCHING ROWS IN gasolina.facturas FOR FOLIOS ({len(rows)}) ===")
    for r in rows:
        print(f"ID: {r['id']} | FolioFactura: {r['folio_factura']} | Proveedor: {r['proveedor']} | Fecha: {r['fecha_factura']} | Total: ${r['importe_total']}")
        print(f"   len_pdf: {r['len_pdf']} bytes | len_xml: {r['len_xml']} bytes | uuid: {r['uuid_cfdi']}")

    # Check overall stats in gasolina.facturas
    cur.execute("""
        SELECT COUNT(*) as total,
               COUNT(archivo_pdf) as count_pdf,
               COUNT(archivo_xml) as count_xml
        FROM gasolina.facturas
    """)
    stats = cur.fetchone()
    print(f"\n=== OVERALL STATS IN gasolina.facturas ===")
    print(f"Total Facturas: {stats['total']}")
    print(f"Facturas WITH PDF in DB (bytea): {stats['count_pdf']}")
    print(f"Facturas WITH XML in DB (bytea): {stats['count_xml']}")
    print(f"Facturas WITHOUT PDF in DB: {stats['total'] - stats['count_pdf']}")

    conn.close()

if __name__ == '__main__':
    check_specific_facturas()
