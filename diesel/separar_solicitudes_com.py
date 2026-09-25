import win32com.client as win32
import os

excel_path = r"c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_DIESEL_NUEVO.xlsx"

try:
    excel = win32.DispatchEx('Excel.Application')
    excel.Visible = False
    excel.DisplayAlerts = False
    
    wb = excel.Workbooks.Open(excel_path)
    
    # Check if BD_SOLICITUDES exists
    sheet_sol = None
    for sh in wb.Sheets:
        if sh.Name == "BD_SOLICITUDES":
            sheet_sol = sh
            break
            
    if not sheet_sol:
        sheet_sol = wb.Sheets.Add(After=wb.Sheets(wb.Sheets.Count))
        sheet_sol.Name = "BD_SOLICITUDES"
    else:
        sheet_sol.Cells.Clear()
        
    sheet_bd = wb.Sheets("BD_DIESEL")
    
    # Copy headers (A1 to O1)
    sheet_bd.Range("A1:O1").Copy(sheet_sol.Range("A1"))
    
    # Collect rows to move
    max_row = sheet_bd.Cells(sheet_bd.Rows.Count, "E").End(-4162).Row # xlUp = -4162
    
    rows_to_move = []
    
    # Loop backwards
    for r in range(max_row, 1, -1):
        mov_type = str(sheet_bd.Cells(r, 5).Value).upper()
        if "SOLICITUD" in mov_type:
            # Get values of A:O
            vals = sheet_bd.Range(sheet_bd.Cells(r, 1), sheet_bd.Cells(r, 15)).Value
            rows_to_move.append((r, vals))
            
    # Write to BD_SOLICITUDES
    current_row = 2
    for r, vals in reversed(rows_to_move):
        sheet_sol.Range(sheet_sol.Cells(current_row, 1), sheet_sol.Cells(current_row, 15)).Value = vals
        # Delete from BD_DIESEL
        sheet_bd.Rows(r).Delete()
        current_row += 1
        
    # Re-apply formulas to ensure folios and weeks are correct
    
    # BD_DIESEL formulas
    # SEMANA = "=IF(B2=\"\",\"\", \"Semana \"&WEEKNUM(B2,2))"
    # FOLIO = "=IF(B2=\"\",\"\", IFERROR(VLOOKUP(E2,CATALOGOS!$J$2:$K$50,2,0),\"XX\") & \"-\" & IFERROR(VLOOKUP(F2,CATALOGOS!$A$2:$B$50,2,0),\"XX\") & \"-\" & WEEKNUM(B2,2) & \"-\" & TEXT(ROW()-1,\"000\"))"
    sheet_bd.Range("C2:C1000").Formula = '=IF(B2="","", "Semana "&WEEKNUM(B2,2))'
    sheet_bd.Range("A2:A1000").Formula = '=IF(B2="","", IFERROR(VLOOKUP(E2,CATALOGOS!$J$2:$K$50,2,0),"XX") & "-" & IFERROR(VLOOKUP(F2,CATALOGOS!$A$2:$B$50,2,0),"XX") & "-" & WEEKNUM(B2,2) & "-" & TEXT(ROW()-1,"000"))'

    # BD_SOLICITUDES formulas (same logic, but operation is always 'SO' or we can still look it up from Col E)
    sheet_sol.Range("C2:C1000").Formula = '=IF(B2="","", "Semana "&WEEKNUM(B2,2))'
    sheet_sol.Range("A2:A1000").Formula = '=IF(B2="","", IFERROR(VLOOKUP(E2,CATALOGOS!$J$2:$K$50,2,0),"XX") & "-" & IFERROR(VLOOKUP(F2,CATALOGOS!$A$2:$B$50,2,0),"XX") & "-" & WEEKNUM(B2,2) & "-" & TEXT(ROW()-1,"000"))'

    # BD_FACTURAS formulas (just in case they got messed up)
    sheet_fac = wb.Sheets("BD_FACTURAS")
    sheet_fac.Range("D2:D1000").Formula = '=IF(C2="","", "Semana "&WEEKNUM(C2,2))'
    sheet_fac.Range("A2:A1000").Formula = '=IF(C2="","", "FA" & "-" & IFERROR(VLOOKUP(F2,CATALOGOS!$A$2:$B$50,2,0),"XX") & "-" & WEEKNUM(C2,2) & "-" & TEXT(ROW()-1,"000"))'

    # AutoFit columns
    sheet_sol.Columns.AutoFit()

    wb.Save()
    wb.Close()
    print(f"Completado exitosamente. Se separaron {len(rows_to_move)} solicitudes.")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    excel.Quit()
