import PyPDF2
import sys

sys.stdout.reconfigure(encoding='utf-8')
file_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\facturas\FACTURA J.D.J. JUNIO2026.pdf'

text = ""
with open(file_path, 'rb') as f:
    reader = PyPDF2.PdfReader(f)
    for page in reader.pages:
        text += page.extract_text() + "\n"

# Let's print the first 1000 characters to see if there are dates
lines = text.split('\n')
for i, line in enumerate(lines[:50]):
    print(f"Line {i}: {line.strip()}")
