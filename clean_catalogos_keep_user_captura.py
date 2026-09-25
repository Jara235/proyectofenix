import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def clean_excel_catalogos():
    excel_path = r"c:\Users\JOSE\Desktop\Proyecto fenix\Control_Solicitudes_Saldo_Diesel.xlsx"
    print(f"Cargando archivo: {excel_path}")
    wb = openpyxl.load_workbook(excel_path)
    
    # 1. VERIFICAR HOJAS Y PRESERVAR 'Captura_Solicitudes' INTACTA
    print("Hojas existentes:", wb.sheetnames)
    assert "Captura_Solicitudes" in wb.sheetnames, "Falta la hoja Captura_Solicitudes"
    print("[OK] Hoja 'Captura_Solicitudes' preservada exactamente con las modificaciones realizadas por el usuario.")

    # 2. LIMPIAR Y REESTRUCTURAR LA HOJA 'Catalogos'
    ws_cat = wb['Catalogos']
    
    # Limpiar contenido anterior
    for row in ws_cat.iter_rows(min_row=1, max_row=100, min_col=1, max_col=10):
        for cell in row:
            cell.value = None

    font_bold = Font(name="Calibri", size=11, bold=True)
    font_normal = Font(name="Calibri", size=11)
    
    # Lista limpia de Obras sin duplicados y con Responsables asignados
    clean_obras = [
        ("México - Toluca", "Cristian Reyes"),
        ("Lerma - Tres Marías", "Francisco Javier"),
        ("Chamapa-Lechería", "Apolinar"),
        ("Bacheo Toluca", "Samuel"),
        ("Planta Huixquilucan", "Luis"),
        ("Planta Pegaso", "Samuel"),
        ("Dragones", "Edgar"),
        ("Desasolve", "Diego Carreola"),
        ("Lerma - Tenango", "Dayanne"),
        ("Providencia", "Jack"),
        ("Alfredo del Mazo", "Variable"),
        ("Jalisco", "Ingeniero Jalisco"),
        ("Tanque Pegaso", "Operador Tanque"),
        ("Colegio Militar", "Francisco Javier"),
        ("Explanada Damián Carmona", "Apolinar"),
        ("Calle Revolución y Calle Lerdo", "Luis"),
    ]

    ws_cat.cell(row=1, column=1, value="LISTA DE OBRAS").font = font_bold
    ws_cat.cell(row=1, column=2, value="RESPONSABLE DEFAULT").font = font_bold

    for i, (obra, resp) in enumerate(clean_obras, start=2):
        ws_cat.cell(row=i, column=1, value=obra).font = font_normal
        ws_cat.cell(row=i, column=2, value=resp).font = font_normal

    max_obras_row = len(clean_obras) + 1

    # 3. ACTUALIZAR 'Resumen_Saldos_Semanales' CON LAS OBRAS LIMPIAS Y RESPONSABLES REALES
    ws_res = wb['Resumen_Saldos_Semanales']

    # Estilos
    COLOR_NAVY = "1F4E79"
    COLOR_ZEBRA = "F2F5F9"
    
    font_header = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    fill_navy = PatternFill(start_color=COLOR_NAVY, end_color=COLOR_NAVY, fill_type="solid")
    fill_zebra = PatternFill(start_color=COLOR_ZEBRA, end_color=COLOR_ZEBRA, fill_type="solid")
    
    align_center = Alignment(horizontal="center", vertical="center")
    align_left = Alignment(horizontal="left", vertical="center")
    align_right = Alignment(horizontal="right", vertical="center")
    
    thin_border_side = Side(border_style="thin", color="D9D9D9")
    border_grid = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)

    # Limpiar tabla anterior en Resumen_Saldos_Semanales (desde fila 9 a 35)
    for r in range(9, 35):
        for c in range(1, 8):
            ws_res.cell(row=r, column=c).value = None
            ws_res.cell(row=r, column=c).fill = PatternFill(fill_type=None)

    # Re-poblar filas de obras en Resumen_Saldos_Semanales
    # Notar que 'Litros Solicitados' en la hoja modificada por el usuario ahora está en la Columna E (Columna 5)
    # y 'Obra' está en la Columna C (Columna 3)
    presupuestos = {
        "México - Toluca": 5000,
        "Lerma - Tres Marías": 3500,
        "Chamapa-Lechería": 2500,
        "Bacheo Toluca": 2000,
        "Planta Huixquilucan": 4000,
        "Planta Pegaso": 3000,
        "Dragones": 1500,
        "Desasolve": 1200,
        "Lerma - Tenango": 2000,
        "Providencia": 1500,
        "Alfredo del Mazo": 2500,
        "Jalisco": 2500,
        "Tanque Pegaso": 5000,
        "Colegio Militar": 1500,
        "Explanada Damián Carmona": 1500,
        "Calle Revolución y Calle Lerdo": 1000,
    }

    for idx, (obra, resp) in enumerate(clean_obras, start=9):
        ws_res.row_dimensions[idx].height = 22
        fill_row = fill_zebra if idx % 2 == 0 else PatternFill(fill_type=None)

        limite = presupuestos.get(obra, 2000)

        # La fórmula SUMIFS se ajusta a la nueva disposición del usuario en Captura_Solicitudes:
        # Columna E = Litros Solicitados
        # Columna C = Obra / Frente Destino
        formula_sol = f'=SUMIFS(Captura_Solicitudes!E:E, Captura_Solicitudes!C:C, A{idx})'
        formula_saldo = f'=C{idx}-D{idx}'
        formula_pct = f'=IF(C{idx}>0, D{idx}/C{idx}, 0)'
        formula_status = f'=IF(E{idx}<0, "⚠️ EXCEDIDO", IF(F{idx}>=0.8, "⚡ POR AGOTAR", "✅ DISPONIBLE"))'

        cells_data = [
            (1, obra, align_left, "@"),
            (2, resp, align_left, "@"),
            (3, limite, align_right, '#,##0 "Lts"'),
            (4, formula_sol, align_right, '#,##0 "Lts"'),
            (5, formula_saldo, align_right, '#,##0 "Lts"'),
            (6, formula_pct, align_right, '0.0%'),
            (7, formula_status, align_center, "@")
        ]

        for col_i, val, align_style, num_format in cells_data:
            c = ws_res.cell(row=idx, column=col_i, value=val)
            c.font = font_normal
            c.alignment = align_style
            c.number_format = num_format
            c.border = border_grid
            if fill_row.fill_type: c.fill = fill_row
            if col_i == 7: c.font = Font(name="Calibri", size=11, bold=True)

    # Fila de Totales
    total_row = 9 + len(clean_obras)
    ws_res.row_dimensions[total_row].height = 24
    
    ws_res.cell(row=total_row, column=1, value="TOTAL GENERAL").font = font_bold
    ws_res.cell(row=total_row, column=1).alignment = align_left
    ws_res.cell(row=total_row, column=1).border = border_grid

    ws_res.cell(row=total_row, column=2, value="").border = border_grid

    for col_i, formula_t, fmt_t in [
        (3, f'=SUM(C9:C{total_row-1})', '#,##0 "Lts"'),
        (4, f'=SUM(D9:D{total_row-1})', '#,##0 "Lts"'),
        (5, f'=SUM(E9:E{total_row-1})', '#,##0 "Lts"'),
        (6, f'=IF(C{total_row}>0, D{total_row}/C{total_row}, 0)', '0.0%'),
    ]:
        c = ws_res.cell(row=total_row, column=col_i, value=formula_t)
        c.font = font_bold
        c.alignment = align_right
        c.number_format = fmt_t
        c.border = border_grid
        c.fill = PatternFill(start_color="E9EEF4", end_color="E9EEF4", fill_type="solid")

    ws_res.cell(row=total_row, column=7, value="").border = border_grid
    ws_res.cell(row=total_row, column=7).fill = PatternFill(start_color="E9EEF4", end_color="E9EEF4", fill_type="solid")

    # Ajustar fórmulas de KPIs superiores
    ws_res["B5"].value = f'=SUM(C9:C{total_row-1})'
    ws_res["C5"].value = f'=SUM(D9:D{total_row-1})'
    ws_res["D5"].value = f'=SUM(E9:E{total_row-1})'

    # Ajustar anchos de columnas
    for ws in [ws_res, ws_cat]:
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val_str = str(cell.value or '')
                if cell.row in (1, 2): continue
                if val_str.startswith('='):
                    max_len = max(max_len, 12)
                else:
                    max_len = max(max_len, len(val_str))
            ws.column_dimensions[col_letter].width = max(max_len + 4, 15)

    ws_res.column_dimensions['A'].width = 32
    ws_res.column_dimensions['B'].width = 24
    ws_res.column_dimensions['C'].width = 24
    ws_res.column_dimensions['D'].width = 24
    ws_res.column_dimensions['E'].width = 24
    ws_res.column_dimensions['F'].width = 16
    ws_res.column_dimensions['G'].width = 20

    wb.save(excel_path)
    print(f"[OK] Tabla de catálogos y resumen limpios. Modificaciones del usuario en 'Captura_Solicitudes' totalmente preservadas.")

if __name__ == "__main__":
    clean_excel_catalogos()
