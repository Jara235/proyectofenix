import re

with open('app_admin.py', 'r', encoding='utf-8') as f:
    code = f.read()

matches = re.finditer(r'@app\.route\(([\'"][^\'"]+[\'"])', code)
for m in matches:
    route = m.group(1)
    if any(k in route.lower() for k in ['factura', 'gasolina', 'descargar', 'pdf', 'xml']):
        print(route)
