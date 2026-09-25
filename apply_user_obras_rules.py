import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def apply_obras_updates():
    excel_path = r"c:\Users\JOSE\Desktop\Proyecto fenix\Control_Solicitudes_Saldo_Diesel.xlsx"
    print(f"Cargando libro: {excel_path}")
    wb = openpyxl.load_workbook(excel_path)

    # 1. ACTUALIZAR 'Captura_Solicitudes' (Reemplazar 'Dragones' por 'Bacheo Toluca')
    ws_cap = wb['Captura_Solicitudes']
    reemplazos_count = 0
    for row in range(5, 101):
        cell_obra = ws_cap.cell(row=row, column=3)
        if cell_obra.value and str(cell_obra.value).strip().lower() == "dragones":
            cell_obra.value = "Bacheo Toluca"
            reemplazos_count += 1
    
    print(f"[OK] Se reemplazaron {reemplazos_count} registros de 'Dragones' por 'Bacheo Toluca' en Captura_Solicitudes.")

    # 2. DEFINIR LISTA DEFINITIVA DE OBRAS ACTIVAS Y SUS RESPONSABLES
    active_obras = [
        ("México - Toluca", "Francisco Javier", 5000),
        ("Lerma - Tres Marías", "Apolinar", 3500),
        ("Chamapa - Lechería", "Sin responsable", 2500),
        ("Bacheo Toluca", "Diego Carreola", 2000),
        ("Planta Huixquilucan", "Luis", 4000),
        ("Planta Pegaso", "Jack", 3000),
        ("Desasolve", "Diego Carreola", 1200),
        ("Providencia", "Samuel", 1500),
        ("Alfredo del Mazo", "Variable", 2500),
        ("Colegio Militar", "Apolinar", 1500),
        ("Explanada Damián Carmona", "Sin responsable", 1500),
        ("Calle Revolución y Calle Lerdo", "Sin responsable", 1000),
        ("Constitución", "Sin responsable", 2000)
    ]

    # 3. ACTUALIZAR HOJA 'Catalogos'
    ws_cat = wb['Catalogos']
    
    # Limpiar filas previas
    for r in range(1, 100):
        for c in range(1, 10):
            ws_cat.cell(row=r, column=c).value = None

    font_bold = Font(name="Calibri", size=11, bold=True)
    font_normal = Font(name="Calibri", size=11)

    ws_cat.cell(row=1, column=1, value="LISTA DE OBRAS").font = font_bold
    ws_cat.cell(row=1, column=2, value="RESPONSABLE DEFAULT").font = font_bold

    for i, (obra, resp, _p) in enumerate(active_obras, start=2):
        ws_cat.cell(row=i, column=1, value=obra).font = font_normal
        ws_cat.cell(row=i, column=2, value=resp).font = font_normal

    max_obras_row = len(active_obras) + 1

    # 4. ACTUALIZAR 'Resumen_Saldos_Semanales'
    ws_res = wb['Resumen_Saldos_Semanales']

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

    # Limpiar filas 9 a 35 en Resumen
    for r in range(9, 35):
        for c in range(1, 8):
            ws_res.cell(row=r, column=c).value = None
            ws_res.cell(row=r, column=c).fill = PatternFill(fill_type=None)

    for idx, (obra, resp, limite) in enumerate(active_obras, start=9):
        ws_res.row_dimensions[idx].height = 22
        fill_row = fill_zebra if idx % 2 == 0 else PatternFill(fill_type=None)

        # Fórmula SUMIFS hacia Captura_Solicitudes (Litros Solicitados en Columna E, Obra en Columna C)
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
    total_row = 9 + len(active_obras)
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

    # Anchos de columna
    ws_res.column_dimensions['A'].width = 32
    ws_res.column_dimensions['B'].width = 24
    ws_res.column_dimensions['C'].width = 24
    ws_res.column_dimensions['D'].width = 24
    ws_res.column_dimensions['E'].width = 24
    ws_res.column_dimensions['F'].width = 16
    ws_res.column_dimensions['G'].width = 20

    ws_cat.column_dimensions['A'].width = 32
    ws_cat.column_dimensions['B'].width = 24

    wb.save(excel_path)
    print(f"[OK] Archivo actualizado exitosamente con la lista definitiva de 13 obras y responsables.")

if __name__ == "__main__":
    apply_obras_updates()
