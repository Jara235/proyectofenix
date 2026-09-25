import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import pandas as pd
import datetime

# Create Workbook
wb = openpyxl.Workbook()

# Styles
def fill(hex_color): return PatternFill("solid", fgColor=hex_color)
def font(bold=False, italic=False, color='000000', size=10, name='Calibri'): return Font(bold=bold, italic=italic, color=color, size=size, name=name)
def align(h='center', v='center', wrap=False): return Alignment(horizontal=h, vertical=v, wrap_text=wrap)
def thin_border():
    s = Side(style='thin', color='CBD5E1')
    return Border(left=s, right=s, top=s, bottom=s)

WHITE = 'FFFFFF'
NAVY = '0F172A'
BLUE_HDR = '1E3A8A'
TEAL_HDR = '0F766E'
PURPLE_HDR = '581C87'
AMBER_HDR = 'B45309'
GRAY_BG = 'F8FAFC'
HIGHLIGHT_ROW = 'FEF3C7'

# ─────────────────────────────────────────────────────────────
# HOJA 1: PROYECCIÓN ENERO - JUNIO
# ─────────────────────────────────────────────────────────────
ws1 = wb.active
ws1.title = "Estimación Ene-Jun"
ws1.views.sheetView[0].showGridLines = True

# Title banner
ws1.merge_cells('A1:L1')
t1 = ws1['A1']
t1.value = "📊 PROYECCIÓN DE CONSUMO DE COMBUSTIBLE (ENERO - JUNIO)"
t1.fill = fill(NAVY); t1.font = font(bold=True, color=WHITE, size=14); t1.alignment = align('left', 'center')
ws1.row_dimensions[1].height = 28

ws1.merge_cells('A2:L2')
sub1 = ws1['A2']
sub1.value = "Estimación para las obras México-Toluca y Lerma-Tres Marías | Basado en comportamiento histórico real | Fénix 2.0"
sub1.fill = fill('1E293B'); sub1.font = font(italic=True, color='94A3B8', size=10); sub1.alignment = align('left', 'center')
ws1.row_dimensions[2].height = 20

# KPI Cards
kpis = [
    ("DIESEL ESTIMADO (6 MESES)", "112,835 L", "$3,046,548.80 MXN", '2563EB'),
    ("GASOLINA ESTIMADA (6 MESES)", "20,526 L", "$490,575.61 MXN", '059669'),
    ("PRESUPUESTO TOTAL COMBUSTIBLE", "133,361 L", "$3,537,124.43 MXN", 'D97706')
]

col_start = 1
for title_kpi, lts_kpi, imp_kpi, color_kpi in kpis:
    col_end = col_start + 3
    ws1.merge_cells(start_row=4, start_column=col_start, end_row=4, end_column=col_end)
    c = ws1.cell(row=4, column=col_start, value=title_kpi)
    c.fill = fill('F1F5F9'); c.font = font(bold=True, color='475569', size=9); c.alignment = align('center', 'center')
    
    ws1.merge_cells(start_row=5, start_column=col_start, end_row=5, end_column=col_end)
    c2 = ws1.cell(row=5, column=col_start, value=f"{lts_kpi}  |  {imp_kpi}")
    c2.fill = fill(color_kpi); c2.font = font(bold=True, color=WHITE, size=12); c2.alignment = align('center', 'center')
    
    for r in range(4, 6):
        for c_idx in range(col_start, col_end + 1):
            ws1.cell(row=r, column=c_idx).border = thin_border()
    col_start += 4

ws1.row_dimensions[4].height = 18
ws1.row_dimensions[5].height = 26

# Header Table Proyeccion
ws1.merge_cells('A7:A8'); ws1['A7'] = "MES"; ws1['A7'].fill = fill(NAVY); ws1['A7'].font = font(bold=True, color=WHITE, size=10); ws1['A7'].alignment = align('center', 'center')
ws1.merge_cells('B7:B8'); ws1['B7'] = "SEMANAS"; ws1['B7'].fill = fill(NAVY); ws1['B7'].font = font(bold=True, color=WHITE, size=10); ws1['B7'].alignment = align('center', 'center')

ws1.merge_cells('C7:E7'); ws1['C7'] = "OBRA: MÉXICO - TOLUCA"; ws1['C7'].fill = fill(BLUE_HDR); ws1['C7'].font = font(bold=True, color=WHITE, size=10); ws1['C7'].alignment = align('center', 'center')
ws1['C8'] = "Diesel (L)"; ws1['C8'].fill = fill('3B82F6'); ws1['C8'].font = font(bold=True, color=WHITE, size=9); ws1['C8'].alignment = align('center', 'center')
ws1['D8'] = "Gasolina (L)"; ws1['D8'].fill = fill('3B82F6'); ws1['D8'].font = font(bold=True, color=WHITE, size=9); ws1['D8'].alignment = align('center', 'center')
ws1['E8'] = "Importe ($)"; ws1['E8'].fill = fill('1D4ED8'); ws1['E8'].font = font(bold=True, color=WHITE, size=9); ws1['E8'].alignment = align('center', 'center')

ws1.merge_cells('F7:H7'); ws1['F7'] = "OBRA: LERMA - TRES MARÍAS"; ws1['F7'].fill = fill(TEAL_HDR); ws1['F7'].font = font(bold=True, color=WHITE, size=10); ws1['F7'].alignment = align('center', 'center')
ws1['F8'] = "Diesel (L)"; ws1['F8'].fill = fill('14B8A6'); ws1['F8'].font = font(bold=True, color=WHITE, size=9); ws1['F8'].alignment = align('center', 'center')
ws1['G8'] = "Gasolina (L)"; ws1['G8'].fill = fill('14B8A6'); ws1['G8'].font = font(bold=True, color=WHITE, size=9); ws1['G8'].alignment = align('center', 'center')
ws1['H8'] = "Importe ($)"; ws1['H8'].fill = fill('0F766E'); ws1['H8'].font = font(bold=True, color=WHITE, size=9); ws1['H8'].alignment = align('center', 'center')

ws1.merge_cells('I7:L7'); ws1['I7'] = "TOTAL CONSOLIDADO AMBAS OBRAS"; ws1['I7'].fill = fill(NAVY); ws1['I7'].font = font(bold=True, color=WHITE, size=10); ws1['I7'].alignment = align('center', 'center')
ws1['I8'] = "Total Diesel (L)"; ws1['I8'].fill = fill('334155'); ws1['I8'].font = font(bold=True, color=WHITE, size=9); ws1['I8'].alignment = align('center', 'center')
ws1['J8'] = "Importe Diesel ($)"; ws1['J8'].fill = fill('334155'); ws1['J8'].font = font(bold=True, color=WHITE, size=9); ws1['J8'].alignment = align('center', 'center')
ws1['K8'] = "Total Gasolina (L)"; ws1['K8'].fill = fill('334155'); ws1['K8'].font = font(bold=True, color=WHITE, size=9); ws1['K8'].alignment = align('center', 'center')
ws1['L8'] = "GRAN TOTAL ($)"; ws1['L8'].fill = fill('0F172A'); ws1['L8'].font = font(bold=True, color='FDE047', size=10); ws1['L8'].alignment = align('center', 'center')

for r in range(7, 9):
    for c in range(1, 13):
        ws1.cell(row=r, column=c).border = thin_border()
ws1.row_dimensions[7].height = 20
ws1.row_dimensions[8].height = 20

# Data rows for Proyeccion
datos_proj = [
    ("Enero", 4.43, 11121.0, 1739.3, 341837.55, 8204.3, 1776.2, 263968.29, 19325.4, 521784.60, 3515.5, 605805.84),
    ("Febrero", 4.00, 10044.8, 1571.0, 308756.50, 7410.4, 1604.3, 238422.97, 17455.2, 471289.32, 3175.3, 547179.47),
    ("Marzo", 4.43, 11121.0, 1739.3, 341837.55, 8204.3, 1776.2, 263968.29, 19325.4, 521784.60, 3515.5, 605805.84),
    ("Abril", 4.29, 10762.3, 1683.2, 330810.54, 7939.7, 1718.9, 255453.18, 18702.0, 504952.84, 3402.1, 586263.72),
    ("Mayo", 4.43, 11121.0, 1739.3, 341837.55, 8204.3, 1776.2, 263968.29, 19325.4, 521784.60, 3515.5, 605805.84),
    ("Junio", 4.29, 10762.3, 1683.2, 330810.54, 7939.7, 1718.9, 255453.18, 18702.0, 504952.84, 3402.1, 586263.72),
]

row_curr = 9
for idx, d in enumerate(datos_proj):
    bg = 'FFFFFF' if idx % 2 == 0 else GRAY_BG
    ws1.cell(row=row_curr, column=1, value=d[0]).font = font(bold=True, size=10)
    ws1.cell(row=row_curr, column=2, value=d[1]).font = font(size=10)
    
    ws1.cell(row=row_curr, column=3, value=d[2]).number_format = '#,##0.0'
    ws1.cell(row=row_curr, column=4, value=d[3]).number_format = '#,##0.0'
    ws1.cell(row=row_curr, column=5, value=d[4]).number_format = '"$"#,##0.00'
    
    ws1.cell(row=row_curr, column=6, value=d[5]).number_format = '#,##0.0'
    ws1.cell(row=row_curr, column=7, value=d[6]).number_format = '#,##0.0'
    ws1.cell(row=row_curr, column=8, value=d[7]).number_format = '"$"#,##0.00'
    
    ws1.cell(row=row_curr, column=9, value=d[8]).number_format = '#,##0.0'
    ws1.cell(row=row_curr, column=10, value=d[9]).number_format = '"$"#,##0.00'
    ws1.cell(row=row_curr, column=11, value=d[10]).number_format = '#,##0.0'
    
    c_gt = ws1.cell(row=row_curr, column=12, value=d[11])
    c_gt.number_format = '"$"#,##0.00'
    c_gt.font = font(bold=True, color='0F172A', size=10)
    c_gt.fill = fill('FEF08A')
    
    for c in range(1, 12):
        cell = ws1.cell(row=row_curr, column=c)
        cell.fill = fill(bg)
        cell.border = thin_border()
        if c in [1, 2]: cell.alignment = align('center', 'center')
        else: cell.alignment = align('right', 'center')
    c_gt.border = thin_border()
    c_gt.alignment = align('right', 'center')
    
    ws1.row_dimensions[row_curr].height = 20
    row_curr += 1

# Totals Row
ws1.cell(row=row_curr, column=1, value="TOTAL ESTIMADO (6 MESES)").fill = fill(NAVY)
ws1.cell(row=row_curr, column=1).font = font(bold=True, color=WHITE, size=10); ws1.cell(row=row_curr, column=1).alignment = align('left', 'center')
ws1.cell(row=row_curr, column=2, value="25.86 Sem").fill = fill(NAVY)
ws1.cell(row=row_curr, column=2).font = font(bold=True, color=WHITE, size=9); ws1.cell(row=row_curr, column=2).alignment = align('center', 'center')

ws1.cell(row=row_curr, column=3, value=112835.4 * 2511.20 / (2511.20 + 1852.59)).number_format = '#,##0.0' # MT Diesel
ws1.cell(row=row_curr, column=4, value=20526.0 * 392.75 / (392.75 + 401.08)).number_format = '#,##0.0' # MT Gas
ws1.cell(row=row_curr, column=5, value=1964348.69).number_format = '"$"#,##0.00' # MT Imp

ws1.cell(row=row_curr, column=6, value=112835.4 * 1852.59 / (2511.20 + 1852.59)).number_format = '#,##0.0' # LT Diesel
ws1.cell(row=row_curr, column=7, value=20526.0 * 401.08 / (392.75 + 401.08)).number_format = '#,##0.0' # LT Gas
ws1.cell(row=row_curr, column=8, value=1572775.74).number_format = '"$"#,##0.00' # LT Imp

ws1.cell(row=row_curr, column=9, value=112835.4).number_format = '#,##0.0'
ws1.cell(row=row_curr, column=10, value=3046548.80).number_format = '"$"#,##0.00'
ws1.cell(row=row_curr, column=11, value=20526.0).number_format = '#,##0.0'

c_tot_gt = ws1.cell(row=row_curr, column=12, value=3537124.43)
c_tot_gt.number_format = '"$"#,##0.00'
c_tot_gt.font = font(bold=True, color='000000', size=11)
c_tot_gt.fill = fill('FACC15')

for c in range(1, 12):
    cell = ws1.cell(row=row_curr, column=c)
    if c > 2:
        cell.fill = fill(NAVY)
        cell.font = font(bold=True, color=WHITE, size=9)
        cell.alignment = align('right', 'center')
    cell.border = thin_border()
c_tot_gt.border = thin_border(); c_tot_gt.alignment = align('right', 'center')
ws1.row_dimensions[row_curr].height = 24

# ─────────────────────────────────────────────────────────────
# HOJA 2: HISTÓRICO REAL MENSUAL Y SEMANAL
# ─────────────────────────────────────────────────────────────
ws2 = wb.create_sheet(title="Histórico Real")
ws2.views.sheetView[0].showGridLines = True

# Title
ws2.merge_cells('A1:I1')
ws2['A1'] = "📈 HISTÓRICO REAL REGISTRADO EN SISTEMA (JUNIO - AGOSTO)"
ws2['A1'].fill = fill(NAVY); ws2['A1'].font = font(bold=True, color=WHITE, size=13); ws2['A1'].alignment = align('left', 'center')
ws2.row_dimensions[1].height = 26

# Tabla 1: Real Mensual
ws2.merge_cells('A3:I3')
ws2['A3'] = "1. RESUMEN REAL MENSUAL POR OBRA Y COMBUSTIBLE"
ws2['A3'].fill = fill('1E3A8A'); ws2['A3'].font = font(bold=True, color=WHITE, size=10); ws2['A3'].alignment = align('left', 'center')
ws2.row_dimensions[3].height = 20

headers_hist_m = ["OBRA", "COMBUSTIBLE", "MES", "CARGAS / VALES", "LITROS REALES", "PRECIO PROM. ($/L)", "IMPORTE TOTAL ($)", "PROM. SEMANAL (L)", "ESTATUS"]
for c_i, h in enumerate(headers_hist_m, 1):
    c = ws2.cell(row=4, column=c_i, value=h)
    c.fill = fill('334155'); c.font = font(bold=True, color=WHITE, size=9); c.alignment = align('center', 'center'); c.border = thin_border()
ws2.row_dimensions[4].height = 20

hist_mensual_data = [
    ("MÉXICO-TOLUCA", "DIESEL", "2026-06 (Jun)", 94, 7176.0, 27.00, 193374.00, 2392.0, "Operación Normal"),
    ("MÉXICO-TOLUCA", "DIESEL", "2026-07 (Jul)", 99, 11691.0, 27.00, 258120.00, 2338.2, "Operación Plena"),
    ("MÉXICO-TOLUCA", "DIESEL", "2026-08 (Ago - Parcial)", 57, 6245.0, 27.00, 164646.00, 3122.5, "Alta Intensidad"),
    ("MÉXICO-TOLUCA", "GASOLINA", "2026-06 (Jun)", 9, 434.9, 23.34, 10121.20, 434.9, "Inicio Cuadrillas"),
    ("MÉXICO-TOLUCA", "GASOLINA", "2026-07 (Jul)", 32, 1882.6, 23.74, 45200.01, 376.5, "Operación Plena"),
    ("MÉXICO-TOLUCA", "GASOLINA", "2026-08 (Ago - Parcial)", 14, 824.5, 23.76, 19628.96, 412.3, "Operación Plena"),
    
    ("LERMA-TRES MARÍAS", "DIESEL", "2026-06 (Jun)", 53, 4416.0, 27.00, 119232.00, 1472.0, "Operación Normal"),
    ("LERMA-TRES MARÍAS", "DIESEL", "2026-07 (Jul)", 130, 11360.3, 27.00, 203830.18, 2272.1, "Pico Operativo Sem 29"),
    ("LERMA-TRES MARÍAS", "DIESEL", "2026-08 (Ago - Parcial)", 11, 897.0, 27.00, 22761.00, 897.0, "Baja Temporal"),
    ("LERMA-TRES MARÍAS", "GASOLINA", "2026-06 (Jun)", 8, 489.3, 23.65, 11585.72, 489.3, "Inicio Cuadrillas"),
    ("LERMA-TRES MARÍAS", "GASOLINA", "2026-07 (Jul)", 36, 1980.2, 23.54, 46497.27, 396.0, "Operación Plena"),
    ("LERMA-TRES MARÍAS", "GASOLINA", "2026-08 (Ago - Parcial)", 13, 739.1, 23.90, 17664.51, 369.5, "Operación Plena"),
]

r_hm = 5
for idx, d in enumerate(hist_mensual_data):
    bg = 'FFFFFF' if idx % 2 == 0 else GRAY_BG
    ws2.cell(row=r_hm, column=1, value=d[0]).font = font(bold=True, size=9)
    ws2.cell(row=r_hm, column=2, value=d[1]).font = font(bold=True, color='1E40AF' if d[1]=='DIESEL' else '047857', size=9)
    ws2.cell(row=r_hm, column=3, value=d[2])
    ws2.cell(row=r_hm, column=4, value=d[3]).number_format = '#,##0'
    ws2.cell(row=r_hm, column=5, value=d[4]).number_format = '#,##0.0'
    ws2.cell(row=r_hm, column=6, value=d[5]).number_format = '"$"#,##0.00'
    ws2.cell(row=r_hm, column=7, value=d[6]).number_format = '"$"#,##0.00'
    ws2.cell(row=r_hm, column=8, value=d[7]).number_format = '#,##0.0'
    ws2.cell(row=r_hm, column=9, value=d[8]).font = font(italic=True, size=8)
    
    for c in range(1, 10):
        cell = ws2.cell(row=r_hm, column=c)
        cell.fill = fill(bg)
        cell.border = thin_border()
        if c in [1, 2, 3, 9]: cell.alignment = align('center', 'center')
        else: cell.alignment = align('right', 'center')
    ws2.row_dimensions[r_hm].height = 18
    r_hm += 1

# ─────────────────────────────────────────────────────────────
# HOJA 3: DETALLE DE MAQUINARIA Y VEHÍCULOS
# ─────────────────────────────────────────────────────────────
ws3 = wb.create_sheet(title="Maquinaria y Vehículos")
ws3.views.sheetView[0].showGridLines = True

ws3.merge_cells('A1:G1')
ws3['A1'] = "🚜 EQUIPOS Y VEHÍCULOS ASIGNADOS A MÉXICO-TOLUCA Y LERMA-TRES MARÍAS"
ws3['A1'].fill = fill(NAVY); ws3['A1'].font = font(bold=True, color=WHITE, size=13); ws3['A1'].alignment = align('left', 'center')
ws3.row_dimensions[1].height = 26

# Headers
headers_eq = ["OBRA", "TIPO COMBUSTIBLE", "EQUIPO / VEHÍCULO", "RESPONSABLE / OPERADOR", "TOTAL CARGAS", "TOTAL LITROS", "IMPORTE ACUMULADO ($)"]
for c_i, h in enumerate(headers_eq, 1):
    c = ws3.cell(row=3, column=c_i, value=h)
    c.fill = fill('334155'); c.font = font(bold=True, color=WHITE, size=9); c.alignment = align('center', 'center'); c.border = thin_border()
ws3.row_dimensions[3].height = 20

equipos_top = [
    ("MÉXICO-TOLUCA", "DIESEL", "PERFILADORA DE ASFALTO", "Francisco Javier / Jesús Ortiz", 45, 9850.0, 265950.00),
    ("MÉXICO-TOLUCA", "DIESEL", "PAVIMENTADORA VÖGELE", "Francisco Javier", 28, 4320.0, 116640.00),
    ("MÉXICO-TOLUCA", "DIESEL", "COMPACTADORES / RODILLOS", "Cuadrilla Fresado y Asfalto", 52, 3890.0, 105030.00),
    ("MÉXICO-TOLUCA", "DIESEL", "RETROEXCAVADORAS Y BARREDORAS", "Operadores Maquinaria", 42, 2810.0, 75870.00),
    ("MÉXICO-TOLUCA", "DIESEL", "CAMIONES DE IMPACTO Y PIPAS", "Transportes / Operación", 35, 2142.0, 57834.00),
    ("MÉXICO-TOLUCA", "GASOLINA", "DODGE RAM 4000 (3/2)", "Cristian Reyes Gómora", 12, 1130.6, 27020.12),
    ("MÉXICO-TOLUCA", "GASOLINA", "MITSUBISHI L200", "Javier Pérez Díaz", 21, 1086.6, 25626.35),
    ("MÉXICO-TOLUCA", "GASOLINA", "RAM 1200", "Clemente Sanabria", 7, 415.5, 10234.37),
    ("MÉXICO-TOLUCA", "GASOLINA", "TOYOTA HIACE (URBAN)", "Alexis Samuel Rendón", 6, 284.5, 6800.03),
    ("MÉXICO-TOLUCA", "GASOLINA", "EQUIPOS MENORES / CORTADORAS", "Cuadrillas México-Toluca", 9, 224.8, 5269.30),
    
    ("LERMA-TRES MARÍAS", "DIESEL", "PERFILADORA RODATEC / WIRTGEN", "Apolinar Reyes", 38, 5920.0, 159840.00),
    ("LERMA-TRES MARÍAS", "DIESEL", "PAVIMENTADORA VÖGELE 1800-3", "Apolinar Reyes", 22, 3450.0, 93150.00),
    ("LERMA-TRES MARÍAS", "DIESEL", "COMPACTADORES Y RODILLOS HAMM", "Cuadrilla Asfalto", 46, 3210.0, 86670.00),
    ("LERMA-TRES MARÍAS", "DIESEL", "PETROLIZADORA INTERNATIONAL", "Operadores Lerma", 18, 1680.0, 45360.00),
    ("LERMA-TRES MARÍAS", "DIESEL", "RETROEXCAVADORAS Y COMPRESORES", "Apolinar Reyes", 30, 1515.3, 40913.18),
    ("LERMA-TRES MARÍAS", "GASOLINA", "DODGE RAM 4000 (3/2)", "Carmelo Álvarez Aniceto", 13, 1107.3, 26199.97),
    ("LERMA-TRES MARÍAS", "GASOLINA", "MITSUBISHI L200 (NYZ-971-C)", "Apolinar Reyes Bolaina", 14, 724.4, 17036.51),
    ("LERMA-TRES MARÍAS", "GASOLINA", "TOYOTA HIACE (URBAN PBT1229)", "Diego Fernández Santiago", 15, 683.1, 16190.17),
    ("LERMA-TRES MARÍAS", "GASOLINA", "MITSUBISHI L200 (NYZ-790-C)", "Leoncio Martínez Pascacio", 11, 521.0, 12321.01),
    ("LERMA-TRES MARÍAS", "GASOLINA", "CORTADORAS DE CONCRETO Y MENOR", "Cuadrilla Lerma", 4, 172.9, 3999.84),
]

r_eq = 4
for idx, d in enumerate(equipos_top):
    bg = 'FFFFFF' if idx % 2 == 0 else GRAY_BG
    ws3.cell(row=r_eq, column=1, value=d[0]).font = font(bold=True, size=9)
    ws3.cell(row=r_eq, column=2, value=d[1]).font = font(bold=True, color='1E40AF' if d[1]=='DIESEL' else '047857', size=9)
    ws3.cell(row=r_eq, column=3, value=d[2]).font = font(bold=True, size=9)
    ws3.cell(row=r_eq, column=4, value=d[3])
    ws3.cell(row=r_eq, column=5, value=d[4]).number_format = '#,##0'
    ws3.cell(row=r_eq, column=6, value=d[5]).number_format = '#,##0.0'
    ws3.cell(row=r_eq, column=7, value=d[6]).number_format = '"$"#,##0.00'
    
    for c in range(1, 8):
        cell = ws3.cell(row=r_eq, column=c)
        cell.fill = fill(bg)
        cell.border = thin_border()
        if c in [1, 2]: cell.alignment = align('center', 'center')
        elif c in [3, 4]: cell.alignment = align('left', 'center')
        else: cell.alignment = align('right', 'center')
    ws3.row_dimensions[r_eq].height = 18
    r_eq += 1

# Adjust column widths automatically
for ws in [ws1, ws2, ws3]:
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            val_str = str(cell.value or '')
            if '\n' in val_str:
                val_str = max(val_str.split('\n'), key=len)
            max_len = max(max_len, len(val_str))
        ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

# Save workbook
filename = 'c:/Users/JOSE/Desktop/Proyecto fenix/Estimacion_Combustible_MexicoToluca_Lerma_Ene_Jun.xlsx'
wb.save(filename)
print("Workbook saved successfully as:", filename)
