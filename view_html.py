import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
with open(r'servidor\templates\index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i in range(198, 220):
        if i < len(lines):
            print(f'{i+1}: {lines[i].rstrip()}')
    print("---")
    for i in range(390, 440):
        if i < len(lines):
            print(f'{i+1}: {lines[i].rstrip()}')
