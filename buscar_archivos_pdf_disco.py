import os

def search_pdf_files():
    search_dirs = [
        r'c:\Users\JOSE\Desktop\Proyecto fenix',
        r'c:\Users\JOSE\Desktop'
    ]

    all_pdfs = []
    all_xmls = []

    print("=== SEARCHING DISK FOR PDF / XML FILES ===")
    for root_dir in search_dirs:
        for root, dirs, files in os.walk(root_dir):
            # Skip node_modules or venv or .git
            if any(skip in root.lower() for skip in ['node_modules', '.git', 'venv', 'env', '__pycache__', 'antigravity']):
                continue
            for f in files:
                f_lower = f.lower()
                if f_lower.endswith('.pdf'):
                    all_pdfs.append(os.path.join(root, f))
                elif f_lower.endswith('.xml'):
                    all_xmls.append(os.path.join(root, f))

    print(f"Total PDF files found: {len(all_pdfs)}")
    print(f"Total XML files found: {len(all_xmls)}")

    # Check if any pdf file contains A10268, A10272, A10321, etc.
    interesting_terms = ['10268', '10272', '10274', '10278', '10321', '10322', '10329', '10267', 'castilla']
    
    print("\n--- Matching PDF/XML files ---")
    matched = 0
    for p in all_pdfs + all_xmls:
        base = os.path.basename(p).lower()
        if any(term in base for term in interesting_terms):
            print(f"Match: {p}")
            matched += 1

    if matched == 0:
        print("No PDF or XML files found on disk matching the folios A10268, A10272, A10321, etc.")

    print("\n--- All PDFs found on disk ---")
    for p in all_pdfs[:30]:
        print(f" - {p}")

if __name__ == '__main__':
    search_pdf_files()
