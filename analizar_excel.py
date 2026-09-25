import openpyxl, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
wb = openpyxl.load_workbook(r'gasolina/SEMANA 26 (1).xlsx', data_only=True)
ws = wb.active
print("=== Estructura SEMANA 26 (columnas A-H) ===")
for i, row in enumerate(ws.iter_rows(min_row=1, max_row=20, values_only=True)):
    print(f'R{i+1}: {[str(v)[:25] if v else None for v in list(row)[:8]]}')
