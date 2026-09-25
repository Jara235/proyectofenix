import psycopg2
from psycopg2.extras import DictCursor

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

print("=== ACTUALIZANDO CARGA TICKET 416427 ($500.00) A EQUIPO MENOR MEXICO TOLUCA ===")
cur.execute("""
    UPDATE gasolina.consumos
    SET vehiculo = 'EQUIPO MENOR',
        placa = 'EQUIPO MENOR',
        conductor = 'JAVIER PEREZ DÍAZ',
        obra_destino = 'OBRA MÉXICO TOLUCA',
        estatus_revision = 'APROBADO',
        observaciones = 'Ticket 416427 LEVET (10/08/2026) - Equipo Menor Obra México Toluca',
        folio_conciliacion = 'GAS-S33-LEV-416427'
    WHERE id = 476 OR folio_conciliacion = 'GAS-S33-LEV-PEND-416427';
""")
print(f"[OK] Carga actualizada: {cur.rowcount} fila")

conn.commit()
conn.close()
