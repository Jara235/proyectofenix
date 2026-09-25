import psycopg2
from psycopg2.extras import DictCursor

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

print("=== 1. VERIFICANDO / INSERTANDO OBRAS Y EQUIPOS EN CATALOGOS ===")
cur.execute("SELECT codigo FROM catalogos.obras WHERE nombre = 'ALFREDO DEL MAZO';")
if not cur.fetchone():
    cur.execute("""
        INSERT INTO catalogos.obras (codigo, nombre, ingeniero_responsable, responsable_default)
        VALUES ('ADM2', 'ALFREDO DEL MAZO', 'CARMELO ALVAREZ', 'CARMELO ALVAREZ');
    """)
    print("[OK] Obra 'ALFREDO DEL MAZO' agregada al catalogo.")

cur.execute("SELECT codigo FROM catalogos.obras WHERE nombre = 'OBRAS PUBLICAS';")
if not cur.fetchone():
    cur.execute("""
        INSERT INTO catalogos.obras (codigo, nombre, ingeniero_responsable, responsable_default)
        VALUES ('OBP', 'OBRAS PUBLICAS', 'TOMAS ARANDA', 'TOMAS ARANDA');
    """)
    print("[OK] Obra 'OBRAS PUBLICAS' agregada al catalogo.")

cur.execute("SELECT numero_economico FROM catalogos.equipos WHERE numero_economico = 'LOWBOYS';")
if not cur.fetchone():
    cur.execute("""
        INSERT INTO catalogos.equipos (numero_economico, descripcion, tipo_equipo, operador_default)
        VALUES ('LOWBOYS', 'LOWBOY MOTORS', 'EQUIPO', 'BRYAN CHAVEZ');
    """)
    print("[OK] Equipo 'LOWBOYS' agregado a catalogos.equipos.")

print("\n=== 2. GUARDANDO LAS 10 CARGAS PENDIENTES EN gasolina.consumos ===")

cargas_pendientes = [
    {
        'ticket': '416476', 'fecha': '2026-08-10', 'placa': 'LF05470', 'conductor': 'TOMAS ARANDA',
        'obra': 'OBRAS PUBLICAS', 'vehiculo': 'CAMIONETA', 'litros': 65.531, 'precio': 22.89, 'importe': 1500.00
    },
    {
        'ticket': '416378', 'fecha': '2026-08-10', 'placa': 'LHB188D', 'conductor': 'JOSE ANTONIO',
        'obra': 'MAQUINARIA', 'vehiculo': 'RAM 1200', 'litros': 62.485, 'precio': 22.89, 'importe': 1430.28
    },
    {
        'ticket': '416424', 'fecha': '2026-08-10', 'placa': 'MHL758A', 'conductor': 'CARLOS ALARCON',
        'obra': 'OBRA MÉXICO TOLUCA', 'vehiculo': 'MITSUBISHI L200', 'litros': 59.827, 'precio': 22.89, 'importe': 1369.44
    },
    {
        'ticket': '416427', 'fecha': '2026-08-10', 'placa': 'MHL758A', 'conductor': 'CARLOS ALARCON',
        'obra': 'OBRA MÉXICO TOLUCA', 'vehiculo': 'MITSUBISHI L200', 'litros': 21.844, 'precio': 22.89, 'importe': 500.00
    },
    {
        'ticket': '417466', 'fecha': '2026-08-12', 'placa': 'LHB188D', 'conductor': 'JOSE ANTONIO',
        'obra': 'MAQUINARIA', 'vehiculo': 'RAM 1200', 'litros': 46.733, 'precio': 22.89, 'importe': 1069.72
    },
    {
        'ticket': '418715', 'fecha': '2026-08-14', 'placa': 'NUZ948C', 'conductor': 'BRYAN CHAVEZ',
        'obra': 'TRANSPORTES FLOTILLA', 'vehiculo': 'CAMIONETA', 'litros': 13.106, 'precio': 22.89, 'importe': 300.00
    },
    {
        'ticket': '418714', 'fecha': '2026-08-14', 'placa': 'LOWBOYS', 'conductor': 'BRYAN CHAVEZ',
        'obra': 'TRANSPORTES FLOTILLA', 'vehiculo': 'LOWBOY', 'litros': 21.844, 'precio': 22.89, 'importe': 500.00
    },
    {
        'ticket': '418496', 'fecha': '2026-08-14', 'placa': '33K849', 'conductor': 'CARLOS TRUJANO',
        'obra': 'MINA TABERNILLAS', 'vehiculo': 'TOYOTA TACOMA', 'litros': 53.783, 'precio': 27.89, 'importe': 1500.00
    },
    {
        'ticket': '418743', 'fecha': '2026-08-14', 'placa': 'LH49746', 'conductor': 'CARMELO ALVAREZ',
        'obra': 'ALFREDO DEL MAZO', 'vehiculo': 'CAMIONETA', 'litros': 21.844, 'precio': 22.89, 'importe': 500.00
    },
    {
        'ticket': '418885', 'fecha': '2026-08-15', 'placa': 'NYZ829C', 'conductor': 'DIEGO CARREOLA',
        'obra': 'MINA ZUMPAHUACAN', 'vehiculo': 'MITSUBISHI L200', 'litros': 21.844, 'precio': 22.89, 'importe': 500.00
    }
]

# Limpiar por si ya existían con folio pendiente
cur.execute("DELETE FROM gasolina.consumos WHERE folio_conciliacion LIKE 'GAS-S33-LEV-PEND-%';")

for c in cargas_pendientes:
    folio = f"GAS-S33-LEV-PEND-{c['ticket']}"
    obs = f"Ticket {c['ticket']} LEVET Semana 33 - Pendiente de confirmacion fisica de ticket / aclaracion"
    cur.execute("""
        INSERT INTO gasolina.consumos (
            folio_conciliacion, fecha, semana, origen, obra_destino, vehiculo, placa,
            kilometraje, litros, costo_por_litro, importe_total, conductor,
            observaciones, estatus_revision, gasolineria
        ) VALUES (
            %s, %s, '33', 'LEVET_PENDIENTE_TICKET', %s, %s, %s,
            0, %s, %s, %s, %s,
            %s, 'PENDIENTE', 'LEVET'
        ) RETURNING id;
    """, (folio, c['fecha'], c['obra'], c['vehiculo'], c['placa'], c['litros'], c['precio'], c['importe'], c['conductor'], obs))
    new_id = cur.fetchone()[0]
    print(f"[OK] Carga Ticket {c['ticket']} (${c['importe']:,.2f}) guardada con ID #{new_id} [ESTATUS: PENDIENTE]")

conn.commit()
print("\n[OK] LAS 10 CARGAS PENDIENTES QUEDARON REGISTRADAS Y SEGURAS EN POSTGRESQL!")
conn.close()
