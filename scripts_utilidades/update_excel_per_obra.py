import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

filename = 'c:/Users/JOSE/Desktop/Proyecto fenix/Estimacion_Combustible_MexicoToluca_Lerma_Ene_Jun.xlsx'
wb = openpyxl.load_workbook(filename)

# Replace sheet
if "Comparativo por Obra" in wb.sheetnames:
    del wb["Comparativo por Obra"]
if "Comparativo vs Referencia" in wb.sheetnames:
    del wb["Comparativo vs Referencia"]

ws_comp = wb.create_sheet(title="Comparativo por Obra", index=0)
ws_comp.views.sheetView[0].showGridLines = True

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
RED_TEXT = '991B1B'
GREEN_TEXT = '166534'

# Title
ws_comp.merge_cells('A1:J1')
ws_comp['A1'] = "📊 COMPARATIVO MENSUAL POR OBRA: ESTIMACIÓN DINÁMICA VS VALOR REAL DE REFERENCIA"
ws_comp['A1'].fill = fill(NAVY); ws_comp['A1'].font = font(bold=True, color=WHITE, size=13); ws_comp['A1'].alignment = align('left', 'center')
ws_comp.row_dimensions[1].height = 28

ws_comp.merge_cells('A2:J2')
ws_comp['A2'] = "Desglose individual por obra para México - Toluca y Lerma - Tres Marías | Evaluación de Variaciones y Causas Operativas | Fénix 2.0"
ws_comp['A2'].fill = fill('1E293B'); ws_comp['A2'].font = font(italic=True, color='94A3B8', size=9); ws_comp['A2'].alignment = align('left', 'center')
ws_comp.row_dimensions[2].height = 20

headers = [
    "MES", 
    "DIESEL EST. (L)", 
    "GASOLINA EST. (L)", 
    "TOTAL VOL. (L)", 
    "PRESUPUESTO ESTIMADO ($)", 
    "VALOR REFERENCIA ($)", 
    "DIFERENCIA ($)", 
    "VARIACIÓN (%)", 
    "¿SUPERA REF.?", 
    "JUSTIFICACIÓN TÉCNICA Y OPERATIVA DE CAMPO"
]

# ─────────────────────────────────────────────────────────────
# SECCIÓN 1: MÉXICO - TOLUCA
# ─────────────────────────────────────────────────────────────
ws_comp.merge_cells('A4:J4')
ws_comp['A4'] = "📍 OBRA: MÉXICO - TOLUCA (VALOR DE REFERENCIA MENSUAL: $334,486.40 MXN | 12,583.8 LITROS)"
ws_comp['A4'].fill = fill(BLUE_HDR); ws_comp['A4'].font = font(bold=True, color=WHITE, size=10); ws_comp['A4'].alignment = align('left', 'center')
ws_comp.row_dimensions[4].height = 22

for c_i, h in enumerate(headers, 1):
    c = ws_comp.cell(row=5, column=c_i, value=h)
    c.fill = fill('334155'); c.font = font(bold=True, color=WHITE, size=9); c.alignment = align('center', 'center'); c.border = thin_border()
ws_comp.row_dimensions[5].height = 22

data_mt = [
    ("Enero", 7932.9, 1395.6, 9328.5, 247543.14, 334486.40, -86943.26, -25.99, "NO", "Heladas matutinas en el tramo de montaña y La Marquesa retrasan el arranque de fresado y tendido hasta las 10:30 hrs. Arranque escalonado post-vacaciones."),
    ("Febrero", 9597.8, 1457.8, 11055.6, 293982.02, 334486.40, -40504.38, -12.11, "NO", "Operación en ascenso con buen clima seco, pero mes corto de 28 días (20 días hábiles) reduce el volumen acumulado mensual."),
    ("Marzo", 12633.9, 1979.0, 14612.9, 388413.40, 334486.40, 53927.00, 16.12, "SÍ", "Estiaje pleno en autopista México-Toluca: frentes continuos de fresado nocturno y tiros largos de mezcla asfáltica sin lluvia."),
    ("Abril", 10424.9, 1624.5, 12049.4, 320297.85, 334486.40, -14188.55, -4.24, "NO", "Buen avance físico pero ajustado por el paro de Semana Santa y cambio programado de picas en la perfiladora de asfalto."),
    ("Mayo", 14396.8, 2169.8, 16566.6, 440571.82, 334486.40, 106085.42, 31.72, "SÍ", "MES PICO: Cierre acelerado de tramos de autopista antes de lluvias. Pavimentadora Vögele y compactadores en dobles turnos continuos."),
    ("Junio", 7073.2, 1346.2, 8419.4, 223150.58, 334486.40, -111335.82, -33.29, "NO", "Inicio de lluvias y tormentas fuertes en zona alta (La Marquesa/Salazar), impidiendo el riego de liga y tendido; traslados a taller.")
]

r_mt = 6
for idx, d in enumerate(data_mt):
    supera = d[8] == "SÍ"
    bg = 'FEF2F2' if supera else 'F0FDF4'
    tag_bg = 'DC2626' if supera else '16A34A'
    
    ws_comp.cell(row=r_mt, column=1, value=d[0]).font = font(bold=True, size=9)
    ws_comp.cell(row=r_mt, column=2, value=d[1]).number_format = '#,##0.0'
    ws_comp.cell(row=r_mt, column=3, value=d[2]).number_format = '#,##0.0'
    ws_comp.cell(row=r_mt, column=4, value=d[3]).number_format = '#,##0.0'
    ws_comp.cell(row=r_mt, column=5, value=d[4]).number_format = '"$"#,##0.00'
    ws_comp.cell(row=r_mt, column=6, value=d[5]).number_format = '"$"#,##0.00'
    
    c_dif = ws_comp.cell(row=r_mt, column=7, value=d[6])
    c_dif.number_format = '"+"#,##0.00;"-"#,##0.00;"$0.00"'
    c_dif.font = font(bold=True, color=RED_TEXT if supera else GREEN_TEXT, size=9)
    
    c_pct = ws_comp.cell(row=r_mt, column=8, value=d[7]/100.0)
    c_pct.number_format = '+0.0%;-0.0%;0.0%'
    c_pct.font = font(bold=True, color=RED_TEXT if supera else GREEN_TEXT, size=9)
    
    c_sup = ws_comp.cell(row=r_mt, column=9, value=d[8])
    c_sup.fill = fill(tag_bg); c_sup.font = font(bold=True, color=WHITE, size=9); c_sup.alignment = align('center', 'center')
    
    c_jus = ws_comp.cell(row=r_mt, column=10, value=d[9])
    c_jus.font = font(size=8); c_jus.alignment = align('left', 'center', wrap=True)
    
    for c in range(1, 11):
        cell = ws_comp.cell(row=r_mt, column=c)
        if c != 9: cell.fill = fill(bg)
        cell.border = thin_border()
        if c == 1: cell.alignment = align('center', 'center')
        elif c in [2, 3, 4, 5, 6, 7, 8]: cell.alignment = align('right', 'center')
    ws_comp.row_dimensions[r_mt].height = 26
    r_mt += 1

# Total México - Toluca
ws_comp.cell(row=r_mt, column=1, value="TOTAL MÉXICO - TOLUCA").fill = fill(BLUE_HDR)
ws_comp.cell(row=r_mt, column=1).font = font(bold=True, color=WHITE, size=9); ws_comp.cell(row=r_mt, column=1).alignment = align('center', 'center')

ws_comp.cell(row=r_mt, column=2, value=62059.5).number_format = '#,##0.0'
ws_comp.cell(row=r_mt, column=3, value=9973.1).number_format = '#,##0.0'
ws_comp.cell(row=r_mt, column=4, value=72032.6).number_format = '#,##0.0'
ws_comp.cell(row=r_mt, column=5, value=1913958.81).number_format = '"$"#,##0.00'
ws_comp.cell(row=r_mt, column=6, value=334486.40 * 6).number_format = '"$"#,##0.00'

ws_comp.cell(row=r_mt, column=7, value=1913958.81 - (334486.40 * 6)).number_format = '"+"#,##0.00;"-"#,##0.00;"$0.00"'
ws_comp.cell(row=r_mt, column=8, value=(1913958.81 - (334486.40 * 6)) / (334486.40 * 6)).number_format = '+0.0%;-0.0%;0.0%'
ws_comp.cell(row=r_mt, column=9, value="2 de 6").fill = fill(BLUE_HDR)
ws_comp.cell(row=r_mt, column=9).font = font(bold=True, color=WHITE, size=8); ws_comp.cell(row=r_mt, column=9).alignment = align('center', 'center')

ws_comp.cell(row=r_mt, column=10, value="Presupuesto Semestral México-Toluca ajustado por variaciones estacionales.").fill = fill(BLUE_HDR)
ws_comp.cell(row=r_mt, column=10).font = font(italic=True, color='94A3B8', size=8); ws_comp.cell(row=r_mt, column=10).alignment = align('left', 'center')

for c in range(1, 11):
    cell = ws_comp.cell(row=r_mt, column=c)
    if c not in [1, 9, 10]:
        cell.fill = fill(BLUE_HDR); cell.font = font(bold=True, color=WHITE, size=9)
        cell.alignment = align('right', 'center')
    cell.border = thin_border()
ws_comp.row_dimensions[r_mt].height = 22
r_mt += 2

# ─────────────────────────────────────────────────────────────
# SECCIÓN 2: LERMA - TRES MARÍAS
# ─────────────────────────────────────────────────────────────
ws_comp.merge_cells(f'A{r_mt}:J{r_mt}')
ws_comp[f'A{r_mt}'] = "📍 OBRA: LERMA - TRES MARÍAS (VALOR DE REFERENCIA MENSUAL: $258,291.50 MXN | 9,765.9 LITROS)"
ws_comp[f'A{r_mt}'].fill = fill(TEAL_HDR); ws_comp[f'A{r_mt}'].font = font(bold=True, color=WHITE, size=10); ws_comp[f'A{r_mt}'].alignment = align('left', 'center')
ws_comp.row_dimensions[r_mt].height = 22
r_mt += 1

for c_i, h in enumerate(headers, 1):
    c = ws_comp.cell(row=r_mt, column=c_i, value=h)
    c.fill = fill('334155'); c.font = font(bold=True, color=WHITE, size=9); c.alignment = align('center', 'center'); c.border = thin_border()
ws_comp.row_dimensions[r_mt].height = 22
r_mt += 1

data_lt = [
    ("Enero", 5845.5, 1427.9, 7273.4, 191955.31, 258291.50, -66336.19, -25.68, "NO", "Temperaturas gélidas en la zona lacustre y sierra de Lerma; calibración y mantenimiento general de maquinaria pesada."),
    ("Febrero", 7080.6, 1491.7, 8572.3, 226827.83, 258291.50, -31463.67, -12.18, "NO", "Buen ritmo en tramos de terracería y base, pero limitado por los 28 días naturales del mes (20 días hábiles)."),
    ("Marzo", 9320.4, 2025.9, 11346.3, 300069.61, 258291.50, 41778.11, 16.18, "SÍ", "Condiciones óptimas de estiaje para carpeta asfáltica en carretera Lerma-Tres Marías, frentes activos de bacheo profundo y compactación."),
    ("Abril", 7690.7, 1663.0, 9353.7, 247394.60, 258291.50, -10896.90, -4.22, "NO", "Interrupción programada de frentes en Semana Santa, utilizada para mantenimiento de la petrolizadora y rodillos Hamm."),
    ("Mayo", 10620.9, 2221.2, 12842.1, 339850.98, 258291.50, 81559.48, 31.58, "SÍ", "MES PICO: Máxima intensidad para proteger terracerías y tender carpeta corrida antes del temporal en la sierra."),
    ("Junio", 5218.1, 1378.2, 6596.3, 173827.68, 258291.50, -84463.82, -32.70, "NO", "Temporal de lluvias en la sierra Lerma-Tres Marías frena colocación de emulsión y asfalto; cuadrillas se enfocan en desasolve/drenaje.")
]

for idx, d in enumerate(data_lt):
    supera = d[8] == "SÍ"
    bg = 'FEF2F2' if supera else 'F0FDF4'
    tag_bg = 'DC2626' if supera else '16A34A'
    
    ws_comp.cell(row=r_mt, column=1, value=d[0]).font = font(bold=True, size=9)
    ws_comp.cell(row=r_mt, column=2, value=d[1]).number_format = '#,##0.0'
    ws_comp.cell(row=r_mt, column=3, value=d[2]).number_format = '#,##0.0'
    ws_comp.cell(row=r_mt, column=4, value=d[3]).number_format = '#,##0.0'
    ws_comp.cell(row=r_mt, column=5, value=d[4]).number_format = '"$"#,##0.00'
    ws_comp.cell(row=r_mt, column=6, value=d[5]).number_format = '"$"#,##0.00'
    
    c_dif = ws_comp.cell(row=r_mt, column=7, value=d[6])
    c_dif.number_format = '"+"#,##0.00;"-"#,##0.00;"$0.00"'
    c_dif.font = font(bold=True, color=RED_TEXT if supera else GREEN_TEXT, size=9)
    
    c_pct = ws_comp.cell(row=r_mt, column=8, value=d[7]/100.0)
    c_pct.number_format = '+0.0%;-0.0%;0.0%'
    c_pct.font = font(bold=True, color=RED_TEXT if supera else GREEN_TEXT, size=9)
    
    c_sup = ws_comp.cell(row=r_mt, column=9, value=d[8])
    c_sup.fill = fill(tag_bg); c_sup.font = font(bold=True, color=WHITE, size=9); c_sup.alignment = align('center', 'center')
    
    c_jus = ws_comp.cell(row=r_mt, column=10, value=d[9])
    c_jus.font = font(size=8); c_jus.alignment = align('left', 'center', wrap=True)
    
    for c in range(1, 11):
        cell = ws_comp.cell(row=r_mt, column=c)
        if c != 9: cell.fill = fill(bg)
        cell.border = thin_border()
        if c == 1: cell.alignment = align('center', 'center')
        elif c in [2, 3, 4, 5, 6, 7, 8]: cell.alignment = align('right', 'center')
    ws_comp.row_dimensions[r_mt].height = 26
    r_mt += 1

# Total Lerma - Tres Marías
ws_comp.cell(row=r_mt, column=1, value="TOTAL LERMA - TRES MARÍAS").fill = fill(TEAL_HDR)
ws_comp.cell(row=r_mt, column=1).font = font(bold=True, color=WHITE, size=9); ws_comp.cell(row=r_mt, column=1).alignment = align('center', 'center')

ws_comp.cell(row=r_mt, column=2, value=45772.9).number_format = '#,##0.0'
ws_comp.cell(row=r_mt, column=3, value=10207.9).number_format = '#,##0.0'
ws_comp.cell(row=r_mt, column=4, value=55980.8).number_format = '#,##0.0'
ws_comp.cell(row=r_mt, column=5, value=1479920.01).number_format = '"$"#,##0.00'
ws_comp.cell(row=r_mt, column=6, value=258291.50 * 6).number_format = '"$"#,##0.00'

ws_comp.cell(row=r_mt, column=7, value=1479920.01 - (258291.50 * 6)).number_format = '"+"#,##0.00;"-"#,##0.00;"$0.00"'
ws_comp.cell(row=r_mt, column=8, value=(1479920.01 - (258291.50 * 6)) / (258291.50 * 6)).number_format = '+0.0%;-0.0%;0.0%'
ws_comp.cell(row=r_mt, column=9, value="2 de 6").fill = fill(TEAL_HDR)
ws_comp.cell(row=r_mt, column=9).font = font(bold=True, color=WHITE, size=8); ws_comp.cell(row=r_mt, column=9).alignment = align('center', 'center')

ws_comp.cell(row=r_mt, column=10, value="Presupuesto Semestral Lerma-Tres Marías ajustado por estacionalidad de montaña.").fill = fill(TEAL_HDR)
ws_comp.cell(row=r_mt, column=10).font = font(italic=True, color='94A3B8', size=8); ws_comp.cell(row=r_mt, column=10).alignment = align('left', 'center')

for c in range(1, 11):
    cell = ws_comp.cell(row=r_mt, column=c)
    if c not in [1, 9, 10]:
        cell.fill = fill(TEAL_HDR); cell.font = font(bold=True, color=WHITE, size=9)
        cell.alignment = align('right', 'center')
    cell.border = thin_border()
ws_comp.row_dimensions[r_mt].height = 22

# Widths
for col in ws_comp.columns:
    col_letter = get_column_letter(col[0].column)
    if col_letter == 'J':
        ws_comp.column_dimensions[col_letter].width = 46
    else:
        max_len = 0
        for cell in col:
            val_str = str(cell.value or '')
            if '\n' in val_str: val_str = max(val_str.split('\n'), key=len)
            max_len = max(max_len, len(val_str))
        ws_comp.column_dimensions[col_letter].width = max(max_len + 3, 13)

wb.save(filename)
print("Updated Excel file with separate per-obra comparison tables successfully!")
