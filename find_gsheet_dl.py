import os, glob

for root, dirs, files in os.walk('.'):
    for f in files:
        if f.endswith('.py'):
            fp = os.path.join(root, f)
            try:
                with open(fp, 'r', encoding='utf-8', errors='ignore') as s:
                    c = s.read()
                    if '1Er1qP6Gt1pwNmTXmOVLEpaY_cpbGlLUg' in c or 'export?format=xlsx' in c or 'google_sheets' in c:
                        print(fp)
            except:
                pass
