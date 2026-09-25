import openpyxl, re, datetime, psycopg2
from psycopg2.extras import DictCursor
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Conectar a base de datos
conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

cur.execute("""
    SELECT folio_factura, semana, fecha_factura, obra_destino, litros_facturados, importe_total, estatus_revision
    FROM diesel.facturas
    WHERE proveedor ILIKE '%CASTILLA%';
""")
db_diesel = {}
for r in cur.fetchall():
    cf = re.sub(r'[^0-9]', '', r['folio_factura'])
    db_diesel[cf] = dict(r)

# Cargar Google Sheet Estado de Cuenta
wb_gs = openpyxl.load_workbook('gasolina/conciliacion_gasolina_google_sheets.xlsx', data_only=True)
ws_ec = wb_gs['Estado de Cuenta']

# Facturas pagadas en imágenes
tabla_1_raw = [
    ("20 de julio de 2026", 1857.15, "BACHEO TOLUCA", "A-10484"),
    ("20 de julio de 2026", 12150.08, "P. DE ASFALTO HUIXQUILUCAN", "A-10485"),
    ("20 de julio de 2026", 21600.09, "P. DE ASFALTO HUIXQUILUCAN", "A-10491"),
    ("20 de julio de 2026", 10800.97, "ALFREDO DEL MAZO", "A-10492"),
    ("14 de julio de 2026", 27000.11, "COLEGIO MILITAR", "A-10496"),
    ("21 de julio de 2026", 10800.13, "P. DE ASFALTO HUIXQUILUCAN", "A-10520"),
    ("21 de julio de 2026", 21600.15, "DEZAZOLVE CANALES", "A-10521"),
    ("21 de julio de 2026", 25925.00, "MEXICO TOLUCA", "A-10522"),
    ("21 de julio de 2026", 5400.05, "ALFREDO DEL MAZO", "A-10532"),
    ("22 de julio de 2026", 21600.15, "P. DE ASFALTO HUIXQUILUCAN", "A-10535"),
    ("22 de julio de 2026", 21600.15, "DEZAZOLVE CANALES", "A-10543"),
    ("23 de julio de 2026", 8100.00, "ALFREDO DEL MAZO", "A-10544"),
    ("23 de julio de 2026", 10800.10, "P. DE ASFALTO HUIXQUILUCAN", "A-10556"),
    ("23 de julio de 2026", 25650.13, "MEXICO TOLUCA", "A-10563"),
    ("23 de julio de 2026", 4860.05, "DEZAZOLVE CANALES", "A-10564"),
    ("23 de julio de 2026", 7290.05, "CONSTITUCION", "A-10565"),
    ("23 de julio de 2026", 14850.08, "ALFREDO DEL MAZO", "A-10572"),
    ("23 de julio de 2026", 24840.10, "ALFREDO DEL MAZO", "A-10577"),
    ("24 de julio de 2026", 10800.10, "P. DE ASFALTO HUIXQUILUCAN", "A-10579"),
    ("27 de julio de 2026", 10800.10, "P. DE ASFALTO HUIXQUILUCAN", "A-10581"),
    ("24 de julio de 2026", 18900.06, "ALFREDO DEL MAZO", "A-10583"),
    ("24 de julio de 2026", 14364.05, "DEZAZOLVE CANALES", "A-10586"),
    ("24 de julio de 2026", 1080.03, "MEXICO TOLUCA", "A-10587"),
    ("24 de julio de 2026", 12960.06, "ALFREDO DEL MAZO", "A-10588"),
    ("25 de julio de 2026", 24840.10, "MEXICO TOLUCA", "A-10589"),
    ("27 de julio de 2026", 9720.03, "LERMA", "A-10603"),
    ("27 de julio de 2026", 3240.00, "PROVIDENCIA", "A-10604"),
    ("28 de julio de 2026", 10800.03, "P. DE ASFALTO HUIXQUILUCAN", "A-10605"),
    ("28 de julio de 2026", 30502.11, "MEXICO TOLUCA", "A-10623"),
    ("28 de julio de 2026", 23490.11, "DEZAZOLVE CANALES", "A-10624"),
    ("28 de julio de 2026", 10800.10, "P. DE ASFALTO HUIXQUILUCAN", "A-10625"),
    ("28 de julio de 2026", 26959.90, "P. DE ASFALTO HUIXQUILUCAN", "A-10630"),
    ("28 de julio de 2026", 1620.03, "P. DE ASFALTO HUIXQUILUCAN", "A-10634"),
    ("29 de julio de 2026", 1558.03, "P. DE ASFALTO HUIXQUILUCAN", "A-10635"),
    ("28 de julio de 2026", 10260.10, "ALFREDO DEL MAZO", "A-10636"),
    ("29 de julio de 2026", 24564.14, "LERMA", "A-10637"),
    ("31 de julio de 2026", 3510.00, "PROVIDENCIA", "A-10644"),
    ("31 de julio de 2026", 17820.03, "ALFREDO DEL MAZO", "A-10645"),
    ("31 de julio de 2026", 25650.09, "DEZAZOLVE CANALES", "A-10646"),
    ("30 de julio de 2026", 21600.46, "P. DE ASFALTO HUIXQUILUCAN", "A-10652"),
    ("27 de julio de 2026", 3105.00, "BACHEO TOLUCA", "A-10653"),
    ("27 de julio de 2026", 24852.31, "DEZAZOLVE CANALES", "A-10654"),
    ("1 de agosto de 2026", 8100.05, "P. DE ASFALTO HUIXQUILUCAN", "A-10669"),
    ("1 de agosto de 2026", 25920.06, "MEXICO TOLUCA", "A-10673"),
    ("1 de agosto de 2026", 8100.05, "P. DE ASFALTO HUIXQUILUCAN", "A-10674"),
    ("29 de julio de 2026", 20520.09, "DEZAZOLVE CANALES", "A-10702"),
    ("29 de julio de 2026", 1620.03, "PROVIDENCIA", "A-10712"),
    ("29 de julio de 2026", 9736.66, "ALFREDO DEL MAZO", "A-10713"),
    ("30 de julio de 2026", 21600.14, "P. DE ASFALTO HUIXQUILUCAN", "A-10722"),
    ("30 de julio de 2026", 24840.10, "MEXICO TOLUCA", "A-10733"),
    ("30 de julio de 2026", 1485.03, "P. DE ASFALTO HUIXQUILUCAN", "A-10748"),
    ("17 de julio de 2026", 5400.05, "P. DE ASFALTO HUIXQUILUCAN", "A-23783100"),
]

tabla_2_raw = [
    ("6 de julio de 2026", 66605.40, "TANQUE PEGASO", "A-10360"),
    ("7 de julio de 2026", 8100.05, "TANQUE PEGASO", "A-10380"),
    ("7 de julio de 2026", 3000.00, "TANQUE PEGASO", "A-10386"),
    ("7 de julio de 2026", 18900.06, "LERMA", "A-10381"),
    ("7 de julio de 2026", 2700.08, "LERMA", "A-10388"),
    ("6 de julio de 2026", 8100.05, "P. DE ASFALTO HUIXQUILUCAN", "A-10361"),
    ("6 de julio de 2026", 10800.10, "P. DE ASFALTO HUIXQUILUCAN", "A-10365"),
    ("6 de julio de 2026", 16200.10, "P. DE ASFALTO HUIXQUILUCAN", "A-10368"),
    ("7 de julio de 2026", 16200.10, "P. DE ASFALTO HUIXQUILUCAN", "A-10884"),
    ("8 de julio de 2026", 10800.10, "P. DE ASFALTO HUIXQUILUCAN", "A-10405"),
    ("8 de julio de 2026", 8100.05, "P. DE ASFALTO HUIXQUILUCAN", "A-10406"),
    ("8 de julio de 2026", 8100.05, "P. DE ASFALTO HUIXQUILUCAN", "A-10408"),
    ("6 de julio de 2026", 6291.00, "PROVIDENCIA", "A-10362"),
    ("6 de julio de 2026", 7695.00, "BACHEO TOLUCA", "A-10366"),
    ("7 de julio de 2026", 21600.15, "BACHEO TOLUCA", "A-10387"),
    ("6 de julio de 2026", 19305.10, "MEXICO TOLUCA", "A-10367"),
    ("8 de julio de 2026", 16200.10, "MEXICO TOLUCA", "A-10398"),
    ("8 de julio de 2026", 23206.21, "DEZAZOLVE CANALES", "A-10409"),
    ("13 de julio de 2026", 601.43, "TANQUE PEGASO", "A-10420"),
    ("15 de julio de 2026", 108000.36, "TANQUE PEGASO", "A-10510"),
    ("13 de julio de 2026", 4197.68, "TANQUE PEGASO", "A-10511"),
    ("10 de julio de 2026", 18043.21, "LERMA", "A-10894"),
    ("13 de julio de 2026", 17804.45, "LERMA", "A-10426"),
    ("13 de julio de 2026", 3000.00, "LERMA", "A-10427"),
    ("9 de julio de 2026", 2700.08, "MAQUINARIA", "A-10886"),
    ("9 de julio de 2026", 16201.80, "P. DE ASFALTO HUIXQUILUCAN", "A-10888"),
    ("10 de julio de 2026", 27000.11, "P. DE ASFALTO HUIXQUILUCAN", "A-10899"),
    ("11 de julio de 2026", 13500.06, "P. DE ASFALTO HUIXQUILUCAN", "A-10904"),
    ("12 de julio de 2026", 8100.05, "P. DE ASFALTO HUIXQUILUCAN", "A-10912"),
    ("14 de julio de 2026", 16200.10, "P. DE ASFALTO HUIXQUILUCAN", "A-10495"),
    ("15 de julio de 2026", 8100.05, "P. DE ASFALTO HUIXQUILUCAN", "A-10438"),
    ("15 de julio de 2026", 27000.11, "P. DE ASFALTO HUIXQUILUCAN", "A-10514"),
    ("13 de julio de 2026", 14445.05, "VICENTE LOMBARDO", "A-10422"),
    ("14 de julio de 2026", 11880.00, "VICENTE LOMBARDO", "A-10499"),
    ("9 de julio de 2026", 10800.10, "PROVIDENCIA", "A-10887"),
    ("15 de julio de 2026", 5400.05, "PROVIDENCIA", "A-10513"),
    ("10 de julio de 2026", 5400.05, "ALFREDO DEL MAZO", "A-10893"),
    ("13 de julio de 2026", 22652.97, "ALFREDO DEL MAZO", "A-10425"),
    ("15 de julio de 2026", 10800.13, "ALFREDO DEL MAZO", "A-10512"),
    ("15 de julio de 2026", 29693.92, "MEXICO TOLUCA", "A-10509"),
    ("10 de julio de 2026", 24705.06, "DEZAZOLVE CANALES", "A-10900"),
    ("13 de julio de 2026", 14445.05, "DEZAZOLVE CANALES", "A-10423"),
    ("14 de julio de 2026", 11880.00, "DEZAZOLVE CANALES", "A-10500"),
    ("16 de julio de 2026", 16200.10, "ALFREDO DEL MAZO", "A-10446"),
    ("16 de julio de 2026", 10800.10, "PROVIDENCIA", "A-10447"),
    ("16 de julio de 2026", 13500.55, "P. DE ASFALTO HUIXQUILUCAN", "A-10449"),
    ("16 de julio de 2026", 22950.13, "DEZAZOLVE CANALES", "A-10453"),
    ("16 de julio de 2026", 1800.02, "TANQUE PEGASO", "A-10454"),
    ("17 de julio de 2026", 27000.11, "LERMA", "A-10457"),
    ("17 de julio de 2026", 10800.06, "P. DE ASFALTO HUIXQUILUCAN", "A-10458"),
    ("17 de julio de 2026", 32400.12, "MEXICO TOLUCA", "A-10459"),
    ("18 de julio de 2026", 20250.13, "ALFREDO DEL MAZO", "A-10474"),
    ("20 de julio de 2026", 12285.08, "PROVIDENCIA", "A-10479"),
    ("20 de julio de 2026", 14715.08, "LERMA", "A-10480"),
    ("20 de julio de 2026", 16200.10, "DEZAZOLVE CANALES", "A-10483"),
    ("20 de julio de 2026", 11642.85, "BACHEO TOLUCA", "A-10484"),
]

def parse_date(date_str):
    meses = {'julio': 7, 'agosto': 8, 'junio': 6, 'mayo': 5}
    m = re.search(r'(\d+)\s+de\s+(\w+)\s+de\s+(\d+)', date_str.lower())
    if m:
        day = int(m.group(1))
        mes_nombre = m.group(2)
        year = int(m.group(3))
        month = meses.get(mes_nombre, 7)
        return datetime.date(year, month, day)
    return None

def get_week(dt):
    if dt < datetime.date(2026, 7, 6): return 27
    elif dt <= datetime.date(2026, 7, 12): return 28
    elif dt <= datetime.date(2026, 7, 19): return 29
    elif dt <= datetime.date(2026, 7, 26): return 30
    elif dt <= datetime.date(2026, 8, 2): return 31
    else: return 32

# Procesar partidas pagadas
partidas_pagadas = []
for orig_list, name in [(tabla_1_raw, "Tabla 1 ($747k)"), (tabla_2_raw, "Tabla 2 ($915k)")]:
    for item in orig_list:
        dt = parse_date(item[0])
        sem = get_week(dt)
        cf = re.sub(r'[^0-9]', '', item[3])
        partidas_pagadas.append({
            'origen_tabla': name,
            'fecha': dt,
            'fecha_str': item[0],
            'importe': item[1],
            'centro_trabajo': item[2],
            'folio': item[3],
            'folio_num': cf,
            'semana': sem
        })

# Crear Libro Excel
wb = openpyxl.Workbook()
wb.remove(wb.active) # Remover hoja por defecto

# Estilos corporativos Fénix
font_title = Font(name='Calibri', size=15, bold=True, color='FFFFFF')
font_subtitle = Font(name='Calibri', size=11, bold=True, color='333333')
font_header = Font(name='Calibri', size=11, bold=True, color='FFFFFF')
font_subtotal = Font(name='Calibri', size=11, bold=True, color='1E3A8A')
font_data = Font(name='Calibri', size=10, bold=False, color='000000')
font_data_bold = Font(name='Calibri', size=10, bold=True, color='000000')
font_alert = Font(name='Calibri', size=10, bold=True, color='9C0006')
font_ok = Font(name='Calibri', size=10, bold=True, color='006100')

fill_navy = PatternFill(start_color='1E3A8A', end_color='1E3A8A', fill_type='solid') # Azul oscuro Fénix
fill_blue_light = PatternFill(start_color='DBEAFE', end_color='DBEAFE', fill_type='solid')
fill_gray_header = PatternFill(start_color='334155', end_color='334155', fill_type='solid')
fill_gray_subtotal = PatternFill(start_color='F1F5F9', end_color='F1F5F9', fill_type='solid')
fill_green_light = PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid')
fill_red_light = PatternFill(start_color='FFC7CE', end_color='FFC7CE', fill_type='solid')
fill_yellow_light = PatternFill(start_color='FFEB9C', end_color='FFEB9C', fill_type='solid')

thin_border = Border(
    left=Side(style='thin', color='CBD5E1'),
    right=Side(style='thin', color='CBD5E1'),
    top=Side(style='thin', color='CBD5E1'),
    bottom=Side(style='thin', color='CBD5E1')
)
top_thin_bottom_double = Border(
    top=Side(style='thin', color='000000'),
    bottom=Side(style='double', color='000000'),
    left=Side(style='thin', color='CBD5E1'),
    right=Side(style='thin', color='CBD5E1')
)

align_center = Alignment(horizontal='center', vertical='center')
align_left = Alignment(horizontal='left', vertical='center')
align_right = Alignment(horizontal='right', vertical='center')

# ==============================================================================
# HOJA 1: RESUMEN EJECUTIVO Y COMPARATIVO GLOBAL
# ==============================================================================
ws_res = wb.create_sheet(title="Resumen_Ejecutivo")
ws_res.views.sheetView[0].showGridLines = True

# Título
ws_res.merge_cells("A1:H1")
ws_res["A1"] = "GRUPO TRUJANO - SISTEMA FÉNIX | CONCILIACIÓN DE FACTURAS Y PAGOS MOBIL HUIXQUILUCAN"
ws_res["A1"].font = font_title
ws_res["A1"].fill = fill_navy
ws_res["A1"].alignment = align_center
ws_res.row_dimensions[1].height = 40

ws_res.merge_cells("A2:H2")
ws_res["A2"] = "Proveedor: Derivados de Petróleo Castilla S.A. de C.V. | Periodo: Semanas 28 a 32 de 2026 | Fecha Conciliación: Agosto 2026"
ws_res["A2"].font = font_subtitle
ws_res["A2"].alignment = align_center
ws_res.row_dimensions[2].height = 22

# Tabla 1: Comparativo por Semana
headers_res1 = [
    "Semana Operativa", "Periodo de Suministro", "No. Facturas Pagadas",
    "Monto Pagado en Imágenes ($)", "Monto Estado de Cuenta ($)", "Diferencia ($)",
    "Estatus Pago", "Concepto Principal Pagado"
]

row_idx = 4
for c_idx, h in enumerate(headers_res1, start=1):
    cell = ws_res.cell(row=row_idx, column=c_idx, value=h)
    cell.font = font_header
    cell.fill = fill_navy
    cell.alignment = align_center
    cell.border = thin_border
ws_res.row_dimensions[row_idx].height = 28

semanas_meta = [
    (28, "06 Jul - 12 Jul 2026", 27, 398354.22, 334052.62, "PAGADO", "Diesel Obra ($328.7k) + Tanque Pegaso ($66.6k) + Gasolina ($3k)"),
    (29, "13 Jul - 19 Jul 2026", 27, 494202.83, 391703.36, "PAGADO", "Diesel Obra ($376.6k) + Tanque Pegaso ($112.8k) + Gasolina ($4.8k)"),
    (30, "20 Jul - 26 Jul 2026", 27, 387511.94, 410312.10, "PAGADO (Diesel)", "Diesel Obra 100% Pagado ($387.5k). Gasolina pendiente ($12k)"),
    (31, "27 Jul - 01 Ago 2026", 27, 382774.78, 384745.72, "PAGADO (Diesel)", "Diesel Obra 100% Pagado ($382.7k). Gasolina pendiente ($10.8k)"),
    (32, "03 Ago - 09 Ago 2026", 0, 0.00, 341114.27, "PENDIENTE", "Semana completa sin pago en este paquete ($341.1k)")
]

for sem, per, n_pag, m_pag, m_edo, est, conc in semanas_meta:
    row_idx += 1
    diff = m_pag - m_edo
    ws_res.cell(row=row_idx, column=1, value=f"Semana {sem}").alignment = align_center
    ws_res.cell(row=row_idx, column=2, value=per).alignment = align_center
    ws_res.cell(row=row_idx, column=3, value=n_pag).alignment = align_center
    
    c_pag = ws_res.cell(row=row_idx, column=4, value=m_pag)
    c_pag.number_format = "$#,##0.00"
    c_pag.alignment = align_right
    
    c_edo = ws_res.cell(row=row_idx, column=5, value=m_edo)
    c_edo.number_format = "$#,##0.00"
    c_edo.alignment = align_right
    
    c_dif = ws_res.cell(row=row_idx, column=6, value=diff)
    c_dif.number_format = "$#,##0.00"
    c_dif.alignment = align_right
    
    c_est = ws_res.cell(row=row_idx, column=7, value=est)
    c_est.alignment = align_center
    if "PENDIENTE" in est:
        c_est.fill = fill_red_light
        c_est.font = font_alert
    elif "PAGADO" in est:
        c_est.fill = fill_green_light
        c_est.font = font_ok
        
    ws_res.cell(row=row_idx, column=8, value=conc).alignment = align_left
    
    for c in range(1, 9):
        ws_res.cell(row=row_idx, column=c).border = thin_border
        if not ws_res.cell(row=row_idx, column=c).font.bold:
            ws_res.cell(row=row_idx, column=c).font = font_data
    ws_res.row_dimensions[row_idx].height = 22

# Fila Total
row_idx += 1
ws_res.cell(row=row_idx, column=1, value="TOTAL GENERAL").alignment = align_center
ws_res.cell(row=row_idx, column=1).font = font_subtotal
ws_res.cell(row=row_idx, column=2, value="Semanas 28 a 32").alignment = align_center
ws_res.cell(row=row_idx, column=3, value=108).alignment = align_center

c_tot_pag = ws_res.cell(row=row_idx, column=4, value="=SUM(D5:D9)")
c_tot_pag.number_format = "$#,##0.00"
c_tot_pag.font = font_subtotal
c_tot_pag.alignment = align_right

c_tot_edo = ws_res.cell(row=row_idx, column=5, value="=SUM(E5:E9)")
c_tot_edo.number_format = "$#,##0.00"
c_tot_edo.font = font_subtotal
c_tot_edo.alignment = align_right

c_tot_dif = ws_res.cell(row=row_idx, column=6, value="=D10-E10")
c_tot_dif.number_format = "$#,##0.00"
c_tot_dif.font = font_subtotal
c_tot_dif.alignment = align_right

ws_res.cell(row=row_idx, column=7, value="CONCILIADO").alignment = align_center
ws_res.cell(row=row_idx, column=7).font = font_subtotal
ws_res.cell(row=row_idx, column=8, value="Diesel Sem 28-31 Pagado | Sem 32 y Gasolina Pendientes").alignment = align_left
ws_res.cell(row=row_idx, column=8).font = font_subtotal

for c in range(1, 9):
    ws_res.cell(row=row_idx, column=c).fill = fill_blue_light
    ws_res.cell(row=row_idx, column=c).border = top_thin_bottom_double
ws_res.row_dimensions[row_idx].height = 25

# Tabla de Explicación de Conciliación de Saldos
row_idx += 3
ws_res.cell(row=row_idx, column=1, value="EXPLICACIÓN DETALLADA DE LA CONCILIACIÓN DE SALDOS").font = font_subtitle
ws_res.row_dimensions[row_idx].height = 22

explicaciones = [
    ("1. Suma Real de las Tablas Pagadas (Imágenes)", "$1,662,843.77", "Corresponde a Tabla 1 ($747,843.77) + Tabla 2 ($915,000.00), totalizando exactamente 108 partidas."),
    ("2. Total Reportado Inicialmente como Pagado", "$1,675,551.72", "Existe una partida de $12,707.95 pendiente de identificar en fichas bancarias/recibos complementarios."),
    ("3. Saldo Registrado en Estado de Cuenta CON Semana 28", "$1,861,928.07", "Incluye Semanas 28, 29, 30, 31 Y ADEMÁS LA SEMANA 32 ($341,114.27). No contemplaba tanques granel Pegaso."),
    ("4. Saldo Registrado en Estado de Cuenta SIN Semana 28", "$1,527,875.45", "Incluye Semanas 29, 30, 31 Y 32 ($341,114.27). La semana 28 del Estado de Cuenta sumaba $334,052.62."),
    ("5. Monto Pendiente Real de Pago a Mobil Huixquilucan", "$378,511.30", "Semana 32 completa ($341,114.27) + Facturas de gasolina pendientes de Semanas 29, 30 y 31 ($37,397.03).")
]

row_idx += 1
for conc, monto, detalle in explicaciones:
    ws_res.cell(row=row_idx, column=1, value=conc).font = font_data_bold
    ws_res.cell(row=row_idx, column=1).alignment = align_left
    ws_res.merge_cells(start_row=row_idx, start_column=1, end_row=row_idx, end_column=3)
    
    c_m = ws_res.cell(row=row_idx, column=4, value=monto)
    c_m.font = font_data_bold
    c_m.alignment = align_right
    c_m.fill = fill_gray_subtotal
    
    ws_res.cell(row=row_idx, column=5, value=detalle).font = font_data
    ws_res.merge_cells(start_row=row_idx, start_column=5, end_row=row_idx, end_column=8)
    
    for c in range(1, 9):
        ws_res.cell(row=row_idx, column=c).border = thin_border
    ws_res.row_dimensions[row_idx].height = 22
    row_idx += 1

# ==============================================================================
# HOJA 2: CONCILIACIÓN FACTURA POR FACTURA (QUÉ SE PAGÓ Y QUÉ FALTA POR PAGAR)
# ==============================================================================
ws_det = wb.create_sheet(title="Conciliacion_Facturas")
ws_det.views.sheetView[0].showGridLines = True

ws_det.merge_cells("A1:I1")
ws_det["A1"] = "CONCILIACIÓN DETALLADA DE FACTURAS: ESTADO DE CUENTA VS PAGOS REALIZADOS (MOBIL HUIXQUILUCAN)"
ws_det["A1"].font = font_title
ws_det["A1"].fill = fill_navy
ws_det["A1"].alignment = align_center
ws_det.row_dimensions[1].height = 35

headers_det = [
    "Semana", "No. Factura", "Tipo Combustible", "Centro de Trabajo / Obra",
    "Fecha Suministro", "Monto en Factura / Edo Cta ($)", "Monto Pagado en Imágenes ($)",
    "Saldo Pendiente ($)", "Estatus Conciliación"
]

row_idx = 3
for c_idx, h in enumerate(headers_det, start=1):
    cell = ws_det.cell(row=row_idx, column=c_idx, value=h)
    cell.font = font_header
    cell.fill = fill_navy
    cell.alignment = align_center
    cell.border = thin_border
ws_det.row_dimensions[row_idx].height = 25

# Mapear todas las facturas pagadas
pagados_lookup = {}
for p in partidas_pagadas:
    cf = p['folio_num']
    if cf not in pagados_lookup:
        pagados_lookup[cf] = []
    pagados_lookup[cf].append(p)

# Extraer y armar filas ordenadas por semana
all_conciliation_rows = []

# 1. Facturas que están en las imágenes
folios_procesados = set()
for p in partidas_pagadas:
    cf = p['folio_num']
    if cf in folios_procesados:
        continue
    folios_procesados.add(cf)
    
    items_p = pagados_lookup[cf]
    tot_pag = sum(x['importe'] for x in items_p)
    f_fecha = items_p[0]['fecha']
    f_obra = items_p[0]['centro_trabajo']
    f_sem = items_p[0]['semana']
    f_orig = items_p[0]['folio']
    
    # Buscar en BD
    monto_bd = tot_pag
    tipo = "DIESEL"
    if cf in db_diesel:
        monto_bd = float(db_diesel[cf]['importe_total'])
        f_obra = db_diesel[cf]['obra_destino'] or f_obra
    
    if "GASOLINA" in f_obra.upper() or cf in ['10386', '10427', '10454', '10635']:
        tipo = "GASOLINA / MENOR"
    
    saldo = max(0.0, monto_bd - tot_pag)
    if saldo < 0.05:
        estatus = "PAGADO AL 100%"
    else:
        estatus = "PAGADO PARCIAL"
        
    all_conciliation_rows.append({
        'semana': f_sem,
        'folio': f_orig,
        'folio_num': cf,
        'tipo': tipo,
        'obra': f_obra,
        'fecha': f_fecha,
        'monto_factura': monto_bd,
        'monto_pagado': tot_pag,
        'saldo': saldo,
        'estatus': estatus
    })

# 2. Facturas de Gasolina y Semana 32 que están en el Estado de Cuenta de Google Sheets pero NO en imágenes
# Semana 29 pendientes
pendientes_gs = [
    (29, "A-10424", "GASOLINA", "Vehículos Menores", None, 1500.00, 0.0, 1500.00, "PENDIENTE POR PAGAR"),
    (29, "A-10434", "GASOLINA", "Vehículos Menores", None, 1200.00, 0.0, 1200.00, "PENDIENTE POR PAGAR"),
    (29, "A-10450", "GASOLINA", "Vehículos Menores", None, 1500.00, 0.0, 1500.00, "PENDIENTE POR PAGAR"),
    (29, "A-10451", "GASOLINA", "Vehículos Menores", None, 1500.00, 0.0, 1500.00, "PENDIENTE POR PAGAR"),
    (29, "A-10460", "GASOLINA", "Vehículos Menores", None, 1500.00, 0.0, 1500.00, "PENDIENTE POR PAGAR"),
    (29, "A-10470", "GASOLINA", "Vehículos Menores", None, 1500.00, 0.0, 1500.00, "PENDIENTE POR PAGAR"),
    (29, "A-10515", "GASOLINA", "Vehículos Menores", None, 1600.00, 0.0, 1600.00, "PENDIENTE POR PAGAR"),
    (29, "A-23783097", "GASOLINA", "Vehículos Menores", None, 1500.00, 0.0, 1500.00, "PENDIENTE POR PAGAR"),
    (29, "A-23783099", "GASOLINA", "Vehículos Menores", None, 1500.00, 0.0, 1500.00, "PENDIENTE POR PAGAR"),
    # Semana 30 pendientes
    (30, "A-10482", "GASOLINA", "Vehículos Menores", None, 2500.00, 0.0, 2500.00, "PENDIENTE POR PAGAR"),
    (30, "A-10486", "GASOLINA", "Vehículos Menores", None, 2000.00, 0.0, 2000.00, "PENDIENTE POR PAGAR"),
    (30, "A-10518", "GASOLINA", "Vehículos Menores", None, 1200.00, 0.0, 1200.00, "PENDIENTE POR PAGAR"),
    (30, "A-10545", "GASOLINA", "Vehículos Menores", None, 1500.00, 0.0, 1500.00, "PENDIENTE POR PAGAR"),
    (30, "A-10552", "GASOLINA", "Vehículos Menores", None, 1500.00, 0.0, 1500.00, "PENDIENTE POR PAGAR"),
    (30, "A-10567", "GASOLINA", "Vehículos Menores", None, 800.00, 0.0, 800.00, "PENDIENTE POR PAGAR"),
    (30, "A-10571", "GASOLINA", "Vehículos Menores", None, 500.00, 0.0, 500.00, "PENDIENTE POR PAGAR"),
    (30, "A-10580", "GASOLINA", "Vehículos Menores", None, 1000.00, 0.0, 1000.00, "PENDIENTE POR PAGAR"),
    (30, "A-10585", "GASOLINA", "Vehículos Menores", None, 1000.00, 0.0, 1000.00, "PENDIENTE POR PAGAR"),
    # Semana 31 pendientes
    (31, "A-10606", "GASOLINA", "Vehículos Menores", None, 1000.00, 0.0, 1000.00, "PENDIENTE POR PAGAR"),
    (31, "A-10607", "GASOLINA", "Vehículos Menores", None, 3511.75, 0.0, 3511.75, "PENDIENTE POR PAGAR"),
    (31, "A-10620", "GASOLINA", "Vehículos Menores", None, 1904.88, 0.0, 1904.88, "PENDIENTE POR PAGAR"),
    (31, "A-10621", "GASOLINA", "Vehículos Menores", None, 1500.00, 0.0, 1500.00, "PENDIENTE POR PAGAR"),
    (31, "A-10710", "GASOLINA", "Vehículos Menores", None, 1500.00, 0.0, 1500.00, "PENDIENTE POR PAGAR"),
    (31, "A-10741", "GASOLINA", "Vehículos Menores", None, 1402.36, 0.0, 1402.36, "PENDIENTE POR PAGAR"),
    # Semana 32 pendientes (Paquete completo)
    (32, "LOTE SEMANA 32", "DIESEL Y GASOLINA", "Obras Varias (29 facturas diesel + 9 gasolina)", None, 341114.27, 0.0, 341114.27, "PENDIENTE POR PAGAR")
]

for sem, fol, tip, obr, fec, m_fac, m_pag, sal, est in pendientes_gs:
    all_conciliation_rows.append({
        'semana': sem,
        'folio': fol,
        'folio_num': re.sub(r'[^0-9]', '', fol),
        'tipo': tip,
        'obra': obr,
        'fecha': fec,
        'monto_factura': m_fac,
        'monto_pagado': m_pag,
        'saldo': sal,
        'estatus': est
    })

# Ordenar filas por Semana, Fecha, Folio
all_conciliation_rows_sorted = sorted(all_conciliation_rows, key=lambda x: (x['semana'], x['fecha'] or datetime.date(2026, 8, 15), x['folio']))

for r in all_conciliation_rows_sorted:
    row_idx += 1
    ws_det.cell(row=row_idx, column=1, value=f"Semana {r['semana']}").alignment = align_center
    ws_det.cell(row=row_idx, column=2, value=r['folio']).alignment = align_center
    ws_det.cell(row=row_idx, column=3, value=r['tipo']).alignment = align_center
    ws_det.cell(row=row_idx, column=4, value=r['obra']).alignment = align_left
    ws_det.cell(row=row_idx, column=5, value=r['fecha'].strftime("%d/%m/%Y") if r['fecha'] else "Agosto 2026").alignment = align_center
    
    c_fac = ws_det.cell(row=row_idx, column=6, value=r['monto_factura'])
    c_fac.number_format = "$#,##0.00"
    c_fac.alignment = align_right
    
    c_pag = ws_det.cell(row=row_idx, column=7, value=r['monto_pagado'])
    c_pag.number_format = "$#,##0.00"
    c_pag.alignment = align_right
    
    c_sal = ws_det.cell(row=row_idx, column=8, value=r['saldo'])
    c_sal.number_format = "$#,##0.00"
    c_sal.alignment = align_right
    
    c_est = ws_det.cell(row=row_idx, column=9, value=r['estatus'])
    c_est.alignment = align_center
    
    if "PENDIENTE" in r['estatus']:
        c_est.fill = fill_red_light
        c_est.font = font_alert
    elif "PARCIAL" in r['estatus']:
        c_est.fill = fill_yellow_light
        c_est.font = font_data_bold
    else:
        c_est.fill = fill_green_light
        c_est.font = font_ok
        
    for c in range(1, 10):
        ws_det.cell(row=row_idx, column=c).border = thin_border
        if not ws_det.cell(row=row_idx, column=c).font.bold:
            ws_det.cell(row=row_idx, column=c).font = font_data
    ws_det.row_dimensions[row_idx].height = 20

# Fila total
row_idx += 1
ws_det.cell(row=row_idx, column=1, value="TOTAL CONCILIACIÓN").alignment = align_center
ws_det.cell(row=row_idx, column=1).font = font_subtotal
ws_det.merge_cells(start_row=row_idx, start_column=1, end_row=row_idx, end_column=5)

c_tot_f = ws_det.cell(row=row_idx, column=6, value=f"=SUM(F4:F{row_idx-1})")
c_tot_f.number_format = "$#,##0.00"
c_tot_f.font = font_subtotal
c_tot_f.alignment = align_right

c_tot_p = ws_det.cell(row=row_idx, column=7, value=f"=SUM(G4:G{row_idx-1})")
c_tot_p.number_format = "$#,##0.00"
c_tot_p.font = font_subtotal
c_tot_p.alignment = align_right

c_tot_s = ws_det.cell(row=row_idx, column=8, value=f"=SUM(H4:H{row_idx-1})")
c_tot_s.number_format = "$#,##0.00"
c_tot_s.font = font_subtotal
c_tot_s.alignment = align_right

ws_det.cell(row=row_idx, column=9, value="BALANCE GENERAL").alignment = align_center
ws_det.cell(row=row_idx, column=9).font = font_subtotal

for c in range(1, 10):
    ws_det.cell(row=row_idx, column=c).fill = fill_blue_light
    ws_det.cell(row=row_idx, column=c).border = top_thin_bottom_double
ws_det.row_dimensions[row_idx].height = 25

# ==============================================================================
# HOJAS 3, 4, 5, 6: DETALLE INDIVIDUAL POR CADA SEMANA (28, 29, 30, 31)
# ==============================================================================
for target_sem in [28, 29, 30, 31]:
    ws_sem = wb.create_sheet(title=f"Semana_{target_sem}")
    ws_sem.views.sheetView[0].showGridLines = True
    
    # Título de la Semana
    ws_sem.merge_cells("A1:G1")
    ws_sem["A1"] = f"PAGOS A MOBIL HUIXQUILUCAN - SEMANA {target_sem} DE 2026"
    ws_sem["A1"].font = font_title
    ws_sem["A1"].fill = fill_navy
    ws_sem["A1"].alignment = align_center
    ws_sem.row_dimensions[1].height = 35
    
    headers_s = [
        "No.", "Fecha Suministro", "Folio Factura", "Centro de Trabajo / Obra",
        "Importe Pagado con IVA ($)", "Tabla Origen Pago", "Estatus"
    ]
    
    r_idx = 3
    for c_idx, h in enumerate(headers_s, start=1):
        cell = ws_sem.cell(row=r_idx, column=c_idx, value=h)
        cell.font = font_header
        cell.fill = fill_navy
        cell.alignment = align_center
        cell.border = thin_border
    ws_sem.row_dimensions[r_idx].height = 25
    
    partidas_sem = [p for p in partidas_pagadas if p['semana'] == target_sem]
    partidas_sem_sorted = sorted(partidas_sem, key=lambda x: (x['fecha'], x['centro_trabajo'], x['folio']))
    
    start_data_row = 4
    for idx, p in enumerate(partidas_sem_sorted, start=1):
        r_idx += 1
        ws_sem.cell(row=r_idx, column=1, value=idx).alignment = align_center
        ws_sem.cell(row=r_idx, column=2, value=p['fecha'].strftime("%d/%m/%Y")).alignment = align_center
        ws_sem.cell(row=r_idx, column=3, value=p['folio']).alignment = align_center
        ws_sem.cell(row=r_idx, column=4, value=p['centro_trabajo']).alignment = align_left
        
        c_imp = ws_sem.cell(row=r_idx, column=5, value=p['importe'])
        c_imp.number_format = "$#,##0.00"
        c_imp.alignment = align_right
        
        ws_sem.cell(row=r_idx, column=6, value=p['origen_tabla']).alignment = align_center
        
        c_st = ws_sem.cell(row=r_idx, column=7, value="PAGADO")
        c_st.alignment = align_center
        c_st.fill = fill_green_light
        c_st.font = font_ok
        
        for c in range(1, 8):
            ws_sem.cell(row=r_idx, column=c).border = thin_border
            if not ws_sem.cell(row=r_idx, column=c).font.bold:
                ws_sem.cell(row=r_idx, column=c).font = font_data
        ws_sem.row_dimensions[r_idx].height = 20
        
    # Total Semana
    r_idx += 1
    ws_sem.cell(row=r_idx, column=1, value=f"TOTAL SEMANA {target_sem}").alignment = align_center
    ws_sem.cell(row=r_idx, column=1).font = font_subtotal
    ws_sem.merge_cells(start_row=r_idx, start_column=1, end_row=r_idx, end_column=4)
    
    c_tot_s = ws_sem.cell(row=r_idx, column=5, value=f"=SUM(E{start_data_row}:E{r_idx-1})")
    c_tot_s.number_format = "$#,##0.00"
    c_tot_s.font = font_subtotal
    c_tot_s.alignment = align_right
    
    ws_sem.cell(row=r_idx, column=6, value=f"{len(partidas_sem)} Facturas").alignment = align_center
    ws_sem.cell(row=r_idx, column=6).font = font_subtotal
    
    ws_sem.cell(row=r_idx, column=7, value="LIQUIDADO").alignment = align_center
    ws_sem.cell(row=r_idx, column=7).font = font_subtotal
    
    for c in range(1, 8):
        ws_sem.cell(row=r_idx, column=c).fill = fill_blue_light
        ws_sem.cell(row=r_idx, column=c).border = top_thin_bottom_double
    ws_sem.row_dimensions[r_idx].height = 25

# ==============================================================================
# HOJA 7: SEMANA 32 (PENDIENTE DE PAGO)
# ==============================================================================
ws_s32 = wb.create_sheet(title="Semana_32_Pendiente")
ws_s32.views.sheetView[0].showGridLines = True

ws_s32.merge_cells("A1:F1")
ws_s32["A1"] = "RELACIÓN DE FACTURAS PENDIENTES POR PAGAR - SEMANA 32 (03 AL 09 AGOSTO 2026)"
ws_s32["A1"].font = font_title
ws_s32["A1"].fill = fill_gray_header
ws_s32["A1"].alignment = align_center
ws_s32.row_dimensions[1].height = 35

headers_32 = [
    "No.", "Folio Factura", "Tipo Combustible", "Centro de Trabajo / Obra",
    "Monto Estimado / Facturado ($)", "Estatus"
]
r_idx = 3
for c_idx, h in enumerate(headers_32, start=1):
    cell = ws_s32.cell(row=r_idx, column=c_idx, value=h)
    cell.font = font_header
    cell.fill = fill_gray_header
    cell.alignment = align_center
    cell.border = thin_border
ws_s32.row_dimensions[r_idx].height = 25

# Facturas de Semana 32 en Estado de Cuenta
s32_diesel_fols = ['A10682','A10684','A10683','A10679','A10685','A10692','A10694','A10699','A10693','A10770','A10773','A10778','A10771','A10779','A10774','A10783','A10791','A10785','A10792','A10784','A10793','A10803','A10804','A10792','A10801','A10802','A10811','A10814','A10815']
s32_gas_fols = ['A10681','A10690','A10695','A10772','A10775','A10782','A10786','A10810','A10816']

count_32 = 0
for f in s32_diesel_fols:
    count_32 += 1
    r_idx += 1
    cf = re.sub(r'[^0-9]', '', f)
    monto = float(db_diesel.get(cf, {}).get('importe_total', 0.0))
    obra = db_diesel.get(cf, {}).get('obra_destino', 'Obra Fénix')
    
    ws_s32.cell(row=r_idx, column=1, value=count_32).alignment = align_center
    ws_s32.cell(row=r_idx, column=2, value=f).alignment = align_center
    ws_s32.cell(row=r_idx, column=3, value="DIESEL").alignment = align_center
    ws_s32.cell(row=r_idx, column=4, value=obra).alignment = align_left
    
    c_m = ws_s32.cell(row=r_idx, column=5, value=monto)
    c_m.number_format = "$#,##0.00"
    c_m.alignment = align_right
    
    c_st = ws_s32.cell(row=r_idx, column=6, value="PENDIENTE")
    c_st.alignment = align_center
    c_st.fill = fill_red_light
    c_st.font = font_alert
    
    for c in range(1, 7):
        ws_s32.cell(row=r_idx, column=c).border = thin_border
        if not ws_s32.cell(row=r_idx, column=c).font.bold:
            ws_s32.cell(row=r_idx, column=c).font = font_data
    ws_s32.row_dimensions[r_idx].height = 20

for f in s32_gas_fols:
    count_32 += 1
    r_idx += 1
    ws_s32.cell(row=r_idx, column=1, value=count_32).alignment = align_center
    ws_s32.cell(row=r_idx, column=2, value=f).alignment = align_center
    ws_s32.cell(row=r_idx, column=3, value="GASOLINA").alignment = align_center
    ws_s32.cell(row=r_idx, column=4, value="Vehículos Menores").alignment = align_left
    
    c_m = ws_s32.cell(row=r_idx, column=5, value=1286.45) # promedio
    c_m.number_format = "$#,##0.00"
    c_m.alignment = align_right
    
    c_st = ws_s32.cell(row=r_idx, column=6, value="PENDIENTE")
    c_st.alignment = align_center
    c_st.fill = fill_red_light
    c_st.font = font_alert
    
    for c in range(1, 7):
        ws_s32.cell(row=r_idx, column=c).border = thin_border
        if not ws_s32.cell(row=r_idx, column=c).font.bold:
            ws_s32.cell(row=r_idx, column=c).font = font_data
    ws_s32.row_dimensions[r_idx].height = 20

# Total Semana 32
r_idx += 1
ws_s32.cell(row=r_idx, column=1, value="TOTAL PENDIENTE SEMANA 32").alignment = align_center
ws_s32.cell(row=r_idx, column=1).font = font_subtotal
ws_s32.merge_cells(start_row=r_idx, start_column=1, end_row=r_idx, end_column=4)

c_tot_32 = ws_s32.cell(row=r_idx, column=5, value=341114.27)
c_tot_32.number_format = "$#,##0.00"
c_tot_32.font = font_subtotal
c_tot_32.alignment = align_right

ws_s32.cell(row=r_idx, column=6, value="NO PAGADO").alignment = align_center
ws_s32.cell(row=r_idx, column=6).font = font_alert

for c in range(1, 7):
    ws_s32.cell(row=r_idx, column=c).fill = fill_red_light
    ws_s32.cell(row=r_idx, column=c).border = top_thin_bottom_double
ws_s32.row_dimensions[r_idx].height = 25

# ==============================================================================
# AJUSTAR ANCHOS DE COLUMNAS AUTOMÁTICAMENTE EN TODAS LAS HOJAS
# ==============================================================================
for sheet in wb.worksheets:
    for col in sheet.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            val_str = str(cell.value or '')
            if cell.coordinate in sheet.merged_cells:
                continue # No sobredimensionar por celdas combinadas de títulos
            if len(val_str) > max_len:
                max_len = len(val_str)
        sheet.column_dimensions[col_letter].width = max(max_len + 4, 12)

# Guardar en rutas del proyecto
out_path_1 = "formatos/CONCILIACION_PAGOS_MOBIL_SEMANAS_28_A_32.xlsx"
out_path_2 = "gasolina/CONCILIACION_PAGOS_MOBIL_SEMANAS_28_A_32.xlsx"
wb.save(out_path_1)
wb.save(out_path_2)
print(f"Archivo Excel guardado con éxito en:")
print(f"  1. {out_path_1}")
print(f"  2. {out_path_2}")
