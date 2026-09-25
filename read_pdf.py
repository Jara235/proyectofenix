import PyPDF2
import sys

sys.stdout.reconfigure(encoding='utf-8')
file_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\facturas\FACTURA J.D.J. JUNIO2026.pdf'
try:
    with open(file_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        print(text[:2000])
except Exception as e:
    print(f"Error reading PDF: {e}")
