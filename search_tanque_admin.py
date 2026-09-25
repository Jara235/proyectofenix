with open('app_admin.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines, 1):
    if any(k in line.lower() for k in ['tanque pegaso', 'tanque_pegaso', 'tanques']):
        print(f"Line {idx}: {line.strip()[:120]}")
