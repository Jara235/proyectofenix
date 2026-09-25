import pdfplumber
import sys

pdf_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\Jalisco\REPORTE COMBUSTIBLES JALISCO SEM #26,.pdf'
print(f"Reading {pdf_path}...")
try:
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        tables = page.extract_tables()
        for i, table in enumerate(tables):
            print(f"--- Table {i} ---")
            for row in table:
                print(row)
except Exception as e:
    print("Error:", e)
