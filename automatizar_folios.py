import openpyxl
from openpyxl.utils import get_column_letter

excel_path = r"c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_DIESEL_NUEVO.xlsx"

try:
    wb = openpyxl.load_workbook(excel_path)
    
    # 1. Configurar CATALOGOS
    sheet_cat = wb["CATALOGOS"]
    
    # Obra Codes (Col A is Obra, Col B will be Code)
    sheet_cat['B1'] = "CODIGO_OBRA"
    obras_dict = {
        "México-Toluca": "MT",
        "Mxico-Toluca": "MT",
        "Lerma - Tres Marías": "L3M",
        "Lerma - Tres Maras": "L3M",
        "No aplica": "NA",
        "Chamapa-Lechería": "CL",
        "Chamapa-Lechera": "CL",
        "Bacheo Toluca": "BT",
        "Planta Asfalto Pegaso": "PAP",
        "Planta Asflato Huixquilucan": "PAH",
        "Planta de Asfalto Huixquilucan": "PAH",
        "Dragones": "DRA",
        "Jalisco": "JAL",
        "Maquinaria Pegaso": "MP",
        "Providencia": "PRO"
    }
    
    for row in range(2, 50):
        obra = sheet_cat.cell(row=row, column=1).value
        if obra:
            sheet_cat.cell(row=row, column=2).value = obras_dict.get(str(obra).strip(), "XX")
            
    # Movimiento Codes (Col E is Movimiento, Col F will be Code)
    sheet_cat['E1'] = "TIPO_MOVIMIENTO"
    sheet_cat['F1'] = "CODIGO_MOV"
    movimientos = [
        ("CARGA TANQUE", "CT"),
        ("CARGA MARIMBA", "CM"),
        ("CARGA MAQUINARIA", "CMQ"),
        ("SOLICITUD", "SO"),
        ("FACTURA", "FA")
    ]
    for i, (mov, code) in enumerate(movimientos, start=2):
        sheet_cat.cell(row=i, column=5).value = mov
        sheet_cat.cell(row=i, column=6).value = code

    # 2. Configurar BD_DIESEL
    sheet_bd = wb["BD_DIESEL"]
    # Sort BD_DIESEL conceptually by Date? Openpyxl cannot natively sort ranges easily like Excel does.
    # The user asked to sort by date. It's safer to tell the user to click "Sort" in Excel, 
    # but we can apply the formulas down to row 1000.
    
    for row in range(2, 1000):
        # SEMANA (Col C) based on FECHA (Col B)
        # ISOWEEKNUM(B2)
        sheet_bd.cell(row=row, column=3).value = f'=IF(B{row}="","", "Semana "&ISOWEEKNUM(B{row}))'
        
        # FOLIO_CONCILIACION (Col A)
        # TIPO_MOVIMIENTO is E, OBRA_DESTINO is F
        sheet_bd.cell(row=row, column=1).value = f'=IF(B{row}="","", IFERROR(VLOOKUP(E{row},CATALOGOS!$E$2:$F$20,2,0),"XX") & "-" & IFERROR(VLOOKUP(F{row},CATALOGOS!$A$2:$B$20,2,0),"XX") & "-" & ISOWEEKNUM(B{row}) & "-" & TEXT(ROW()-1,"000"))'

    # 3. Configurar BD_FACTURAS
    sheet_fac = wb["BD_FACTURAS"]
    
    for row in range(2, 1000):
        # SEMANA (Col D) based on FECHA_FACTURA (Col C)
        sheet_fac.cell(row=row, column=4).value = f'=IF(C{row}="","", "Semana "&ISOWEEKNUM(C{row}))'
        
        # FOLIO_CONCILIACION (Col A)
        # Operation is ALWAYS "FA" for Facturas. PUNTO_DE_CARGA is F.
        sheet_fac.cell(row=row, column=1).value = f'=IF(C{row}="","", "FA" & "-" & IFERROR(VLOOKUP(F{row},CATALOGOS!$A$2:$B$50,2,0),"XX") & "-" & ISOWEEKNUM(C{row}) & "-" & TEXT(ROW()-1,"000"))'

    wb.save(excel_path)
    print("Formulas y catalogos actualizados correctamente.")

except Exception as e:
    print(f"Error: {e}")
