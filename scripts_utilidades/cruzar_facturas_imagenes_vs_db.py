import datetime, re, psycopg2
from psycopg2.extras import DictCursor

tabla_1_raw = [
    ("20 de julio de 2026", 1857.15, "BACHEO TOLUCA", "A-10484"),
    ("20 de julio de 2026", 12150.08, "P. DE ASFALTO HUIXQUILUCAN", "A-10485"),
    ("20 de julio de 2026", 21600.09, "P. DE ASFALTO HUIXQUILUCAN", "A-10491"),
    ("20 de julio de 2026", 10800.97, "ALFREDO DEL MAZO", "A-10492"),
    ("14 de julio de 2026", 27000.11, "COLEGIO MILITAR", "A-10496"),
    ("21 de julio de 2026", 10800.13, "P. DE ASFALTO HUIXQUILUCAN", "A-10520"),
    ("21 de julio de 2026", 21600.15, "DEZAZOLVE CANALES", "A-10521"),
    ("21 de julio de 2026", 25925.00, "MEXICO TOLUCA", "A-10522"),
    ("21 de julio de 2026", 5400.05, "ALFREDO DEL MAZO", "A-10532"),
    ("22 de julio de 2026", 21600.15, "P. DE ASFALTO HUIXQUILUCAN", "A-10535"),
    ("22 de julio de 2026", 21600.15, "DEZAZOLVE CANALES", "A-10543"),
    ("23 de julio de 2026", 8100.00, "ALFREDO DEL MAZO", "A-10544"),
    ("23 de julio de 2026", 10800.10, "P. DE ASFALTO HUIXQUILUCAN", "A-10556"),
    ("23 de julio de 2026", 25650.13, "MEXICO TOLUCA", "A-10563"),
    ("23 de julio de 2026", 4860.05, "DEZAZOLVE CANALES", "A-10564"),
    ("23 de julio de 2026", 7290.05, "CONSTITUCION", "A-10565"),
    ("23 de julio de 2026", 14850.08, "ALFREDO DEL MAZO", "A-10572"),
    ("23 de julio de 2026", 24840.10, "ALFREDO DEL MAZO", "A-10577"),
    ("24 de julio de 2026", 10800.10, "P. DE ASFALTO HUIXQUILUCAN", "A-10579"),
    ("27 de julio de 2026", 10800.10, "P. DE ASFALTO HUIXQUILUCAN", "A-10581"),
    ("24 de julio de 2026", 18900.06, "ALFREDO DEL MAZO", "A-10583"),
    ("24 de julio de 2026", 14364.05, "DEZAZOLVE CANALES", "A-10586"),
    ("24 de julio de 2026", 1080.03, "MEXICO TOLUCA", "A-10587"),
    ("24 de julio de 2026", 12960.06, "ALFREDO DEL MAZO", "A-10588"),
    ("25 de julio de 2026", 24840.10, "MEXICO TOLUCA", "A-10589"),
    ("27 de julio de 2026", 9720.03, "LERMA", "A-10603"),
    ("27 de julio de 2026", 3240.00, "PROVIDENCIA", "A-10604"),
    ("28 de julio de 2026", 10800.03, "P. DE ASFALTO HUIXQUILUCAN", "A-10605"),
    ("28 de julio de 2026", 30502.11, "MEXICO TOLUCA", "A-10623"),
    ("28 de julio de 2026", 23490.11, "DEZAZOLVE CANALES", "A-10624"),
    ("28 de julio de 2026", 10800.10, "P. DE ASFALTO HUIXQUILUCAN", "A-10625"),
    ("28 de julio de 2026", 26959.90, "P. DE ASFALTO HUIXQUILUCAN", "A-10630"),
    ("28 de julio de 2026", 1620.03, "P. DE ASFALTO HUIXQUILUCAN", "A-10634"),
    ("29 de julio de 2026", 1558.03, "P. DE ASFALTO HUIXQUILUCAN", "A-10635"),
    ("28 de julio de 2026", 10260.10, "ALFREDO DEL MAZO", "A-10636"),
    ("29 de julio de 2026", 24564.14, "LERMA", "A-10637"),
    ("31 de julio de 2026", 3510.00, "PROVIDENCIA", "A-10644"),
    ("31 de julio de 2026", 17820.03, "ALFREDO DEL MAZO", "A-10645"),
    ("31 de julio de 2026", 25650.09, "DEZAZOLVE CANALES", "A-10646"),
    ("30 de julio de 2026", 21600.46, "P. DE ASFALTO HUIXQUILUCAN", "A-10652"),
    ("27 de julio de 2026", 3105.00, "BACHEO TOLUCA", "A-10653"),
    ("27 de julio de 2026", 24852.31, "DEZAZOLVE CANALES", "A-10654"),
    ("1 de agosto de 2026", 8100.05, "P. DE ASFALTO HUIXQUILUCAN", "A-10669"),
    ("1 de agosto de 2026", 25920.06, "MEXICO TOLUCA", "A-10673"),
    ("1 de agosto de 2026", 8100.05, "P. DE ASFALTO HUIXQUILUCAN", "A-10674"),
    ("29 de julio de 2026", 20520.09, "DEZAZOLVE CANALES", "A-10702"),
    ("29 de julio de 2026", 1620.03, "PROVIDENCIA", "A-10712"),
    ("29 de julio de 2026", 9736.66, "ALFREDO DEL MAZO", "A-10713"),
    ("30 de julio de 2026", 21600.14, "P. DE ASFALTO HUIXQUILUCAN", "A-10722"),
    ("30 de julio de 2026", 24840.10, "MEXICO TOLUCA", "A-10733"),
    ("30 de julio de 2026", 1485.03, "P. DE ASFALTO HUIXQUILUCAN", "A-10748"),
    ("17 de julio de 2026", 5400.05, "P. DE ASFALTO HUIXQUILUCAN", "A-23783100"),
]

tabla_2_raw = [
    ("6 de julio de 2026", 66605.40, "TANQUE PEGASO", "A-10360"),
    ("7 de julio de 2026", 8100.05, "TANQUE PEGASO", "A-10380"),
    ("7 de julio de 2026", 3000.00, "TANQUE PEGASO", "A-10386"),
    ("7 de julio de 2026", 18900.06, "LERMA", "A-10381"),
    ("7 de julio de 2026", 2700.08, "LERMA", "A-10388"),
    ("6 de julio de 2026", 8100.05, "P. DE ASFALTO HUIXQUILUCAN", "A-10361"),
    ("6 de julio de 2026", 10800.10, "P. DE ASFALTO HUIXQUILUCAN", "A-10365"),
    ("6 de julio de 2026", 16200.10, "P. DE ASFALTO HUIXQUILUCAN", "A-10368"),
    ("7 de julio de 2026", 16200.10, "P. DE ASFALTO HUIXQUILUCAN", "A-10884"),
    ("8 de julio de 2026", 10800.10, "P. DE ASFALTO HUIXQUILUCAN", "A-10405"),
    ("8 de julio de 2026", 8100.05, "P. DE ASFALTO HUIXQUILUCAN", "A-10406"),
    ("8 de julio de 2026", 8100.05, "P. DE ASFALTO HUIXQUILUCAN", "A-10408"),
    ("6 de julio de 2026", 6291.00, "PROVIDENCIA", "A-10362"),
    ("6 de julio de 2026", 7695.00, "BACHEO TOLUCA", "A-10366"),
    ("7 de julio de 2026", 21600.15, "BACHEO TOLUCA", "A-10387"),
    ("6 de julio de 2026", 19305.10, "MEXICO TOLUCA", "A-10367"),
    ("8 de julio de 2026", 16200.10, "MEXICO TOLUCA", "A-10398"),
    ("8 de julio de 2026", 23206.21, "DEZAZOLVE CANALES", "A-10409"),
    ("13 de julio de 2026", 601.43, "TANQUE PEGASO", "A-10420"),
    ("15 de julio de 2026", 108000.36, "TANQUE PEGASO", "A-10510"),
    ("13 de julio de 2026", 4197.68, "TANQUE PEGASO", "A-10511"),
    ("10 de julio de 2026", 18043.21, "LERMA", "A-10894"),
    ("13 de julio de 2026", 17804.45, "LERMA", "A-10426"),
    ("13 de julio de 2026", 3000.00, "LERMA", "A-10427"),
    ("9 de julio de 2026", 2700.08, "MAQUINARIA", "A-10886"),
    ("9 de julio de 2026", 16201.80, "P. DE ASFALTO HUIXQUILUCAN", "A-10888"),
    ("10 de julio de 2026", 27000.11, "P. DE ASFALTO HUIXQUILUCAN", "A-10899"),
    ("11 de julio de 2026", 13500.06, "P. DE ASFALTO HUIXQUILUCAN", "A-10904"),
    ("12 de julio de 2026", 8100.05, "P. DE ASFALTO HUIXQUILUCAN", "A-10912"),
    ("14 de julio de 2026", 16200.10, "P. DE ASFALTO HUIXQUILUCAN", "A-10495"),
    ("15 de julio de 2026", 8100.05, "P. DE ASFALTO HUIXQUILUCAN", "A-10438"),
    ("15 de julio de 2026", 27000.11, "P. DE ASFALTO HUIXQUILUCAN", "A-10514"),
    ("13 de julio de 2026", 14445.05, "VICENTE LOMBARDO", "A-10422"),
    ("14 de julio de 2026", 11880.00, "VICENTE LOMBARDO", "A-10499"),
    ("9 de julio de 2026", 10800.10, "PROVIDENCIA", "A-10887"),
    ("15 de julio de 2026", 5400.05, "PROVIDENCIA", "A-10513"),
    ("10 de julio de 2026", 5400.05, "ALFREDO DEL MAZO", "A-10893"),
    ("13 de julio de 2026", 22652.97, "ALFREDO DEL MAZO", "A-10425"),
    ("15 de julio de 2026", 10800.13, "ALFREDO DEL MAZO", "A-10512"),
    ("15 de julio de 2026", 29693.92, "MEXICO TOLUCA", "A-10509"),
    ("10 de julio de 2026", 24705.06, "DEZAZOLVE CANALES", "A-10900"),
    ("13 de julio de 2026", 14445.05, "DEZAZOLVE CANALES", "A-10423"),
    ("14 de julio de 2026", 11880.00, "DEZAZOLVE CANALES", "A-10500"),
    ("16 de julio de 2026", 16200.10, "ALFREDO DEL MAZO", "A-10446"),
    ("16 de julio de 2026", 10800.10, "PROVIDENCIA", "A-10447"),
    ("16 de julio de 2026", 13500.55, "P. DE ASFALTO HUIXQUILUCAN", "A-10449"),
    ("16 de julio de 2026", 22950.13, "DEZAZOLVE CANALES", "A-10453"),
    ("16 de julio de 2026", 1800.02, "TANQUE PEGASO", "A-10454"),
    ("17 de julio de 2026", 27000.11, "LERMA", "A-10457"),
    ("17 de julio de 2026", 10800.06, "P. DE ASFALTO HUIXQUILUCAN", "A-10458"),
    ("17 de julio de 2026", 32400.12, "MEXICO TOLUCA", "A-10459"),
    ("18 de julio de 2026", 20250.13, "ALFREDO DEL MAZO", "A-10474"),
    ("20 de julio de 2026", 12285.08, "PROVIDENCIA", "A-10479"),
    ("20 de julio de 2026", 14715.08, "LERMA", "A-10480"),
    ("20 de julio de 2026", 16200.10, "DEZAZOLVE CANALES", "A-10483"),
    ("20 de julio de 2026", 11642.85, "BACHEO TOLUCA", "A-10484"),
]

def parse_date(date_str):
    meses = {'julio': 7, 'agosto': 8, 'junio': 6, 'mayo': 5}
    m = re.search(r'(\d+)\s+de\s+(\w+)\s+de\s+(\d+)', date_str.lower())
    if m:
        day = int(m.group(1))
        mes_nombre = m.group(2)
        year = int(m.group(3))
        month = meses.get(mes_nombre, 7)
        return datetime.date(year, month, day)
    return None

def get_week(dt):
    if dt < datetime.date(2026, 7, 6): return 27
    elif dt <= datetime.date(2026, 7, 12): return 28
    elif dt <= datetime.date(2026, 7, 19): return 29
    elif dt <= datetime.date(2026, 7, 26): return 30
    elif dt <= datetime.date(2026, 8, 2): return 31
    else: return 32

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

# Obtener todas las facturas en BD de Castilla
cur.execute("""
    SELECT folio_factura, fecha_factura, semana, obra_destino, importe_total, litros_facturados, estatus_revision
    FROM diesel.facturas
    WHERE proveedor ILIKE '%CASTILLA%';
""")
db_facturas = {r['folio_factura'].replace('A-', '').strip(): dict(r) for r in cur.fetchall()}

print("=== CRUCE DE FACTURAS PAGADAS VS BASE DE DATOS ===")
encontradas = 0
no_encontradas = 0
discrepancia_importe = 0.0

todas = tabla_1_raw + tabla_2_raw
print(f"Total registros analizados: {len(todas)}")

# Agrupar folios unicos (ver si hay folios divididos)
folios_dict = {}
for dt_str, imp, ctro, fol in todas:
    dt = parse_date(dt_str)
    sem = get_week(dt)
    fol_clean = fol.replace('A-', '').strip()
    if fol_clean not in folios_dict:
        folios_dict[fol_clean] = {'folio': fol, 'importe_pago': 0.0, 'fechas': [], 'centros': [], 'semanas': set()}
    folios_dict[fol_clean]['importe_pago'] += imp
    folios_dict[fol_clean]['fechas'].append(str(dt))
    folios_dict[fol_clean]['centros'].append(ctro)
    folios_dict[fol_clean]['semanas'].add(sem)

print(f"Folios únicos de facturas en imágenes: {len(folios_dict)}")

# Comparar con BD
sum_pagada_en_bd = 0.0
sum_pagada_no_en_bd = 0.0
sum_bd_total = sum(f['importe_total'] for f in db_facturas.values())

for fol_num, data in folios_dict.items():
    if fol_num in db_facturas:
        encontradas += 1
        db_f = db_facturas[fol_num]
        imp_bd = float(db_f['importe_total'])
        imp_pago = data['importe_pago']
        diff = imp_pago - imp_bd
        sum_pagada_en_bd += imp_pago
        if abs(diff) > 0.05:
            print(f"[DIFERENCIA] Folio {fol_num}: Pagado=${imp_pago:,.2f} vs BD=${imp_bd:,.2f} (Diff: ${diff:,.2f})")
    else:
        no_encontradas += 1
        sum_pagada_no_en_bd += data['importe_pago']
        print(f"[NO EN BD] Folio {fol_num}: Pagado=${data['importe_pago']:,.2f} | Centro={data['centros']} | Sem={data['semanas']}")

print(f"\nResumen:")
print(f"  * Encontradas en BD: {encontradas} facturas (${sum_pagada_en_bd:,.2f})")
print(f"  * NO encontradas en BD: {no_encontradas} facturas (${sum_pagada_no_en_bd:,.2f})")
