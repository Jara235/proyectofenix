import psycopg2
from psycopg2.extras import DictCursor

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

print("=== 1. ACTUALIZANDO CARGA PCU8771 (ID #446) A $2,000.00 ===")
cur.execute("""
    UPDATE gasolina.consumos
    SET litros = 87.374,
        costo_por_litro = 22.89,
        importe_total = 2000.00,
        observaciones = 'Tickets Levet 417001 ($1,633.04) + 417002 ($366.96) combinados (Total $2,000.00)'
    WHERE id = 446;
""")
print(f"[OK] Carga ID 446 actualizada: {cur.rowcount} fila")

print("\n=== 2. INSERTANDO CARGA MHL758A (Ticket 416424 - $1,369.44) ===")
cur.execute("""
    INSERT INTO gasolina.consumos (
        folio_conciliacion, fecha, semana, origen, obra_destino, vehiculo, placa,
        kilometraje, litros, costo_por_litro, importe_total, conductor,
        observaciones, estatus_revision, gasolineria
    ) VALUES (
        'GAS-S33-LEV-416424', '2026-08-10', '33', 'Gasolineria', 'OBRA MÉXICO TOLUCA', 'MITSUBISHI L200', 'MHL758A',
        0, 59.827, 22.89, 1369.44, 'CARLOS ALARCON',
        'Ticket 416424 Levet (Carlos Alarcon MHL758A)', 'APROBADO', 'LEVET'
    ) RETURNING id;
""")
id_alarcon = cur.fetchone()[0]
print(f"[OK] Carga Carlos Alarcon (Ticket 416424) insertada con ID: {id_alarcon}")

conn.commit()
print("\n[OK] ¡TRANSACCIÓN GUARDADA CON ÉXITO EN POSTGRESQL!")
conn.close()
