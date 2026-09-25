with open('servidor/templates/admin/admin_resumen.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'modulo-gasolina' in line or 'BLOQUE 4' in line or 'tbody-gasolina' in line or 'renderGasolinaUI' in line:
        print(f"Line {idx+1}: {line.strip()}")
