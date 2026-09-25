import pdfplumber, os

for pdf_name in ['AUTORIZACION TAG JDJ.pdf', 'AUTORIZACION TAG TRD.pdf']:
    path = os.path.join('TAGS', 'aurotirzaciones', pdf_name)
    print(f"\n=======================================================")
    print(f"ARCHIVO: {path}")
    print(f"=======================================================")
    with pdfplumber.open(path) as pdf:
        for idx, page in enumerate(pdf.pages, start=1):
            print(f"\n--- PÁGINA {idx} ---")
            text = page.extract_text()
            print(text)
            tables = page.extract_tables()
            if tables:
                print("\n--- TABLAS EXTRAÍDAS ---")
                for t in tables:
                    for row in t:
                        print(" | ".join([str(c or '').strip() for c in row]))
