import psycopg2, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor()

OBRAS_KEYWORDS = [
    'PLANTA DE ASFALTO','PLANTA ASFALTO','HUIXQUILUCAN','TANQUE PEGASO','PLANTA PEGASO','PEGASO',
    'MAQUINARIA PEGASO','DESASOLVE','DEZAZOLVE','VICENTE LOMBARDO','LOMBARDO','ALFREDO DEL MAZO',
    'BACHEO','MEXICO TOLUCA','MEXICO-TOLUCA','PROVIDENCIA','LERMA','TENANGO',
    'FLOTILLA','TRANSPORTES'
]

cur.execute("""
    SELECT folio_conciliacion, fecha, obra_destino, equipo, litros, tipo_movimiento, origen, responsable
    FROM diesel.consumos
    WHERE semana = 'Semana 28'
    ORDER BY obra_destino, fecha
""")
rows = cur.fetchall()

sin_clasificar = []
for r in rows:
    obra = str(r[2] or '').upper()
    match = any(kw in obra for kw in OBRAS_KEYWORDS)
    if not match:
        sin_clasificar.append(r)

print(f"Consumos SIN CLASIFICAR Semana 28: {len(sin_clasificar)} movimientos")
print()
print(f"{'FOLIO':<22} {'FECHA':<12} {'OBRA_DESTINO':<28} {'EQUIPO':<20} {'LITROS':>7}")
print("-" * 96)
for r in sin_clasificar:
    print(f"  {str(r[0]):<20} {str(r[1]):<12} {str(r[2] or ''):<28} {str(r[3] or ''):<20} {float(r[4] or 0):>7.1f}")

total = sum(float(r[4] or 0) for r in sin_clasificar)
print("-" * 96)
print(f"  TOTAL:  {total:.1f} Lts en {len(sin_clasificar)} movimientos")

print(f"\nObras distintas sin clasificar:")
obras_distintas = {}
for r in sin_clasificar:
    o = str(r[2] or 'Sin obra')
    obras_distintas[o] = obras_distintas.get(o, 0) + float(r[4] or 0)
for o, lts in sorted(obras_distintas.items(), key=lambda x: -x[1]):
    print(f"  -> \"{o}\"  :  {lts:.1f} Lts")

conn.close()
