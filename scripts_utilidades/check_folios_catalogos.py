import openpyxl

excel_path = r"c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_DIESEL_NUEVO.xlsx"

try:
    wb = openpyxl.load_workbook(excel_path, data_only=True)
    
    print("=== OBRAS EN CATALOGOS ===")
    sheet_cat = wb["CATALOGOS"]
    for row in sheet_cat.iter_rows(min_row=1, max_row=15, min_col=1, max_col=1, values_only=True):
        if row[0]:
            print(row[0])
            
    print("\n=== ENCABEZADOS BD_DIESEL ===")
    sheet_bd = wb["BD_DIESEL"]
    print([cell.value for cell in sheet_bd[1]])
    
    print("\n=== ENCABEZADOS BD_FACTURAS ===")
    sheet_fac = wb["BD_FACTURAS"]
    print([cell.value for cell in sheet_fac[1]])

except Exception as e:
    print(f"Error: {e}")
