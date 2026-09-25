import openpyxl, os

files = [
    'acarreos/OBRA MEXICO TOLUCA 2026 (6).xlsx',
    'acarreos/OBRA LERMA 3 MARIAS 2026 (13).xlsx',
    'acarreos/OBRA ALFREDO DEL MAZO (9).xlsx'
]

for fpath in files:
    print("=" * 100)
    print(f"ARCHIVO: {fpath}")
    print("=" * 100)
    if not os.path.exists(fpath):
        print("NO EXISTE")
        continue
    
    wb = openpyxl.load_workbook(fpath, data_only=True)
    print(f"Hojas encontradas: {wb.sheetnames}")
    
    for sname in wb.sheetnames:
        ws = wb[sname]
        print(f"\n--- Hoja: '{sname}' (filas: {ws.max_row}, cols: {ws.max_column}) ---")
        # Mostrar primeras 15 filas no vacías
        non_empty = 0
        for r in range(1, min(ws.max_row + 1, 30)):
            vals = [ws.cell(r, c).value for c in range(1, min(ws.max_column + 1, 20))]
            if any(v is not None for v in vals):
                row_str = [str(v).strip() if v is not None else "" for v in vals]
                # Filtrar columnas vacías al final
                while row_str and row_str[-1] == "":
                    row_str.pop()
                if row_str:
                    print(f"  Fila {r:2d}: {row_str}")
                    non_empty += 1
                if non_empty >= 12:
                    break
