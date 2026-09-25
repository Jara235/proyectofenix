import openpyxl
from copy import copy

excel_path = r"c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_DIESEL_NUEVO.xlsx"

try:
    wb = openpyxl.load_workbook(excel_path)
    
    if "BD_SOLICITUDES" not in wb.sheetnames:
        sheet_sol = wb.create_sheet("BD_SOLICITUDES")
    else:
        sheet_sol = wb["BD_SOLICITUDES"]
        sheet_sol.delete_rows(1, sheet_sol.max_row)
        
    sheet_bd = wb["BD_DIESEL"]
    
    # 1. Copiar encabezados
    headers = []
    for col in range(1, sheet_bd.max_column + 1):
        cell = sheet_bd.cell(row=1, column=col)
        new_cell = sheet_sol.cell(row=1, column=col)
        new_cell.value = cell.value
        headers.append(cell.value)
        if cell.has_style:
            new_cell.font = copy(cell.font)
            new_cell.border = copy(cell.border)
            new_cell.fill = copy(cell.fill)
            
    # 2. Leer todas las filas
    rows_diesel = []
    rows_solicitudes = []
    
    max_c = sheet_bd.max_column
    for row_idx in range(2, sheet_bd.max_row + 1):
        mov_type = str(sheet_bd.cell(row=row_idx, column=5).value or "").strip().upper()
        # Verificar si la fila esta completamente vacia
        is_empty = all(sheet_bd.cell(row=row_idx, column=c).value is None for c in range(1, max_c + 1))
        
        if is_empty:
            continue
            
        row_data = [sheet_bd.cell(row=row_idx, column=c).value for c in range(1, max_c + 1)]
        
        if "SOLICITUD" in mov_type:
            rows_solicitudes.append(row_data)
        else:
            rows_diesel.append(row_data)
            
    # 3. Limpiar BD_DIESEL y reescribir
    sheet_bd.delete_rows(2, sheet_bd.max_row)
    
    for r_idx, row_data in enumerate(rows_diesel, start=2):
        for c_idx, val in enumerate(row_data, start=1):
            # No copiar formulas, las inyectaremos con powershell despues
            if isinstance(val, str) and val.startswith('='):
                continue
            sheet_bd.cell(row=r_idx, column=c_idx).value = val
            
    # 4. Escribir BD_SOLICITUDES
    for r_idx, row_data in enumerate(rows_solicitudes, start=2):
        for c_idx, val in enumerate(row_data, start=1):
            if isinstance(val, str) and val.startswith('='):
                continue
            sheet_sol.cell(row=r_idx, column=c_idx).value = val
            
    # Autoajuste basico
    for col in sheet_sol.columns:
        sheet_sol.column_dimensions[col[0].column_letter].width = 15

    wb.save(excel_path)
    print(f"Exito. {len(rows_solicitudes)} solicitudes separadas y {len(rows_diesel)} registros de carga mantenidos.")

except Exception as e:
    print(f"Error: {e}")
