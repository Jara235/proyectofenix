with open('app_admin.py', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if '@app.route' in line:
        print(f"Line {i+1}: {line.strip()}")
