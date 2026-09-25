import os, glob

for root, dirs, files in os.walk('.'):
    if '.git' in root or 'node_modules' in root or '__pycache__' in root:
        continue
    for f in files:
        if f.endswith('.py') or f.endswith('.json') or f.endswith('.md'):
            filepath = os.path.join(root, f)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as fp:
                    content = fp.read()
                    if 'docs.google.com' in content or 'sheets' in content.lower() or 'sync' in content.lower() or 'importar' in content.lower():
                        if any(x in content for x in ['docs.google.com/spreadsheets', 'gspread', 'sheet_id', 'SPREADSHEET_ID']):
                            print(filepath)
            except Exception as e:
                pass
