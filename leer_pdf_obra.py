import pdfplumber
import sys, io, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PDF_DIR = r"c:\Users\JOSE\Desktop\Proyecto fenix\facturas\diesel\Semana_28"

# Leer los primeros 3 PDFs para entender el formato
pdfs = [f for f in os.listdir(PDF_DIR) if f.endswith('.pdf')][:3]

for pdf_file in pdfs:
    path = os.path.join(PDF_DIR, pdf_file)
    print(f"\n{'='*60}")
    print(f"PDF: {pdf_file}")
    print(f"{'='*60}")
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    print(f"  [{i:3d}] {line}")
