import psycopg2
import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor()

OBRAS_MAP = [
    (['PLANTA DE ASFALTO', 'PLANTA ASFALTO', 'HUIXQUILUCAN', 'TANQUE PEGASO', 'PLANTA PEGASO', 'PEGASO'], 'Planta Pegaso'),
    (['MAQUINARIA PEGASO'],                                              'Maquinaria Pegaso'),
    (['DESASOLVE', 'DEZAZOLVE', 'VICENTE LOMBARDO', 'LOMBARDO'],        'Vicente Lombardo'),
    (['ALFREDO DEL MAZO', 'ALFREDO MAZO'],                              'Alfredo del Mazo'),
    (['BACHEO TOLUCA', 'BACHEO'],                                       'Bacheo Toluca'),
    (['MEXICO TOLUCA', 'MEX-TOL', 'MEXICO-TOLUCA', 'MÉXICO-TOLUCA',
      'MEXICO - TOLUCA', 'MÉXICO- TOLUCA', 'PROVIDENCIA', 'PETROLIZADORA'], 'Mexico-Toluca'),
    (['LERMA TENANGO', 'LERMA-TENANGO', 'LERMA - TENANGO', 'LERMA',
      'OBRA: LERMA'],                                                   'Lerma - Tenango'),
    (['FLOTILLA', 'TRANSPORTES FLOTILLA', 'OBRA: TRANSPORTES'],        'Transportes Flotilla'),
]

def mapear(texto):
    if not texto: return 'Sin clasificar'
    t = texto.upper()
    for kws, obra in OBRAS_MAP:
        for kw in kws:
            if kw in t:
                return obra
    return 'Sin clasificar'

# ── CONSUMOS Semana 28 por Obra ──────────────────────────
cur.execute("""
    SELECT obra_destino, COUNT(*) movimientos, SUM(litros) litros_consumidos
    FROM diesel.consumos
    WHERE semana = 'Semana 28'
    GROUP BY obra_destino
    ORDER BY SUM(litros) DESC
""")
consumos_raw = cur.fetchall()

# Agrupar por obra normalizada
consumos = {}
for obra_raw, mov, lts in consumos_raw:
    obra = mapear(str(obra_raw or ''))
    if obra not in consumos:
        consumos[obra] = {'movimientos': 0, 'litros': 0}
    consumos[obra]['movimientos'] += int(mov)
    consumos[obra]['litros']      += float(lts or 0)

# ── FACTURAS Semana 28 por Obra ──────────────────────────
cur.execute("""
    SELECT punto_de_carga, COUNT(*) facturas, SUM(litros_facturados) litros_facturados
    FROM diesel.facturas
    WHERE semana = 'Semana 28'
    GROUP BY punto_de_carga
    ORDER BY SUM(litros_facturados) DESC
""")
facturas_raw = cur.fetchall()

facturas = {}
for punto, fac, lts in facturas_raw:
    obra = mapear(str(punto or ''))
    if obra not in facturas:
        facturas[obra] = {'facturas': 0, 'litros': 0}
    facturas[obra]['facturas'] += int(fac)
    facturas[obra]['litros']   += float(lts or 0)

# ── TABLA COMPARATIVA ────────────────────────────────────
todas_obras = sorted(set(list(consumos.keys()) + list(facturas.keys())))

print("=" * 90)
print(f"  CONCILIACION DIESEL - SEMANA 28")
print(f"  (Semana 28 = Lunes 7 Jul - Domingo 12 Jul 2026)")
print("=" * 90)
print(f"  {'OBRA':<30} {'CONSUMO':>8} {'FACTURA':>8}  {'DIFERENCIA':>10}  {'ESTADO':>15}")
print(f"  {'':30} {'(Lts)':>8} {'(Lts)':>8}  {'(Lts)':>10}")
print("-" * 90)

total_cons = 0
total_fact = 0

for obra in todas_obras:
    lts_c = consumos.get(obra, {}).get('litros', 0)
    lts_f = facturas.get(obra, {}).get('litros', 0)
    dif   = lts_f - lts_c
    mov   = consumos.get(obra, {}).get('movimientos', 0)
    fac   = facturas.get(obra, {}).get('facturas', 0)

    if lts_f == 0:
        estado = 'SIN FACTURA'
    elif lts_c == 0:
        estado = 'SIN CONSUMO'
    elif abs(dif) < 50:
        estado = 'OK'
    elif dif > 0:
        estado = 'FAC > CONS'
    else:
        estado = 'CONS > FAC'

    print(f"  {obra:<30} {lts_c:>8.1f} {lts_f:>8.1f}  {dif:>+10.1f}  {estado:>15}")
    total_cons += lts_c
    total_fact += lts_f

print("=" * 90)
dif_total = total_fact - total_cons
print(f"  {'TOTAL':<30} {total_cons:>8.1f} {total_fact:>8.1f}  {dif_total:>+10.1f}")
print("=" * 90)

print(f"\n  Movimientos de consumo en Semana 28: {sum(d['movimientos'] for d in consumos.values())}")
print(f"  Facturas en Semana 28:               {sum(d['facturas'] for d in facturas.values())}")
print(f"\n  Nota: Diferencia positiva = se facturó MÁS de lo que se registró como consumo")
print(f"        Diferencia negativa = se consumió MÁS de lo que llegó facturado")

cur.close()
conn.close()
