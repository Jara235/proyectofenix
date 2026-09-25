import psycopg2, pdfplumber
from psycopg2.extras import DictCursor

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

print("=== MOVIMIENTOS DE BRYAN / BRAYAN EN tags.movimientos ===")
cur.execute("""
    SELECT id, empresa, mes, semana, tag, no_economico, responsable, tipo_unidad, placas, obra_asignada, fecha, importe, archivo_origen
    FROM tags.movimientos
    WHERE responsable ILIKE '%BRYAN%' OR responsable ILIKE '%BRAYAN%' 
       OR no_economico ILIKE '%BRYAN%' OR no_economico ILIKE '%BRAYAN%'
       OR tag ILIKE '%30874326%' OR tag ILIKE '%30874329%'
    ORDER BY fecha;
""")
movs = cur.fetchall()
print(f"Total movimientos encontrados: {len(movs)}")
for m in movs:
    print(dict(m))

print("\n=== COMPARAR TODAS LAS AUTORIZACIONES DE LOS PDFS VS BD ===")
# Leer PDF JDJ
pdf_jdj = []
with pdfplumber.open('TAGS/aurotirzaciones/AUTORIZACION TAG JDJ.pdf') as pdf:
    for p in pdf.pages:
        tbl = p.extract_tables()
        if tbl:
            for t in tbl:
                for row in t:
                    if len(row) >= 9 and row[0] and row[0].isdigit():
                        pdf_jdj.append(row)

print(f"\nPDF JDJ ({len(pdf_jdj)} filas):")
for r in pdf_jdj:
    print(r)

# Leer PDF TRD
pdf_trd = []
with pdfplumber.open('TAGS/aurotirzaciones/AUTORIZACION TAG TRD.pdf') as pdf:
    for p in pdf.pages:
        tbl = p.extract_tables()
        if tbl:
            for t in tbl:
                for row in t:
                    if len(row) >= 9 and row[0] and row[0].isdigit():
                        pdf_trd.append(row)

print(f"\nPDF TRD ({len(pdf_trd)} filas):")
for r in pdf_trd:
    print(r)

conn.close()
