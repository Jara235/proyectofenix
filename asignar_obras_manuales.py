import psycopg2
import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor()
print("Conectado a PostgreSQL")

# Asignaciones manuales confirmadas por el maestro de gasolina
asignaciones = [
    # (folio_conciliacion, obra_destino)
    ('FA-DPC-28-121', 'Transportes Flotilla'),   # NZT266B - Samuel Ortega - Flotilla
    ('FA-DPC-28-144', 'Planta Pegaso'),           # LKC794D - Cristobal (Tanque Pegaso gasolina)
    ('FA-DPC-28-147', 'Transportes Flotilla'),   # LHB184D - Clemente Sanabria - Flotilla
    ('FA-DPC-28-148', 'Lerma - Tenango'),         # PBT-12-29 - Diego Fernandez - Lerma
    ('FA-DPC-28-149', 'Lerma - Tenango'),         # NYZ-790-C - Leoncio Martinez - Lerma
]

print("\n=== ACTUALIZANDO OBRAS MANUALES ===")
for folio, obra in asignaciones:
    cur.execute("""
        UPDATE diesel.facturas 
        SET punto_de_carga = CONCAT(punto_de_carga, ' [OBRA: ', %s, ']')
        WHERE folio_conciliacion = %s
        RETURNING folio_conciliacion, litros_facturados
    """, (obra, folio))
    r = cur.fetchone()
    if r:
        print(f"  OK  {folio} -> {obra} ({r[1]} Lts)")
    else:
        print(f"  ??  {folio} NO ENCONTRADO")

conn.commit()

# Resumen final de la Semana 28
print("\n=== RESUMEN FINAL SEMANA 28 ===")

OBRAS_MAP = [
    (['PLANTA DE ASFALTO', 'PLANTA ASFALTO', 'HUIXQUILUCAN', 'TANQUE PEGASO',
      'PLANTA PEGASO', 'PEGASO'],                                                 'Planta Pegaso'),
    (['MAQUINARIA PEGASO'],                                                       'Maquinaria Pegaso'),
    (['DESASOLVE', 'DEZAZOLVE', 'VICENTE LOMBARDO', 'LOMBARDO'],                  'Vicente Lombardo'),
    (['ALFREDO DEL MAZO', 'ALFREDO MAZO'],                                        'Alfredo del Mazo'),
    (['BACHEO TOLUCA', 'BACHEO'],                                                 'Bacheo Toluca y Calle Lerdo'),
    (['MEXICO TOLUCA', 'MEX-TOL', 'MEXICO-TOLUCA', 'MÉXICO-TOLUCA',
      'MEXICO - TOLUCA', 'MÉXICO- TOLUCA', 'LA PROVIDENCIA', 'PROVIDENCIA',
      'PETROLIZADORA'],                                                           'Mexico-Toluca'),
    (['LERMA TENANGO', 'LERMA-TENANGO', 'LERMA - TENANGO', 'LERMA'],              'Lerma - Tenango'),
    (['FLOTILLA', 'TRANSPORTES FLOTILLA', 'OBRA: TRANSPORTES'],                  'Transportes Flotilla'),
    (['OBRA: LERMA'],                                                             'Lerma - Tenango'),
    (['OBRA: PLANTA'],                                                            'Planta Pegaso'),
]

cur.execute("SELECT folio_conciliacion, punto_de_carga, litros_facturados FROM diesel.facturas WHERE semana = 'Semana 28'")
rows = cur.fetchall()

conteo = {}
for folio, punto, lts in rows:
    t = (punto or '').upper()
    obra = 'Por Asignar'
    for keywords, o in OBRAS_MAP:
        for kw in keywords:
            if kw in t:
                obra = o
                break
        if obra != 'Por Asignar': break
    conteo.setdefault(obra, {'f': 0, 'l': 0})
    conteo[obra]['f'] += 1
    conteo[obra]['l'] += float(lts or 0)

print(f"\n{'Obra':<42} {'Fact':>5} {'Litros':>10}")
print("=" * 60)
for obra, d in sorted(conteo.items(), key=lambda x: -x[1]['l']):
    estado = '  ' if obra != 'Por Asignar' else '?? '
    print(f"  {estado}{obra:<40} {d['f']:>5} {d['l']:>10.1f}")
print("=" * 60)
total_f = sum(d['f'] for d in conteo.values())
total_l = sum(d['l'] for d in conteo.values())
print(f"  {'TOTAL':<42} {total_f:>5} {total_l:>10.1f}")

cur.close()
conn.close()
print("\nListo!")
