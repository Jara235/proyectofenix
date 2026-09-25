with open('app_admin.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines in app_admin.py: {len(lines)}")
for idx, line in enumerate(lines, start=1):
    if '@app.route' in line and ('tag' in line.lower() or 'pase' in line.lower() or 'caseta' in line.lower()):
        print(f"L{idx:04d}: {line.strip()}")
        # print next 10 lines
        for j in range(idx, min(idx+25, len(lines))):
            print(f"   {lines[j].strip()}")
        print("-" * 50)
