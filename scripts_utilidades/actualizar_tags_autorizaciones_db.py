import psycopg2, re
from psycopg2.extras import DictCursor
import pdfplumber

def parse_num(val):
    if not val: return 0.0
    clean = re.sub(r'[^\d.]', '', str(val))
    try:
        return float(clean)
    except:
        return 0.0

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

# 1. Resetear y poblar tags.autorizaciones
cur.execute("TRUNCATE TABLE tags.autorizaciones RESTART IDENTITY;")

# JDJ
jdj_aut = [
    {'tag': 'IMDM30874327', 'no_economico': 'LEONCIO', 'responsable': 'LEONCIO MARTINEZ (BONAICE)', 'placas': 'NYZ790C', 'tipo': 'CAMIONETA', 'aut': 2000.0, 'obra': 'Lerma - Tres Marías'},
    {'tag': 'IMDM30874326', 'no_economico': 'BRYAN MORENO', 'responsable': 'BRYAN MORENO', 'placas': 'NH4348B', 'tipo': 'PETROLIZADORA 2', 'aut': 2000.0, 'obra': 'Maquinaria'},
    {'tag': 'IMDM30874324', 'no_economico': 'PAOLA JARAMILLO', 'responsable': 'PAOLA JARAMILLO', 'placas': 'LLY085A', 'tipo': 'CHANGAN', 'aut': 500.0, 'obra': 'Corporativo'},
    {'tag': 'IMDM30874320', 'no_economico': 'APOLINAR R.', 'responsable': 'APOLINAR REYES', 'placas': 'NYZ971C', 'tipo': 'MITSUBISHI L200', 'aut': 1500.0, 'obra': 'Lerma - Tres Marías'},
    {'tag': 'IMDM28600393', 'no_economico': 'CAM 31/2CARMELO', 'responsable': 'CARMELO ALVAREZ', 'placas': 'LH49746', 'tipo': 'CAM. 3 1/2', 'aut': 2500.0, 'obra': 'Obras Metepec'},
    {'tag': 'IMDM28600391', 'no_economico': 'Alberto Maq', 'responsable': 'Alberto Maq', 'placas': 'PCW9391', 'tipo': 'DODGE RAM 700', 'aut': 500.0, 'obra': 'Maquinaria'},
    {'tag': 'IMDM28600385', 'no_economico': 'YOVANI VICENTE', 'responsable': 'YOVANI VICENTE', 'placas': 'LD61309', 'tipo': 'CAMIONETA RAM 400', 'aut': 4000.0, 'obra': 'Transportes Flotilla'},
    {'tag': 'IMDM28600382', 'no_economico': 'JOSE TRUJANO', 'responsable': 'JOSE TRUJANO', 'placas': '', 'tipo': 'VEHÍCULO', 'aut': 2500.0, 'obra': 'Grupo Trujano'},
    {'tag': 'IMDM28600378', 'no_economico': 'CLEMENTE', 'responsable': 'CLEMENTE', 'placas': 'LHB184D', 'tipo': 'RAM 1200', 'aut': 1000.0, 'obra': 'Transportes Flotilla'},
    {'tag': 'IMDM28600368', 'no_economico': 'CARLOS NAZAR', 'responsable': 'CARLOS NAZAR', 'placas': 'PCW9238', 'tipo': 'VEHÍCULO', 'aut': 500.0, 'obra': 'Maquinaria'},
    {'tag': 'IMDM28600364', 'no_economico': 'DIEGO FERNANDEZ', 'responsable': 'DIEGO FERNANDEZ', 'placas': 'PBT-12-29', 'tipo': 'TOYOTA HIACE', 'aut': 1500.0, 'obra': 'Lerma - Tres Marías'},
    {'tag': 'IMDM28600363', 'no_economico': 'FRANCISCO GOMORA', 'responsable': 'FRANCISCO GOMORA', 'placas': '', 'tipo': 'PETROLIZADORA', 'aut': 2000.0, 'obra': 'Lerma - Tres Marías'},
    {'tag': 'IMDM28600360', 'no_economico': 'ING VICTOR', 'responsable': 'ING VICTOR', 'placas': 'LHB182D', 'tipo': 'CAM', 'aut': 1000.0, 'obra': 'Guadalajara'},
    {'tag': 'IMDM28600359', 'no_economico': 'UNIDAD PILOTO', 'responsable': 'UNIDAD PILOTO', 'placas': '', 'tipo': 'VEHÍCULO', 'aut': 1000.0, 'obra': 'Obras'},
    {'tag': 'IMDM28600355', 'no_economico': 'ROBERTO CARLOS', 'responsable': 'ROBERTO CARLOS', 'placas': '', 'tipo': 'VEHÍCULO', 'aut': 0.0, 'obra': 'Inactivo'},
    {'tag': 'CPFI 01427350', 'no_economico': 'JAVIER PEREZ', 'responsable': 'JAVIER PEREZ', 'placas': 'MHL758A', 'tipo': 'MITSUBISHI 1200', 'aut': 500.0, 'obra': 'México - Toluca'},
    {'tag': 'IMDM30874323', 'no_economico': 'URBAN PERSONAL', 'responsable': 'CARLOS ALARCON (URBAN PERSONAL)', 'placas': 'pbt-12-30', 'tipo': 'URBAN', 'aut': 500.0, 'obra': 'México - Toluca'},
    {'tag': 'IMDM30874322', 'no_economico': 'PIPA ROJA', 'responsable': 'ARMANDO CASIMIRO', 'placas': 'LE76787', 'tipo': 'PIPA ROJA', 'aut': 2000.0, 'obra': 'Transportes Flotilla'},
    {'tag': 'IMDM30874329', 'no_economico': 'UT COMPRAS', 'responsable': 'BRAYAN GABRIEL CHAVEZ', 'placas': 'NYK3710', 'tipo': 'UT COMPRAS / TORNADO', 'aut': 1000.0, 'obra': 'Transportes Flotilla'},
    {'tag': 'IMDM31180016', 'no_economico': 'PIPA ROJA MACK', 'responsable': 'ARMANDO CASIMIRO (PIPA MACK)', 'placas': 'PIPA MACK', 'tipo': 'PIPA DE AGUA', 'aut': 4000.0, 'obra': 'Transportes Flotilla'}
]

for j in jdj_aut:
    cur.execute("""
        INSERT INTO tags.autorizaciones (empresa, tag, no_economico, responsable, placas, tipo_unidad, monto_autorizado, estatus)
        VALUES ('JDJ', %s, %s, %s, %s, %s, %s, 'ACTIVO');
    """, (j['tag'], j['no_economico'], j['responsable'], j['placas'], j['tipo'], j['aut']))

# TRD
trd_aut = [
    {'tag': 'IMDM30874319', 'no_economico': 'PIPA AGUA', 'responsable': 'PIPA AGUA', 'placas': 'NE4262B', 'tipo': 'PIPA AGUA', 'aut': 1000.0, 'estatus': 'ACTIVO'},
    {'tag': 'IMDM30874318', 'no_economico': 'IMPACTO', 'responsable': 'IMPACTO', 'placas': 'NE4268B', 'tipo': 'IMPACTO', 'aut': 1000.0, 'estatus': 'ACTIVO'},
    {'tag': 'IMDM30874317', 'no_economico': 'ANTONIO IBAÑEZ', 'responsable': 'ANTONIO IBAÑEZ', 'placas': 'HTZ CN4433', 'tipo': 'UTILITARIO', 'aut': 500.0, 'estatus': 'ACTIVO'},
    {'tag': 'IMDM30874316', 'no_economico': 'EDGAR VELAZQUEZ', 'responsable': 'EDGAR VELAZQUEZ', 'placas': 'PCW 9391', 'tipo': 'UTILITARIO', 'aut': 500.0, 'estatus': 'ACTIVO'},
    {'tag': 'IMDM30874315', 'no_economico': 'CRISTOBAL SILVA', 'responsable': 'CRISTOBAL SILVA', 'placas': 'MHL758A', 'tipo': 'UTILITARIO', 'aut': 0.0, 'estatus': 'ACTIVO'},
    {'tag': 'IMDM30874314', 'no_economico': 'JOSE TRUJANO', 'responsable': 'JOSE TRUJANO (JEEP)', 'placas': 'JEEP', 'tipo': 'UTILITARIO', 'aut': 2500.0, 'estatus': 'ACTIVO'},
    {'tag': 'IMDM30874310', 'no_economico': 'JOSUE ORTEGA', 'responsable': 'JOSUE ORTEGA', 'placas': 'LD61303', 'tipo': 'UTILITARIO', 'aut': 1500.0, 'estatus': 'ACTIVO'},
    {'tag': 'IMDM28600335', 'no_economico': 'UBER BELLO', 'responsable': 'UBER BELLO', 'placas': '', 'tipo': 'UTILITARIO', 'aut': 0.0, 'estatus': 'INACTIVO'},
    {'tag': 'IMDM28600334', 'no_economico': 'JESUS MARIN', 'responsable': 'JESUS MARIN', 'placas': 'PCU8771', 'tipo': 'UTILITARIO / CHEVROLET S10', 'aut': 700.0, 'estatus': 'ACTIVO'},
    {'tag': 'IMDM28600333', 'no_economico': 'CARLOS REYES', 'responsable': 'CARLOS REYES', 'placas': '33K848', 'tipo': 'UTILITARIO / TACOMA', 'aut': 1000.0, 'estatus': 'ACTIVO'},
    {'tag': 'IMDM28600332', 'no_economico': 'FLOR ARANDA', 'responsable': 'FLOR ARANDA', 'placas': 'LND180D', 'tipo': 'UTILITARIO / MITSUBISHI L200', 'aut': 500.0, 'estatus': 'ACTIVO'},
    {'tag': 'IMDM28600331', 'no_economico': 'LAZARO PINAL', 'responsable': 'LAZARO PINAL', 'placas': 'MHL757A', 'tipo': 'UTILITARIO / MITSUBISHI L200', 'aut': 0.0, 'estatus': 'INACTIVO'},
    {'tag': 'IMDM28600329', 'no_economico': 'DIEGO FER', 'responsable': 'DIEGO FER', 'placas': 'PBT1229', 'tipo': 'VEHÍCULO', 'aut': 0.0, 'estatus': 'INACTIVO'},
    {'tag': 'IMDM28600328', 'no_economico': 'ELTOHN GAMORA', 'responsable': 'ELTOHN GAMORA', 'placas': '', 'tipo': 'VEHÍCULO', 'aut': 0.0, 'estatus': 'INACTIVO'},
    {'tag': 'IMDM28600327', 'no_economico': 'JORGE TRUJANO', 'responsable': 'JORGE TRUJANO', 'placas': '', 'tipo': 'VEHÍCULO', 'aut': 2000.0, 'estatus': 'ACTIVO'},
    {'tag': 'IMDM28600326', 'no_economico': 'LIC KENDY', 'responsable': 'LIC KENDY', 'placas': '', 'tipo': 'VEHÍCULO', 'aut': 0.0, 'estatus': 'INACTIVO'},
    {'tag': 'IMDM28600325', 'no_economico': 'PIPA DE AGUA', 'responsable': 'PIPA DE AGUA (NPW1169)', 'placas': 'NPW1169', 'tipo': 'PIPA DE AGUA', 'aut': 0.0, 'estatus': 'ACTIVO'},
    {'tag': 'IMDM28600323', 'no_economico': 'ING. PEPE', 'responsable': 'ING. PEPE', 'placas': 'XXXXXXX', 'tipo': 'TRUJANO 2026', 'aut': 2000.0, 'estatus': 'ACTIVO'},
    {'tag': 'IMDM28600320', 'no_economico': 'HUGO PUINI', 'responsable': 'HUGO PUINI', 'placas': '', 'tipo': 'VEHÍCULO', 'aut': 0.0, 'estatus': 'INACTIVO'},
    {'tag': 'IMDM28600319', 'no_economico': 'ARMANDO C.L.', 'responsable': 'ARMANDO C.L.', 'placas': '', 'tipo': 'VEHÍCULO', 'aut': 0.0, 'estatus': 'INACTIVO'},
    {'tag': 'IMDM28600318', 'no_economico': 'PABLO FLORES', 'responsable': 'PABLO FLORES', 'placas': 'MHL-759-A', 'tipo': 'VEHÍCULO', 'aut': 0.0, 'estatus': 'INACTIVO'},
    {'tag': 'IMDM28600317', 'no_economico': 'OFICINA C', 'responsable': 'OFICINA C', 'placas': '', 'tipo': 'VEHÍCULO', 'aut': 0.0, 'estatus': 'INACTIVO'},
    {'tag': 'IMDM28600316', 'no_economico': 'FAMSA AMARILLO', 'responsable': 'FAMSA AMARILLO', 'placas': '', 'tipo': 'VEHÍCULO', 'aut': 0.0, 'estatus': 'ACTIVO'},
    {'tag': 'IMDM28600315', 'no_economico': 'JOSE TRUJANO', 'responsable': 'JOSE TRUJANO', 'placas': '', 'tipo': 'VEHÍCULO', 'aut': 2000.0, 'estatus': 'ACTIVO'},
    {'tag': 'IMDM28600314', 'no_economico': 'RAYMUNDO G.', 'responsable': 'RAYMUNDO G.', 'placas': '', 'tipo': 'VEHÍCULO', 'aut': 500.0, 'estatus': 'ACTIVO'},
    {'tag': 'IMDM28600312', 'no_economico': 'CRISTIAN GOMORA', 'responsable': 'CRISTIAN GOMORA', 'placas': 'LD61303', 'tipo': 'VEHÍCULO', 'aut': 1500.0, 'estatus': 'ACTIVO'}
]

for t in trd_aut:
    cur.execute("""
        INSERT INTO tags.autorizaciones (empresa, tag, no_economico, responsable, placas, tipo_unidad, monto_autorizado, estatus)
        VALUES ('TRD', %s, %s, %s, %s, %s, %s, %s);
    """, (t['tag'], t['no_economico'], t['responsable'], t['placas'], t['tipo'], t['aut'], t['estatus']))

# 2. Actualizar movimientos de Bryan Gabriel Chavez en tags.movimientos para que tengan el nombre correcto
cur.execute("""
    UPDATE tags.movimientos
    SET responsable = 'BRAYAN GABRIEL CHAVEZ', no_economico = 'UT COMPRAS'
    WHERE tag ILIKE '%30874329%' AND (responsable ILIKE '%COMPRAS%' OR responsable IS NULL OR responsable = '');
""")

conn.commit()
print(f"tags.autorizaciones actualizado con éxito. Total registros: {len(jdj_aut) + len(trd_aut)}")
conn.close()
