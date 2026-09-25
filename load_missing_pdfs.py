import os, re, sqlite3
import pdfplumber
db = sqlite3.connect('c:/Users/JOSE/Desktop/Proyecto fenix/fenix.db')
c = db.cursor()
folder = 'c:/Users/JOSE/Desktop/Proyecto fenix/facturas'
target_folios = ['10198', '10213', '10214', '10216', '10217', '10225', '10226']
for f in os.listdir(folder):
    if f.endswith('.pdf') and any(tf in f for tf in target_folios) and '(1)' not in f:
        path = os.path.join(folder, f)
        try:
            with pdfplumber.open(path) as pdf:
                text = ''
                for p in pdf.pages: text += p.extract_text() + '\n'
                m_folio = re.search(r'FACTURA No.\s*[A-Za-z-]?\s*(\d+)', text)
                m_fecha = re.search(r'FECHA:\s*(\d{4}-\d{2}-\d{2})', text)
                m_total = re.search(r'TOTAL\s*\$([\d,.]+)', text)
                litros_matches = re.findall(r'(\d+(?:\.\d+)?)\s*LTR', text)
                litros = sum([float(x.replace(',', '')) for x in litros_matches])
                if not m_folio: continue
                folio = m_folio.group(1)
                fecha = m_fecha.group(1) + 'T00:00:00' if m_fecha else ''
                total = float(m_total.group(1).replace(',', '')) if m_total else 0.0
                print(f'Loading Folio {folio} | Lts: {litros} | Total: {total}')
                c.execute("INSERT OR REPLACE INTO fenix_facturas_documentos (folio, fecha_emision, total, litros_totales, texto_pdf_extraido, subtotal) VALUES (?, ?, ?, ?, ?, 0)", (folio, fecha, total, litros, text))
        except Exception as e:
            print(f"Error reading {f}: {e}")
db.commit()
db.close()
