with open('app_admin.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'archivo_pdf' in line or 'archivo_xml' in line or 'send_file' in line:
        print(f"Line {idx+1}: {line.strip()}")
