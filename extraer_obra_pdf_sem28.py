import pdfplumber
import psycopg2
import os, re, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PDF_DIR = r"c:\Users\JOSE\Desktop\Proyecto fenix\facturas\diesel\Semana_28"

# Mapeo de palabras clave en el texto del PDF a nombre de obra en el catalogo
OBRAS_MAP = [
    (['PLANTA DE ASFALTO', 'PLANTA ASFALTO', 'HUIXQUILUCAN', 'HUIX', 'P.A.H'], 'Planta Pegaso'),
    (['BACHEO TOLUCA', 'BACHEO', 'TOLUCA'], 'Bacheo Toluca y Calle Lerdo'),
    (['MEXICO TOLUCA', 'MEX-TOL', 'MEXICO-TOLUCA', 'CUERPO B', 'CUERPO A'], 'Mexico-Toluca'),
    (['LERMA TENANGO', 'LERMA-TENANGO', 'LERMA - TENANGO', 'LERMA', 'TENANGO'], 'Lerma - Tenango'),
    (['CHAMAPA', 'LECHERIA', 'CHAMAPA-LECHERIA'], 'Chamapa-Lecheria'),
    (['LA PROVIDENCIA', 'PROVIDENCIA'], 'Mexico-Toluca'),  # La Providencia es una estacion en Mex-Tol
    (['MARIMBA'], None),  # Marimba es el equipo, no la obra - necesitamos mas contexto
    (['CUARTELES', 'CUARTEL', 'VALLE DE MEXICO'], 'Cuarteles Generales Valle de Mexico'),
    (['EXPLANADA', 'DAMIAN CARMONA'], 'Explanada Damian Carmona'),
    (['JALISCO', 'BD_JALISCO'], 'Jalisco'),
    (['FLOTILLA', 'TRANSPORTES'], 'Transportes Flotilla'),
    (['DELEGACION SAN PEDRO', 'SAN PEDRO', 'CALLE REVOLUCION', 'LERDO'], 'Calle Revolucion y Calle Lerdo, en la Delegacion San Pedro'),
]

def extraer_obra_de_pdf(pdf_path):
    """Extrae el texto de la obra que aparece despues de Fecha de Vencimiento."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue
                lines = text.split('\n')
                for line in lines:
                    if 'Fecha de Vencimiento' in line or 'FECHA DE VENCIMIENTO' in line:
                        # Todo lo que viene despues de la fecha
                        # Patron: "Fecha de Vencimiento: DD/MM/YYYY TEXTO_DE_OBRA..."
                        m = re.search(r'Fecha de Vencimiento:\s*\d{2}/\d{2}/\d{4}\s*(.+)', line, re.IGNORECASE)
                        if m:
                            texto_obra = m.group(1).strip()
                            return texto_obra
    except Exception as e:
        print(f"  ERROR leyendo PDF {pdf_path}: {e}")
    return None

def mapear_obra(texto):
    """Mapea el texto libre del PDF al nombre de obra del catalogo."""
    if not texto:
        return 'Por Asignar', texto
    texto_upper = texto.upper()
    for keywords, obra_nombre in OBRAS_MAP:
        for kw in keywords:
            if kw in texto_upper:
                if obra_nombre is None:
                    return 'Por Asignar (revisar)', texto
                return obra_nombre, texto
    return 'Por Asignar', texto

# Conectar a Postgres
conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor()
print("Conectado a PostgreSQL")

# Obtener todas las facturas de Semana 28 que tienen folio DPC-28
cur.execute("""
    SELECT id, folio_conciliacion, folio_factura 
    FROM diesel.facturas 
    WHERE semana = 'Semana 28'
    ORDER BY folio_factura
""")
facturas_pg = cur.fetchall()
print(f"Facturas Semana 28 en Postgres: {len(facturas_pg)}")

# Obtener lista de PDFs en la carpeta
pdfs_disponibles = {}
for f in os.listdir(PDF_DIR):
    if f.endswith('.pdf'):
        # El nombre del PDF contiene el folio: DPC180725R47_CFDI_A10361_20260706.pdf
        # El folio en el XML es A10361 -> en BD guardamos como "10361"
        m = re.search(r'_CFDI_A(\d+)_', f)
        if m:
            folio_num = m.group(1)
            pdfs_disponibles[folio_num] = os.path.join(PDF_DIR, f)

print(f"PDFs disponibles: {len(pdfs_disponibles)}")

print("\n=== PROCESANDO FACTURAS ===")
actualizados = 0
sin_pdf = 0
sin_obra = 0

for fac_id, folio_conc, folio_fac in facturas_pg:
    folio_fac_str = str(folio_fac or '').strip()
    
    # Buscar el PDF correspondiente
    pdf_path = pdfs_disponibles.get(folio_fac_str)
    if not pdf_path:
        # Intentar busqueda alternativa
        for num, path in pdfs_disponibles.items():
            if folio_fac_str in num or num in folio_fac_str:
                pdf_path = path
                break
    
    if not pdf_path:
        sin_pdf += 1
        print(f"  [SIN PDF] {folio_conc} | Folio: {folio_fac_str}")
        continue
    
    # Extraer texto de obra del PDF
    texto_obra = extraer_obra_de_pdf(pdf_path)
    obra_nombre, texto_original = mapear_obra(texto_obra)
    
    # Actualizar en Postgres
    cur.execute("""
        UPDATE diesel.facturas 
        SET punto_de_carga = %s
        WHERE id = %s
    """, (texto_original or 'Sin descripcion en PDF', fac_id))
    
    # Si encontramos una obra del catalogo, actualizamos tambien esa columna si existe
    # Por ahora guardamos el texto completo en punto_de_carga
    actualizados += 1
    
    estado = "OK" if obra_nombre != 'Por Asignar' else "??"
    print(f"  [{estado}] {folio_conc} | Folio: {folio_fac_str} | Obra: {obra_nombre}")
    print(f"        Texto PDF: {texto_obra}")

conn.commit()
print(f"\n=== RESULTADO ===")
print(f"  Actualizados: {actualizados}")
print(f"  Sin PDF:      {sin_pdf}")

# Mostrar resumen por obra
cur.execute("""
    SELECT punto_de_carga, COUNT(*), ROUND(SUM(litros_facturados),1) 
    FROM diesel.facturas 
    WHERE semana = 'Semana 28'
    GROUP BY punto_de_carga 
    ORDER BY SUM(litros_facturados) DESC
""")
print("\nSemana 28 - Litros por Obra (del PDF):")
for r in cur.fetchall():
    print(f"  {r[1]:3d} facturas | {r[2]:8.1f} Lts | {r[0]}")

cur.close()
conn.close()
print("\nListo!")
