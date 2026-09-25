import datetime, re, psycopg2
from psycopg2.extras import DictCursor

# Tabla 1 (Imagen 1 y 2 - Total $747,843.77)
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

# Tabla 2 (Imagen 3 - Total $915,000.00)
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
    meses = {
        'julio': 7, 'agosto': 8, 'junio': 6, 'mayo': 5
    }
    m = re.search(r'(\d+)\s+de\s+(\w+)\s+de\s+(\d+)', date_str.lower())
    if m:
        day = int(m.group(1))
        mes_nombre = m.group(2)
        year = int(m.group(3))
        month = meses.get(mes_nombre, 7)
        return datetime.date(year, month, day)
    return None

def get_week(dt):
    # En 2026:
    # 06 Jul a 12 Jul = Sem 28
    # 13 Jul a 19 Jul = Sem 29
    # 20 Jul a 26 Jul = Sem 30
    # 27 Jul a 02 Ago = Sem 31
    # 03 Ago a 09 Ago = Sem 32
    if dt < datetime.date(2026, 7, 6):
        return 27
    elif dt <= datetime.date(2026, 7, 12):
        return 28
    elif dt <= datetime.date(2026, 7, 19):
        return 29
    elif dt <= datetime.date(2026, 7, 26):
        return 30
    elif dt <= datetime.date(2026, 8, 2):
        return 31
    else:
        return 32

print(f"Total filas Tabla 1: {len(tabla_1_raw)} | Suma: ${sum(r[1] for r in tabla_1_raw):,.2f}")
print(f"Total filas Tabla 2: {len(tabla_2_raw)} | Suma: ${sum(r[1] for r in tabla_2_raw):,.2f}")
total_general = sum(r[1] for r in tabla_1_raw) + sum(r[1] for r in tabla_2_raw)
print(f"SUMA TOTAL DE AMBAS TABLAS: ${total_general:,.2f} MXN\n")

# Procesar todas las facturas
todas_facturas = []
for f in tabla_1_raw:
    dt = parse_date(f[0])
    sem = get_week(dt)
    todas_facturas.append({
        'tabla': 'Tabla 1 ($747k)', 'fecha_str': f[0], 'fecha': dt, 'semana': sem,
        'importe': f[1], 'centro': f[2], 'folio': f[3]
    })

for f in tabla_2_raw:
    dt = parse_date(f[0])
    sem = get_week(dt)
    todas_facturas.append({
        'tabla': 'Tabla 2 ($915k)', 'fecha_str': f[0], 'fecha': dt, 'semana': sem,
        'importe': f[1], 'centro': f[2], 'folio': f[3]
    })

# Agrupar por semana
semanas_resumen = {}
for item in todas_facturas:
    s = item['semana']
    if s not in semanas_resumen:
        semanas_resumen[s] = {'cant': 0, 'importe': 0.0, 'centros': {}, 'facturas': []}
    semanas_resumen[s]['cant'] += 1
    semanas_resumen[s]['importe'] += item['importe']
    semanas_resumen[s]['facturas'].append(item)
    c = item['centro']
    semanas_resumen[s]['centros'][c] = semanas_resumen[s]['centros'].get(c, 0.0) + item['importe']

print("=" * 80)
print("RESUMEN DE FACTURAS PAGADAS A MOBIL AGRUPADAS POR SEMANA")
print("=" * 80)
for s in sorted(semanas_resumen.keys()):
    info = semanas_resumen[s]
    print(f">> SEMANA {s}: {info['cant']} facturas | Importe Total: ${info['importe']:>12,.2f} MXN")
    for c, imp in sorted(info['centros'].items(), key=lambda x: x[1], reverse=True):
        print(f"     * {c:<30}: ${imp:>10,.2f}")
    print("-" * 80)
