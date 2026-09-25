import os
import re
import pandas as pd
import PyPDF2

folder_path = r"c:\Users\JOSE\Desktop\Proyecto fenix\facturas"
excel_path = r"c:\Users\JOSE\Desktop\Proyecto fenix\FACTURAS_EXTRAIDAS_REVISION.xlsx"

try:
    df = pd.read_excel(excel_path)
except Exception as e:
    print(f"Error reading excel: {e}")
    exit(1)

# Ensure new column exists
if 'DESTINO_REPORTADO_PDF' not in df.columns:
    df['DESTINO_REPORTADO_PDF'] = ""

pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]

# Create a mapping from Folio to PDF path, or Basename to PDF path
# Sometimes folios have prefixes, so let's match by basename
pdf_map = {}
for pdf in pdf_files:
    basename = os.path.splitext(pdf)[0].lower()
    pdf_map[basename] = os.path.join(folder_path, pdf)

count_updated = 0

for index, row in df.iterrows():
    archivo_origen = str(row.get('ARCHIVO_ORIGEN', ''))
    basename = os.path.splitext(archivo_origen)[0].lower()
    
    pdf_path = pdf_map.get(basename)
    
    if pdf_path and os.path.exists(pdf_path):
        text = ""
        try:
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            continue
            
        # Search for "Fecha de Vencimiento: DD/MM/YYYY [DESTINO]"
        # Handle cases with or without space, different date formats
        match = re.search(r'Fecha de Vencimiento\s*:\s*\d{2}[-/]\d{2}[-/]\d{2,4}\s*(.+)', text, re.IGNORECASE)
        if match:
            destino = match.group(1).strip()
            df.at[index, 'DESTINO_REPORTADO_PDF'] = destino
            count_updated += 1
        else:
            # Maybe the OCR broke the line, try a broader search around 'Vencimiento'
            match2 = re.search(r'Vencimiento.*?\d{4}\s+([A-Za-z].+)', text, re.IGNORECASE)
            if match2:
                destino = match2.group(1).strip()
                df.at[index, 'DESTINO_REPORTADO_PDF'] = destino
                count_updated += 1

# Save back
df.to_excel(excel_path, index=False)
print(f"Se actualizaron {count_updated} registros con el destino extraido del PDF.")
