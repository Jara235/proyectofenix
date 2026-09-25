import psycopg2, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor()

OBRAS_MAP = [
    (['PLANTA DE ASFALTO', 'PLANTA ASFALTO', 'HUIXQUILUCAN', 'TANQUE PEGASO',
      'PLANTA PEGASO', 'PEGASO', 'P.A.H', 'OBRA: PLANTA'],                                           'Planta Pegaso'),
    (['MAQUINARIA PEGASO', 'MAQUINARIA PEG'],                                         'Maquinaria Pegaso'),
    (['DESASOLVE', 'DEZAZOLVE', 'VICENTE LOMBARDO', 'LOMBARDO'],                      'Vicente Lombardo'),
    (['ALFREDO DEL MAZO', 'ALFREDO MAZO'],                                            'Alfredo del Mazo'),
    (['BACHEO TOLUCA', 'BACHEO'],                                                     'Bacheo Toluca'),
    (['MEXICO TOLUCA', 'MEX-TOL', 'MEXICO-TOLUCA', 'MEXICO - TOLUCA',
      'MÉXICO-TOLUCA', 'MÉXICO- TOLUCA', 'MÉXICO - TOLUCA',
      'LA PROVIDENCIA', 'PROVIDENCIA', 'PETROLIZADORA'],                              'Mexico-Toluca'),
    (['LERMA TENANGO', 'LERMA-TENANGO', 'LERMA - TENANGO', 'LERMA', 'OBRA: LERMA'],                  'Lerma - Tenango'),
    (['COLEGIO MILITAR', 'COLMIL'],                                                   'Colegio Militar'),
    (['DRAGONES', 'DRAG'],                                                            'Dragones'),
    (['FLOTILLA', 'TRANSPORTES FLOTILLA', 'OBRA: TRANSPORTES', 'TRANSPORTES'],        'Transportes Flotilla'),
]

def mapear(txt):
    if not txt: return 'Sin clasificar'
    t = txt.upper()
    for kws, obra in OBRAS_MAP:
        for kw in kws:
            if kw in t: return obra
    return 'Sin clasificar'

# Consumos
cur.execute("SELECT obra_destino, COUNT(*), SUM(litros) FROM diesel.consumos WHERE semana='Semana 28' GROUP BY obra_destino")
consumos = {}
for o, n, l in cur.fetchall():
    k = mapear(o)
    consumos.setdefault(k, {'m':0,'l':0})
    consumos[k]['m'] += n
    consumos[k]['l'] += float(l or 0)

# Facturas
cur.execute("SELECT punto_de_carga, COUNT(*), SUM(litros_facturados) FROM diesel.facturas WHERE semana='Semana 28' GROUP BY punto_de_carga")
facturas = {}
for p, n, l in cur.fetchall():
    k = mapear(p)
    facturas.setdefault(k, {'f':0,'l':0})
    facturas[k]['f'] += n
    facturas[k]['l'] += float(l or 0)

todas = sorted(set(list(consumos.keys()) + list(facturas.keys())))

print(f"\n{'OBRA':<28} {'CONSUMO':>9} {'FACTURA':>9} {'DIFERENCIA':>11}  ESTADO")
print("=" * 75)
tc, tf = 0, 0
for obra in todas:
    lc = consumos.get(obra, {}).get('l', 0)
    lf = facturas.get(obra, {}).get('l', 0)
    dif = lf - lc
    if   lf == 0:         estado = "SIN FACTURA ⚠️"
    elif lc == 0:         estado = "SIN CONSUMO ⚠️"
    elif abs(dif) < 50:   estado = "✅ OK"
    elif dif > 0:         estado = "🟡 Fac > Cons"
    else:                 estado = "🔴 Cons > Fac"
    print(f"  {obra:<26} {lc:>9.1f} {lf:>9.1f} {dif:>+11.1f}  {estado}")
    tc += lc; tf += lf

print("=" * 75)
print(f"  {'TOTAL':<26} {tc:>9.1f} {tf:>9.1f} {tf-tc:>+11.1f}")

cur.close()
conn.close()
