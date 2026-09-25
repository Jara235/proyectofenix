import psycopg2
import pdfplumber
import os, re, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PDF_DIR = r"c:\Users\JOSE\Desktop\Proyecto fenix\facturas\diesel\Semana_28"

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor()

# Mapeo CORREGIDO con todos los patrones
OBRAS_MAP = [
    (['PLANTA DE ASFALTO', 'PLANTA ASFALTO', 'HUIXQUILUCAN', 'TANQUE PEGASO',
      'PLANTA PEGASO', 'PEGASO', 'P.A.H'],                                           'Planta Pegaso'),
    (['MAQUINARIA PEGASO', 'MAQUINARIA PEG'],                                         'Maquinaria Pegaso'),
    (['DESASOLVE', 'DEZAZOLVE', 'VICENTE LOMBARDO', 'LOMBARDO'],                      'Vicente Lombardo'),
    (['ALFREDO DEL MAZO', 'ALFREDO MAZO'],                                            'Alfredo del Mazo'),
    (['BACHEO TOLUCA', 'BACHEO'],                                                     'Bacheo Toluca y Calle Lerdo'),
    (['MEXICO TOLUCA', 'MEX-TOL', 'MEXICO-TOLUCA', 'MEXICO - TOLUCA',
      'MÉXICO-TOLUCA', 'MÉXICO- TOLUCA', 'MÉXICO - TOLUCA',
      'LA PROVIDENCIA', 'PROVIDENCIA', 'PETROLIZADORA'],                              'Mexico-Toluca'),
    (['LERMA TENANGO', 'LERMA-TENANGO', 'LERMA - TENANGO', 'LERMA'],                  'Lerma - Tenango'),
    (['CHAMAPA', 'LECHERIA'],                                                         'Chamapa-Lecheria'),
    (['CUARTELES', 'CUARTEL', 'VALLE DE MEXICO'],                                     'Cuarteles Generales Valle de Mexico'),
    (['EXPLANADA', 'DAMIAN CARMONA'],                                                 'Explanada Damian Carmona'),
    (['JALISCO'],                                                                     'Jalisco'),
    (['FLOTILLA', 'TRANSPORTES FLOTILLA'],                                            'Transportes Flotilla'),
]

def mapear_obra(texto):
    if not texto: return 'Por Asignar'
    t = texto.upper()
    for keywords, obra in OBRAS_MAP:
        for kw in keywords:
            if kw in t:
                return obra
    return 'Por Asignar'

def extraer_texto_pdf(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ''
                for line in text.split('\n'):
                    m = re.search(r'Fecha de Vencimiento:\s*\d{2}/\d{2}/\d{4}\s*(.+)', line, re.IGNORECASE)
                    if m:
                        return m.group(1).strip()
    except:
        pass
    return None

pdfs = {}
for f in os.listdir(PDF_DIR):
    if f.endswith('.pdf'):
        m = re.search(r'_CFDI_A(\d+)_', f)
        if m:
            pdfs[m.group(1)] = os.path.join(PDF_DIR, f)

# Actualizar solo los "Por Asignar" que ahora se pueden resolver
cur.execute("""
    SELECT id, folio_conciliacion, folio_factura, punto_de_carga
    FROM diesel.facturas 
    WHERE semana = 'Semana 28'
    ORDER BY folio_factura
""")
facturas = cur.fetchall()

print("=== RECLASIFICACION CON MAPEO CORREGIDO ===")
actualizados = 0
for fac_id, folio_conc, folio_fac, punto_actual in facturas:
    pdf_path = pdfs.get(str(folio_fac or ''))
    if not pdf_path:
        continue
    texto = extraer_texto_pdf(pdf_path)
    obra = mapear_obra(texto)
    cur.execute("UPDATE diesel.facturas SET punto_de_carga = %s WHERE id = %s", (texto or punto_actual, fac_id))
    estado = 'OK' if obra != 'Por Asignar' else '??'
    print(f"  [{estado}] {folio_conc:20s} | {obra:35s} | {(texto or '')[:45]}")
    actualizados += 1

conn.commit()

# Resumen final
cur.execute("""
    SELECT folio_factura, punto_de_carga, litros_facturados 
    FROM diesel.facturas WHERE semana = 'Semana 28'
""")
rows = cur.fetchall()
conteo = {}
for _, punto, lts in rows:
    t = (punto or '').upper()
    obra = 'Por Asignar'
    for keywords, o in OBRAS_MAP:
        for kw in keywords:
            if kw in t:
                obra = o
                break
        if obra != 'Por Asignar': break
    conteo.setdefault(obra, {'f':0, 'l':0})
    conteo[obra]['f'] += 1
    conteo[obra]['l'] += float(lts or 0)

print(f"\n{'='*60}")
print(f"{'OBRA':<40} {'FAC':>4} {'LITROS':>10}")
print("-"*60)
for obra, d in sorted(conteo.items(), key=lambda x: -x[1]['l']):
    print(f"  {obra:<38} {d['f']:>4} {d['l']:>10.1f}")
print("-"*60)
print(f"  {'TOTAL':<38} {sum(d['f'] for d in conteo.values()):>4} {sum(d['l'] for d in conteo.values()):>10.1f}")

cur.close()
conn.close()
print("\nListo!")
