with open('app_admin.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'resumen/gasolina' in line or 'todas_las_facturas' in line:
        print(f"Line {idx+1}: {line.strip()}")
