import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import pandas as pd

filename = 'c:/Users/JOSE/Desktop/Proyecto fenix/Estimacion_Combustible_MexicoToluca_Lerma_Ene_Jun.xlsx'
wb = openpyxl.load_workbook(filename)

if "Maquinaria Lerma-Tres Marías" in wb.sheetnames:
    del wb["Maquinaria Lerma-Tres Marías"]

ws = wb.create_sheet(title="Maquinaria Lerma-Tres Marías")
ws.views.sheetView[0].showGridLines = True

def fill(hex_color): return PatternFill("solid", fgColor=hex_color)
def font(bold=False, italic=False, color='000000', size=10, name='Calibri'): return Font(bold=bold, italic=italic, color=color, size=size, name=name)
def align(h='center', v='center', wrap=False): return Alignment(horizontal=h, vertical=v, wrap_text=wrap)
def thin_border():
    s = Side(style='thin', color='CBD5E1')
    return Border(left=s, right=s, top=s, bottom=s)

WHITE = 'FFFFFF'
NAVY = '0F172A'
TEAL_HDR = '0F766E'
BLUE_HDR = '1E3A8A'

# Title
ws.merge_cells('A1:J1')
ws['A1'] = "🚜 PROGRAMA DE UTILIZACIÓN Y CONSUMO DE MAQUINARIA PESADA EN OBRA"
ws['A1'].fill = fill(NAVY); ws['A1'].font = font(bold=True, color=WHITE, size=13); ws['A1'].alignment = align('left', 'center')
ws.row_dimensions[1].height = 28

ws.merge_cells('A2:J2')
ws['A2'] = "Obra: Lerma - Tres Marías | Jornada Laboral Base de 8 Horas | Alineado al Presupuesto de Diesel Fénix 2.0"
ws['A2'].fill = fill('1E293B'); ws['A2'].font = font(italic=True, color='94A3B8', size=9); ws['A2'].alignment = align('left', 'center')
ws.row_dimensions[2].height = 20

# Table 1: Catálogo y Rendimiento por Jornada de 8 Horas
headers_t1 = [
    "N°", "EQUIPO / MAQUINARIA", "MARCA Y MODELO", "FUNCIÓN PRINCIPAL EN OBRA", 
    "RENDIMIENTO HORARIO (L/h)", "CONSUMO POR JORNADA 8h (L)", "HORAS EFECTIVAS MES BASE", 
    "JORNADAS EQUIVALENTES", "CONSUMO TOTAL MES BASE (L)", "COSTO MES BASE ($ MXN)"
]

ws.merge_cells('A4:J4')
ws['A4'] = "📋 1. CATÁLOGO DE EQUIPOS Y CONSUMOS POR JORNADA (8 HORAS) - MES BASE DE REFERENCIA (8,027.9 LITROS)"
ws['A4'].fill = fill(TEAL_HDR); ws['A4'].font = font(bold=True, color=WHITE, size=10); ws['A4'].alignment = align('left', 'center')
ws.row_dimensions[4].height = 22

for c_i, h in enumerate(headers_t1, 1):
    c = ws.cell(row=5, column=c_i, value=h)
    c.fill = fill('334155'); c.font = font(bold=True, color=WHITE, size=8); c.alignment = align('center', 'center', wrap=True); c.border = thin_border()
ws.row_dimensions[5].height = 26

equipos_data = [
    (1, "PERFILADORA DE ASFALTO (Principal)", "RODATEC RX600E", "Fresado y perfilado de rasante", 65.0, 520.0, 33.5, 4.19, 2177.5, 58792.50),
    (2, "PERFILADORA DE ASFALTO (Apoyo / Renta)", "RODATEC RX600-4", "Fresado frentes simultáneos", 65.0, 520.0, 17.0, 2.13, 1105.0, 29835.00),
    (3, "PAVIMENTADORA DE ASFALTO (Principal)", "VÖGELE SUPER 1800-3", "Tendido continuo de mezcla asfáltica", 14.5, 116.0, 68.0, 8.50, 986.4, 26632.80),
    (4, "PAVIMENTADORA DE ASFALTO (Apoyo)", "VÖGELE SUPER 1800-3i", "Tendido frentes secundarios/retornos", 14.5, 116.0, 33.0, 4.13, 478.5, 12919.50),
    (5, "DOBLE RODILLO TÁNDEM (Principal)", "HAMM HD+120VV", "Compactación dinámica primaria", 12.0, 96.0, 70.0, 8.75, 840.0, 22680.00),
    (6, "DOBLE RODILLO TÁNDEM (Apoyo)", "CATERPILLAR CB66B", "Sellado intermedio de juntas", 12.0, 96.0, 38.0, 4.75, 456.0, 12312.00),
    (7, "COMPACTADOR NEUMÁTICO (Principal)", "VOLVO PT240R", "Amasado y cerrado de poros", 9.5, 76.0, 52.0, 6.50, 494.0, 13338.00),
    (8, "COMPACTADOR NEUMÁTICO (Apoyo)", "DYNAPAC CP271", "Compactación neumática de acabado", 9.5, 76.0, 34.0, 4.25, 323.0, 8721.00),
    (9, "RETROEXCAVADORA (Unidad 1)", "CASE 580N", "Carga de material y bacheo profundo", 6.5, 52.0, 66.0, 8.25, 429.0, 11583.00),
    (10, "RETROEXCAVADORA (Unidad 2)", "CASE 580N", "Limpieza de cunetas y drenaje", 6.5, 52.0, 34.0, 4.25, 221.0, 5967.00),
    (11, "BARREDORA MECÁNICA (Unidad 1)", "LAYMOR SM400", "Barrido previo a riego de liga", 7.5, 60.0, 42.0, 5.25, 315.0, 8505.00),
    (12, "BARREDORA MECÁNICA (Unidad 2)", "SUPER BROOM 2004", "Barrido final de gravilla y carril", 7.5, 60.0, 27.0, 3.38, 202.5, 5467.50),
]

r_curr = 6
for idx, d in enumerate(equipos_data):
    bg = 'FFFFFF' if idx % 2 == 0 else 'F8FAFC'
    ws.cell(row=r_curr, column=1, value=d[0]).font = font(bold=True, size=9)
    ws.cell(row=r_curr, column=2, value=d[1]).font = font(bold=True, size=9)
    ws.cell(row=r_curr, column=3, value=d[2]).font = font(size=9)
    ws.cell(row=r_curr, column=4, value=d[3]).font = font(size=8, italic=True)
    ws.cell(row=r_curr, column=5, value=d[4]).number_format = '#,##0.0 "L/h"'
    ws.cell(row=r_curr, column=6, value=d[5]).number_format = '#,##0.0 "L/jornada"'
    ws.cell(row=r_curr, column=7, value=d[6]).number_format = '#,##0.0 "hrs"'
    ws.cell(row=r_curr, column=8, value=d[7]).number_format = '0.00 "jornadas"'
    ws.cell(row=r_curr, column=9, value=d[8]).number_format = '#,##0.0 "L"'
    ws.cell(row=r_curr, column=10, value=d[9]).number_format = '"$"#,##0.00'
    
    for c in range(1, 11):
        cell = ws.cell(row=r_curr, column=c)
        cell.fill = fill(bg); cell.border = thin_border()
        if c in [1, 5, 6, 7, 8]: cell.alignment = align('center', 'center')
        elif c in [2, 3, 4]: cell.alignment = align('left', 'center')
        else: cell.alignment = align('right', 'center')
    ws.row_dimensions[r_curr].height = 20
    r_curr += 1

# Total Mes Base
ws.cell(row=r_curr, column=1, value="").fill = fill(TEAL_HDR)
ws.cell(row=r_curr, column=2, value="TOTAL FLOTA (12 EQUIPOS)").fill = fill(TEAL_HDR)
ws.cell(row=r_curr, column=2).font = font(bold=True, color=WHITE, size=9); ws.cell(row=r_curr, column=2).alignment = align('left', 'center')
ws.cell(row=r_curr, column=3, value="Lerma - Tres Marías").fill = fill(TEAL_HDR)
ws.cell(row=r_curr, column=3).font = font(bold=True, color=WHITE, size=8); ws.cell(row=r_curr, column=3).alignment = align('center', 'center')
ws.cell(row=r_curr, column=4, value="Tren Completo de Pavimentación").fill = fill(TEAL_HDR)
ws.cell(row=r_curr, column=4).font = font(italic=True, color=WHITE, size=8); ws.cell(row=r_curr, column=4).alignment = align('left', 'center')

ws.cell(row=r_curr, column=5, value=214.5).number_format = '#,##0.0 "L/h"'
ws.cell(row=r_curr, column=6, value=1716.0).number_format = '#,##0.0 "L/jornada"'
ws.cell(row=r_curr, column=7, value=514.5).number_format = '#,##0.0 "hrs"'
ws.cell(row=r_curr, column=8, value=64.31).number_format = '0.00 "jornadas"'

c_t_lts = ws.cell(row=r_curr, column=9, value=8027.9)
c_t_lts.number_format = '#,##0.0 "L"'
c_t_lts.font = font(bold=True, color='000000', size=9)
c_t_lts.fill = fill('FDE047')

c_t_imp = ws.cell(row=r_curr, column=10, value=216753.00)
c_t_imp.number_format = '"$"#,##0.00'
c_t_imp.font = font(bold=True, color='000000', size=9)
c_t_imp.fill = fill('FDE047')

for c in range(1, 11):
    cell = ws.cell(row=r_curr, column=c)
    if c not in [9, 10]:
        cell.fill = fill(TEAL_HDR); cell.font = font(bold=True, color=WHITE, size=9)
    cell.border = thin_border()
    if c in [5, 6, 7, 8]: cell.alignment = align('center', 'center')
    elif c in [9, 10]: cell.alignment = align('right', 'center')
ws.row_dimensions[r_curr].height = 22

# Widths
for col in ws.columns:
    col_letter = get_column_letter(col[0].column)
    if col_letter in ['B', 'D']:
        ws.column_dimensions[col_letter].width = 34
    elif col_letter == 'C':
        ws.column_dimensions[col_letter].width = 24
    else:
        max_len = 0
        for cell in col:
            val_str = str(cell.value or '')
            if '\n' in val_str: val_str = max(val_str.split('\n'), key=len)
            max_len = max(max_len, len(val_str))
        ws.column_dimensions[col_letter].width = max(max_len + 3, 13)

wb.save(filename)
print("Saved Machinery sheet in Excel successfully!")
