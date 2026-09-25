import os
import datetime
import psycopg2
from psycopg2.extras import DictCursor
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

def create_excel_control():
    # 1. Extraer datos reales de la Base de Datos PostgreSQL (fenix_db)
    print("Conectando a PostgreSQL fenix_db...")
    conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
    cur = conn.cursor(cursor_factory=DictCursor)

    # Obras
    cur.execute("SELECT codigo, nombre, COALESCE(responsable_default, ingeniero_responsable, 'Sin Asignar') as responsable FROM catalogos.obras WHERE nombre IS NOT NULL ORDER BY nombre")
    obras_raw = cur.fetchall()
    obras_list = []
    seen_obras = set()
    for o in obras_raw:
        n = o['nombre'].strip().replace('\n', ' ')
        if n and n not in seen_obras:
            seen_obras.add(n)
            obras_list.append({'codigo': o['codigo'], 'nombre': n, 'responsable': o['responsable'] or 'Responsable Obra'})

    # Equipos
    cur.execute("SELECT numero_economico, descripcion, tipo_equipo FROM catalogos.equipos ORDER BY numero_economico")
    equipos_raw = cur.fetchall()
    equipos_list = []
    seen_eq = set()
    for e in equipos_raw:
        eco = str(e['numero_economico']).strip()
        if eco and eco.lower() != 'nan' and eco not in seen_eq:
            seen_eq.add(eco)
            desc = str(e['descripcion'] or '').strip()
            equipos_list.append({'economico': eco, 'descripcion': desc, 'tipo': e['tipo_equipo'] or 'DIESEL'})

    # Responsables
    cur.execute("SELECT DISTINCT nombre FROM catalogos.responsables WHERE nombre IS NOT NULL ORDER BY nombre")
    resp_raw = cur.fetchall()
    resp_list = [r['nombre'].strip() for r in resp_raw if r['nombre']]

    conn.close()
    print(f"Catálogos cargados: {len(obras_list)} obras, {len(equipos_list)} equipos, {len(resp_list)} responsables.")

    # 2. Crear Libro de Excel
    wb = openpyxl.Workbook()
    
    # Estilos de Color
    COLOR_NAVY = "1F4E79"       # Azul oscuro encabezados
    COLOR_BLUE_LIGHT = "D9E1F2" # Azul claro KPIs
    COLOR_ACCENT = "2F5597"     # Azul acento
    COLOR_ZEBRA = "F2F5F9"      # Filas alternas
    COLOR_GREEN = "E2EFDA"      # Disponible
    COLOR_YELLOW = "FFF2CC"     # Alerta
    COLOR_RED = "FCE4D6"        # Excedido

    font_title = Font(name="Calibri", size=16, bold=True, color="FFFFFF")
    font_subtitle = Font(name="Calibri", size=11, italic=True, color="D9E1F2")
    font_header = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    font_bold = Font(name="Calibri", size=11, bold=True)
    font_normal = Font(name="Calibri", size=11)
    
    fill_navy = PatternFill(start_color=COLOR_NAVY, end_color=COLOR_NAVY, fill_type="solid")
    fill_accent = PatternFill(start_color=COLOR_ACCENT, end_color=COLOR_ACCENT, fill_type="solid")
    fill_kpi = PatternFill(start_color=COLOR_BLUE_LIGHT, end_color=COLOR_BLUE_LIGHT, fill_type="solid")
    fill_zebra = PatternFill(start_color=COLOR_ZEBRA, end_color=COLOR_ZEBRA, fill_type="solid")
    
    align_center = Alignment(horizontal="center", vertical="center")
    align_left = Alignment(horizontal="left", vertical="center")
    align_right = Alignment(horizontal="right", vertical="center")
    
    thin_border_side = Side(border_style="thin", color="D9D9D9")
    border_grid = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
    border_kpi = Border(left=Side(style="medium", color=COLOR_NAVY), right=Side(style="medium", color=COLOR_NAVY),
                        top=Side(style="medium", color=COLOR_NAVY), bottom=Side(style="medium", color=COLOR_NAVY))

    # ==========================================
    # HOJA 3: CATALOGOS (Referencia estática)
    # ==========================================
    ws_cat = wb.active
    ws_cat.title = "Catalogos"
    ws_cat.views.sheetView[0].showGridLines = True

    ws_cat.cell(row=1, column=1, value="LISTA DE OBRAS").font = font_bold
    ws_cat.cell(row=1, column=2, value="RESPONSABLE DEFAULT").font = font_bold
    ws_cat.cell(row=1, column=4, value="LISTA DE EQUIPOS").font = font_bold
    ws_cat.cell(row=1, column=5, value="DESCRIPCIÓN").font = font_bold
    ws_cat.cell(row=1, column=7, value="RESPONSABLES").font = font_bold

    for i, o in enumerate(obras_list, start=2):
        ws_cat.cell(row=i, column=1, value=o['nombre'])
        ws_cat.cell(row=i, column=2, value=o['responsable'])

    for i, e in enumerate(equipos_list, start=2):
        ws_cat.cell(row=i, column=4, value=e['economico'])
        ws_cat.cell(row=i, column=5, value=e['descripcion'])

    for i, r in enumerate(resp_list, start=2):
        ws_cat.cell(row=i, column=7, value=r)

    max_obras_row = len(obras_list) + 1
    max_eq_row = len(equipos_list) + 1

    # ==========================================
    # HOJA 2: CAPTURA DE SOLICITUDES
    # ==========================================
    ws_cap = wb.create_sheet(title="Captura_Solicitudes")
    ws_cap.views.sheetView[0].showGridLines = True

    # Banner de Encabezado
    ws_cap.merge_cells("A1:J1")
    ws_cap.merge_cells("A2:J2")
    ws_cap["A1"] = "GRUPO TRUJANO — PROYECTO FÉNIX"
    ws_cap["A1"].font = font_title
    ws_cap["A1"].fill = fill_navy
    ws_cap["A1"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
    
    ws_cap["A2"] = "MÓDULO DE CAPTURA DIARIA DE SOLICITUDES DE DIÉSEL PARA OBRAS"
    ws_cap["A2"].font = font_subtitle
    ws_cap["A2"].fill = fill_navy
    ws_cap["A2"].alignment = Alignment(horizontal="left", vertical="center", indent=1)

    ws_cap.row_dimensions[1].height = 25
    ws_cap.row_dimensions[2].height = 18
    ws_cap.row_dimensions[4].height = 26

    # Encabezados de Tabla de Captura
    headers_cap = [
        "Folio Solicitud", "Fecha", "Obra / Frente Destino", "Responsable Obra",
        "Equipo / Económico", "Litros Solicitados", "Horas / Km Est.",
        "Uso / Actividad", "Estatus", "Observaciones"
    ]

    for col_num, h_text in enumerate(headers_cap, 1):
        cell = ws_cap.cell(row=4, column=col_num, value=h_text)
        cell.font = font_header
        cell.fill = fill_accent
        cell.alignment = align_center
        cell.border = border_grid

    # Muestras de Solicitudes iniciales
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    sample_requests = [
        ("SOL-2026-001", today_str, "México - Toluca", "Cristian Reyes", "EX-02", 450, 8, "Excavación de zanja tramo km 14", "Aprobado", "Carga requerida primera hora"),
        ("SOL-2026-002", today_str, "Lerma - Tres Marías", "Francisco Javier", "PR-01", 600, 10, "Fresado de carpeta asfáltica", "Aprobado", "Carga con Pipa Marimba"),
        ("SOL-2026-003", today_str, "Chamapa-Lechería", "Apolinar", "RT-01", 200, 6, "Limpieza de cunetas", "Aprobado", "Tanque directo"),
        ("SOL-2026-004", today_str, "Bacheo Toluca", "Samuel", "BR-01", 150, 7, "Barredora vialidad principal", "Aprobado", "Turno matutino"),
        ("SOL-2026-005", today_str, "Planta Huixquilucan", "Luis", "PAH", 800, 12, "Producción de mezcla asfáltica", "Aprobado", "Tanque Huixquilucan"),
        ("SOL-2026-006", today_str, "Dragones", "Edgar", "DR-01", 300, 8, "Compactación de subrasante", "Aprobado", "Obra Dragones"),
        ("SOL-2026-007", today_str, "Planta Pegaso", "Samuel", "PPE", 500, 10, "Suministro caldera y planta", "Aprobado", "Tanque Pegaso"),
        ("SOL-2026-008", today_str, "México - Toluca", "Cristian Reyes", "EX-03", 400, 8, "Movimiento de tierras", "Pendiente", "Solicitud para mañana"),
    ]

    for row_idx, data in enumerate(sample_requests, start=5):
        ws_cap.row_dimensions[row_idx].height = 20
        fill_row = fill_zebra if row_idx % 2 == 0 else PatternFill(fill_type=None)
        
        for col_idx, val in enumerate(data, start=1):
            cell = ws_cap.cell(row=row_idx, column=col_idx, value=val)
            cell.font = font_normal
            cell.border = border_grid
            if fill_row.fill_type: cell.fill = fill_row
            
            if col_idx in (1, 2, 9):
                cell.alignment = align_center
            elif col_idx in (6, 7):
                cell.alignment = align_right
                cell.number_format = '#,##0'
            else:
                cell.alignment = align_left

    # Extender filas vacías preparadas con formato hasta la fila 100
    for row_idx in range(5 + len(sample_requests), 101):
        ws_cap.row_dimensions[row_idx].height = 20
        fill_row = fill_zebra if row_idx % 2 == 0 else PatternFill(fill_type=None)
        
        # Fórmula VLOOKUP automática para Responsable según la Obra seleccionada
        # =IFERROR(VLOOKUP(C{row}, Catalogos!A:B, 2, FALSE), "")
        formula_resp = f'=IFERROR(VLOOKUP(C{row_idx}, Catalogos!$A$2:$B${max_obras_row}, 2, FALSE), "")'
        
        for col_idx in range(1, 11):
            cell = ws_cap.cell(row=row_idx, column=col_idx)
            cell.font = font_normal
            cell.border = border_grid
            if fill_row.fill_type: cell.fill = fill_row
            
            if col_idx == 1:
                cell.value = f'=IF(C{row_idx}<>"", "SOL-2026-" & TEXT({row_idx}-4, "000"), "")'
                cell.alignment = align_center
            elif col_idx == 2:
                cell.value = today_str
                cell.alignment = align_center
            elif col_idx == 4:
                cell.value = formula_resp
                cell.alignment = align_left
            elif col_idx in (6, 7):
                cell.alignment = align_right
                cell.number_format = '#,##0'
            elif col_idx == 9:
                cell.value = "Pendiente"
                cell.alignment = align_center

    # Validación de Datos (Listas desplegables para Obras y Equipos)
    dv_obras = DataValidation(type="list", formula1=f"=Catalogos!$A$2:$A${max_obras_row}", allow_blank=True)
    ws_cap.add_data_validation(dv_obras)
    dv_obras.add(f"C5:C100")

    dv_equipos = DataValidation(type="list", formula1=f"=Catalogos!$D$2:$D${max_eq_row}", allow_blank=True)
    ws_cap.add_data_validation(dv_equipos)
    dv_equipos.add(f"E5:E100")

    dv_estatus = DataValidation(type="list", formula1='"Pendiente,Aprobado,Rechazado,Despachado"', allow_blank=True)
    ws_cap.add_data_validation(dv_estatus)
    dv_estatus.add(f"I5:I100")

    # ==========================================
    # HOJA 1: RESUMEN Y SALDOS AUTORIZADOS (Dashboard Principal)
    # ==========================================
    ws_res = wb.create_sheet(title="Resumen_Saldos_Semanales", index=0)
    ws_res.views.sheetView[0].showGridLines = True

    # Banner
    ws_res.merge_cells("A1:G1")
    ws_res.merge_cells("A2:G2")
    ws_res["A1"] = "GRUPO TRUJANO — CONTROL DE SALDOS Y SOLICITUDES DE DIÉSEL"
    ws_res["A1"].font = font_title
    ws_res["A1"].fill = fill_navy
    ws_res["A1"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
    
    ws_res["A2"] = "SEGUIMIENTO EN TIEMPO REAL: LÍMITE SEMANAL AUTORIZADO VS. CONSUMO / SOLICITADO"
    ws_res["A2"].font = font_subtitle
    ws_res["A2"].fill = fill_navy
    ws_res["A2"].alignment = Alignment(horizontal="left", vertical="center", indent=1)

    ws_res.row_dimensions[1].height = 25
    ws_res.row_dimensions[2].height = 18

    # Tarjetas de KPI Resumen Ejecutivos (Filas 4 y 5)
    kpis = [
        ("B4:B5", "B4", "B5", "AUTORIZADO TOTAL", "=SUM(C9:C30)", '#,##0 "Lts"'),
        ("C4:C5", "C4", "C5", "TOTAL SOLICITADO", "=SUM(D9:D30)", '#,##0 "Lts"'),
        ("D4:D5", "D4", "D5", "SALDO DISPONIBLE", "=SUM(E9:E30)", '#,##0 "Lts"'),
        ("E4:F4", "E4", "E5", "% EJECUTADO GLOBAL", "=IF(B5>0, C5/B5, 0)", '0.0%'),
    ]

    for merge_range, cell_lbl, cell_val, label_text, formula_val, num_fmt in kpis:
        ws_res[cell_lbl] = label_text
        ws_res[cell_lbl].font = Font(name="Calibri", size=9, bold=True, color="595959")
        ws_res[cell_lbl].alignment = align_center
        ws_res[cell_lbl].fill = fill_kpi

        ws_res[cell_val] = formula_val
        ws_res[cell_val].font = Font(name="Calibri", size=14, bold=True, color=COLOR_NAVY)
        ws_res[cell_val].alignment = align_center
        ws_res[cell_val].fill = fill_kpi
        ws_res[cell_val].number_format = num_fmt

        ws_res[cell_lbl].border = border_kpi
        ws_res[cell_val].border = border_kpi

    ws_res.row_dimensions[4].height = 18
    ws_res.row_dimensions[5].height = 26

    # Encabezados de Tabla de Saldos
    headers_res = [
        "Obra / Frente de Trabajo", "Responsable de Obra", "Límite Autorizado (Lts)",
        "Litros Solicitados (Lts)", "Saldo Disponible (Lts)", "% Utilizado", "Estatus / Alerta"
    ]

    ws_res.row_dimensions[8].height = 26
    for col_num, h_text in enumerate(headers_res, 1):
        cell = ws_res.cell(row=8, column=col_num, value=h_text)
        cell.font = font_header
        cell.fill = fill_navy
        cell.alignment = align_center
        cell.border = border_grid

    # Obras principales con su tope presupuestal autorizado inicial
    obras_presupuesto = [
        ("México - Toluca", "Cristian Reyes", 5000),
        ("Lerma - Tres Marías", "Francisco Javier", 3500),
        ("Chamapa-Lechería", "Apolinar", 2500),
        ("Bacheo Toluca", "Samuel", 2000),
        ("Planta Huixquilucan", "Luis", 4000),
        ("Dragones", "Edgar", 1500),
        ("Planta Pegaso", "Samuel", 3000),
        ("Jalisco", "Ingeniero Jalisco", 2500),
        ("Desasolve", "Diego Carreola", 1200),
        ("Lerma - Tenango", "Dayanne", 2000),
    ]

    for idx, (obra, resp, limite) in enumerate(obras_presupuesto, start=9):
        ws_res.row_dimensions[idx].height = 22
        fill_row = fill_zebra if idx % 2 == 0 else PatternFill(fill_type=None)

        # Fórmulas de Excel locales (sin hipervínculos externos):
        # Litros solicitados = SUMIFS(Captura_Solicitudes!F:F, Captura_Solicitudes!C:C, A{idx})
        formula_sol = f'=SUMIFS(Captura_Solicitudes!F:F, Captura_Solicitudes!C:C, A{idx})'
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
            if col_i == 7: c.font = font_bold

    # Fila de Totales
    total_row = 9 + len(obras_presupuesto)
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

    # Ajuste automático de ancho de columnas
    for ws in [ws_res, ws_cap, ws_cat]:
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val_str = str(cell.value or '')
                if cell.row in (1, 2): continue # ignora banners fusionados
                if val_str.startswith('='):
                    max_len = max(max_len, 12)
                else:
                    max_len = max(max_len, len(val_str))
            ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

    ws_res.column_dimensions['A'].width = 30
    ws_res.column_dimensions['B'].width = 24
    ws_res.column_dimensions['C'].width = 24
    ws_res.column_dimensions['D'].width = 24
    ws_res.column_dimensions['E'].width = 24
    ws_res.column_dimensions['F'].width = 16
    ws_res.column_dimensions['G'].width = 20

    ws_cap.column_dimensions['A'].width = 18
    ws_cap.column_dimensions['B'].width = 14
    ws_cap.column_dimensions['C'].width = 28
    ws_cap.column_dimensions['D'].width = 22
    ws_cap.column_dimensions['E'].width = 18
    ws_cap.column_dimensions['F'].width = 18
    ws_cap.column_dimensions['G'].width = 16
    ws_cap.column_dimensions['H'].width = 32
    ws_cap.column_dimensions['I'].width = 14
    ws_cap.column_dimensions['J'].width = 30

    output_path = r"c:\Users\JOSE\Desktop\Proyecto fenix\Control_Solicitudes_Saldo_Diesel.xlsx"
    wb.save(output_path)
    print(f"[OK] Excel generado exitosamente en: {output_path}")

if __name__ == "__main__":
    create_excel_control()
