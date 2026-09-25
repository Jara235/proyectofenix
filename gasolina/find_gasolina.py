with open(r'servidor\templates\index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if 'id="gasolina' in line or 'function loadGasolina' in line:
            print(f'Line {i+1}: {line.strip()}')
