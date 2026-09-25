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

# Calculate total litros
litros_total = 0.0
for line in text.split('\n'):
    if 'PL/' in line and '/EXP/' in line:
        try:
            val = float(line.split('PL/')[0].strip())
            litros_total += val
        except:
            pass

# Find subtotal, iva, total
subtotal = 0.0
iva = 0.0
total = 0.0

matches = re.findall(r'SubTotal\s+([0-9,.]+)', text)
if matches: subtotal = float(matches[-1].replace(',', ''))
matches = re.findall(r'I.V.A\s+.*?\s+([0-9,.]+)', text)
if matches: iva = float(matches[-1].replace(',', ''))
matches = re.findall(r'Total\s+([0-9,.]+)', text)
if matches: total = float(matches[-1].replace(',', ''))

print(f"Litros: {litros_total:.2f}")
print(f"Subtotal: {subtotal}")
print(f"IVA: {iva}")
print(f"Total: {total}")
