with open('app_admin.py', 'r', encoding='utf-8') as f:
    code = f.read()

import re
matches = re.finditer(r'@app\.route\([^\)]+\)\s+def\s+([a-zA-Z0-9_]+)', code)
for m in matches:
    fn = m.group(1)
    if 'pdf' in fn or 'xml' in fn or 'factura' in fn or 'descarga' in fn:
        print(f"Function: {fn}")
