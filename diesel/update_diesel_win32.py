import win32com.client as win32
import os

excel = win32.Dispatch('Excel.Application')
excel.Visible = False
excel.DisplayAlerts = False

filepath = os.path.abspath('c:/Users/JOSE/Desktop/Proyecto fenix/MAESTRO_CONTROL_DIESEL_NUEVO.xlsx')
print(f'Opening {filepath}')
wb = excel.Workbooks.Open(filepath)

try:
    ws = wb.Sheets('BD_DIESEL')
    last_row = ws.Cells(ws.Rows.Count, 1).End(-4162).Row
    
    print(f'Applying formula to row 2 to {last_row}')
    if last_row >= 2:
        formula_str = '=IF(A2="", "", IF(ROUND(SUMIFS(BD_FACTURAS!K:K, BD_FACTURAS!A:A, A2), 2) = ROUND(K2, 2), "✅ Cuadrado", "⚠️ Diferencia"))'
        ws.Range(f'N2:N{last_row}').Formula = formula_str
        
    wb.Save()
    print('Saved successfully')
finally:
    wb.Close()
    excel.Quit()

