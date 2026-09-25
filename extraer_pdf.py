import os
import re
import pandas as pd

def try_extract():
    try:
        import PyPDF2
        return "PyPDF2"
    except ImportError:
        pass
    
    try:
        import fitz
        return "fitz"
    except ImportError:
        pass
    
    return None

lib = try_extract()
if not lib:
    print("NO_PDF_LIB")
    exit(1)

print(f"Using {lib}")

folder_path = r"c:\Users\JOSE\Desktop\Proyecto fenix\facturas"
pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]
xml_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.xml')]

# Get basenames without extension
xml_basenames = {os.path.splitext(f)[0] for f in xml_files}
orphaned_pdfs = [f for f in pdf_files if os.path.splitext(f)[0] not in xml_basenames]

print(f"Found {len(orphaned_pdfs)} orphaned PDFs (no XML).")

data = []

def extract_text_from_pdf(filepath):
    text = ""
    if lib == "PyPDF2":
        import PyPDF2
        try:
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Error PyPDF2 {filepath}: {e}")
    elif lib == "fitz":
        import fitz
        try:
            doc = fitz.open(filepath)
            for page in doc:
                text += page.get_text() + "\n"
        except Exception as e:
            print(f"Error fitz {filepath}: {e}")
    return text

for pdf in orphaned_pdfs:
    filepath = os.path.join(folder_path, pdf)
    text = extract_text_from_pdf(filepath)
    
    if not text.strip():
        continue
        
    # Basic Regex for CFDI PDF data (Gas station receipts often look similar)
    # This is a heuristic approach since PDFs vary wildly
    folio = pdf.replace('.pdf', '')
    folio_match = re.search(r'Folio\s*[:\-]\s*([A-Za-z0-9]+)', text, re.IGNORECASE)
    if folio_match:
        folio = folio_match.group(1)
        
    fecha = ""
    fecha_match = re.search(r'Fecha\s*[:\-]?\s*(\d{2,4}[-/]\d{2}[-/]\d{2,4})', text, re.IGNORECASE)
    if fecha_match:
        fecha = fecha_match.group(1)
        
    # Look for DIESEL or GASOLINA and try to grab liters (Cantidad)
    tipo_combustible = "Desconocido (PDF)"
    if "DIESEL" in text.upper() or "DIÉSEL" in text.upper():
        tipo_combustible = "Diésel (PDF)"
    elif "MAGNA" in text.upper() or "PREMIUM" in text.upper() or "GASOLINA" in text.upper():
        tipo_combustible = "Gasolina (PDF)"
        
    # Try to find Total (often $XXX.XX or just numbers near Total)
    total = 0.0
    total_match = re.search(r'Total\s*[:\$]?\s*(\d+[,.]\d{2})', text, re.IGNORECASE)
    if total_match:
        try:
            total = float(total_match.group(1).replace(',', ''))
        except:
            pass
            
    # Try to find Cantidad (Liters) - usually near the fuel word
    litros = 0.0
    litros_match = re.search(r'(\d+[,.]\d{2,4})\s*(LTR|Lts|Litros)', text, re.IGNORECASE)
    if litros_match:
        try:
            litros = float(litros_match.group(1).replace(',', ''))
        except:
            pass
            
    # If regex fails, just append what we got so user can fill manually
    data.append({
        'ARCHIVO_ORIGEN': pdf,
        'FOLIO_FACTURA': folio,
        'FECHA_FACTURA': fecha,
        'PROVEEDOR': "Extraído de PDF",
        'DESCRIPCION_SAT': "Verificar PDF manualmente",
        'TIPO_COMBUSTIBLE': tipo_combustible,
        'LITROS_FACTURADOS': litros,
        'PRECIO_UNITARIO': 0, # Hard to reliably parse from random PDFs
        'IMPORTE_TOTAL': total
    })

if data:
    # Append to existing excel
    excel_path = r"c:\Users\JOSE\Desktop\Proyecto fenix\FACTURAS_EXTRAIDAS_REVISION.xlsx"
    try:
        existing_df = pd.read_excel(excel_path)
        new_df = pd.DataFrame(data)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        
        # Sort again
        combined_df = combined_df.sort_values(by=['TIPO_COMBUSTIBLE', 'FECHA_FACTURA'], ascending=[True, True])
        combined_df.to_excel(excel_path, index=False)
        print(f"Se añadieron {len(data)} facturas desde PDFs huérfanos al archivo de revisión.")
    except Exception as e:
        print(f"Error updating excel: {e}")
else:
    print("No se encontraron PDFs huérfanos válidos o legibles.")
