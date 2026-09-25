import pdfplumber, json

def clean_val(v):
    if v is None: return ''
    return str(v).replace('\n', ' ').strip()

def parse_pdf(path):
    rows = []
    with pdfplumber.open(path) as pdf:
        for p in pdf.pages:
            tables = p.extract_tables()
            for t in tables:
                for r in t:
                    cleaned = [clean_val(c) for c in r]
                    if cleaned and cleaned[0].isdigit():
                        rows.append(cleaned)
    return rows

jdj_rows = parse_pdf('TAGS/aurotirzaciones/AUTORIZACION TAG JDJ.pdf')
trd_rows = parse_pdf('TAGS/aurotirzaciones/AUTORIZACION TAG TRD.pdf')

print(f"=== AUTORIZACIONES JDJ ({len(jdj_rows)} filas) ===")
for r in jdj_rows:
    print(r)

print(f"\n=== AUTORIZACIONES TRD ({len(trd_rows)} filas) ===")
for r in trd_rows:
    print(r)
