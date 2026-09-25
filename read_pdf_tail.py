import PyPDF2
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')
file_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\facturas\FACTURA J.D.J. JUNIO2026.pdf'

text = ""
with open(file_path, 'rb') as f:
    reader = PyPDF2.PdfReader(f)
    for page in reader.pages:
        text += page.extract_text() + "\n"

print(text[-2000:])
