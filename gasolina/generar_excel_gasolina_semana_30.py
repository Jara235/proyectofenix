import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
import psycopg2
from psycopg2.extras import DictCursor
from collections import OrderedDict
import datetime as dt_module

def main():
    # Connect to database
    conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
    cur = conn.cursor(cursor_factory=DictCursor)

    # 1. Colors and Styles
    COL_HDR_FILL   = '1E293B'   # dark header
    COL_ING_FILL   = '312E81'   # purple engineer row
    COL_TOT_FILL   = '1E3A5F'   # totals row
    COL_ALT1       = 'F8FAFC'
    COL_ALT2       = 'EFF6FF'
    WHITE          = 'FFFFFF'

    def fill(hex_color): return PatternFill('solid', fgColor=hex_color)
    def font(bold=False, color='000000', size=10, name='Calibri'): return Font(bold=bold, color=color, size=size, name=name)
    def align(h='center', v='center', wrap=False): return Alignment(horizontal=h, vertical=v, wrap_text=wrap)
    def thin_border():
        s = Side(style='thin', color='CBD5E1')
        return Border(left=s, right=s, top=s, bottom=s)

    def style_hdr(cell, text=None):
        cell.fill = fill(COL_HDR_FILL); cell.font = font(bold=True, color=WHITE, size=9)
        cell.alignment = align('center', 'center', wrap=True); cell.border = thin_border()
        if text is not None: cell.value = text

    def style_ing(cell, text=None):
        cell.fill = fill(COL_ING_FILL); cell.font = font(bold=True, color=WHITE, size=9)
        cell.alignment = align('left', 'center'); cell.border = thin_border()
        if text is not None: cell.value = text

    def style_tot(cell, text=None):
        cell.fill = fill(COL_TOT_FILL); cell.font = font(bold=True, color=WHITE, size=9)
        cell.alignment = align('right', 'center'); cell.border = thin_border()
        if text is not None: cell.value = text

    def style_data(cell, value=None, h='right', bg=None):
        if bg: cell.fill = fill(bg)
        cell.font = font(size=9); cell.alignment = align(h, 'center'); cell.border = thin_border()
        if value is not None: cell.value = value

    # 2. Authorized amounts for Gasoline from catalogos.autorizaciones
    cur.execute('''
        SELECT referencia, litros_autorizados 
        FROM catalogos.autorizaciones 
        WHERE semana IN (29, 30) AND litros_autorizados > 0
    ''')
    auth_map = {}
    for r in cur.fetchall():
        ref = r['referencia'].strip()
        auth_map[ref] = float(r['litros_autorizados'])

    # 3. Query Week 30 Gasolina Consumos
    cond = "WHERE estatus_revision = 'APROBADO' AND (obra_destino IS NULL OR obra_destino NOT ILIKE '%Tanque Pegaso%') AND semana = '30'"

    cur.execute(f'''
        SELECT COALESCE(NULLIF(NULLIF(conductor,'nan'),''),'S/R') as resp,
               COALESCE(NULLIF(obra_destino,''), 'GENERAL / SIN OBRA') as obra_destino,
               SUM(litros) as litros
        FROM gasolina.consumos
        {cond}
        GROUP BY COALESCE(NULLIF(NULLIF(conductor,'nan'),''),'S/R'), COALESCE(NULLIF(obra_destino,''), 'GENERAL / SIN OBRA')
        ORDER BY resp, obra_destino
    ''')
    rows_pivot = cur.fetchall()

    cur.execute(f'''
        SELECT COALESCE(NULLIF(obra_destino,''), 'GENERAL / SIN OBRA') as obra,
               fecha::text as fecha_str,
               SUM(litros) as total_litros,
               AVG(costo_por_litro) as precio_prom,
               SUM(importe_total) as importe_total
        FROM gasolina.consumos
        {cond}
        GROUP BY COALESCE(NULLIF(obra_destino,''), 'GENERAL / SIN OBRA'), fecha::text
        ORDER BY obra, fecha::text
    ''')
    rows_diario = cur.fetchall()

    dias_worked = 7

    # Build Workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Semana 30'
    ws.sheet_view.showGridLines = False

    # Cols width
    for cl in ['A','B','C','D','E']: ws.column_dimensions[cl].width = 3
    T4_COLS = {'F': 24, 'G': 18, 'H': 18, 'I': 28, 'J': 18, 'K': 22, 'L': 22}
    for col_letter, width in T4_COLS.items(): ws.column_dimensions[col_letter].width = width

    # Title
    r = 2
    ws.merge_cells(f'F{r}:L{r}')
    tc = ws[f'F{r}']
    tc.value = 'CONSUMO SEMANA 30 (GASOLINA)'
    tc.fill = fill(COL_HDR_FILL); tc.font = font(bold=True, color=WHITE, size=12); tc.alignment = align('center', 'center'); tc.border = thin_border()

    r += 1
    hdrs4 = ['RESPONSABLE','AUTORIZADO DIARIO',f'SEMANAL ({dias_worked} DÍAS)','OBRA','CONSUMO POR OBRA','CONSUMO POR INGENIERO','REMANENTE POR INGENIERO']
    for i, hdr in enumerate(hdrs4):
        cell = ws[f'{chr(70+i)}{r}']
        style_hdr(cell, hdr)
    r += 1

    resp_obras = OrderedDict()
    for row in rows_pivot:
        resp = row['resp']
        resp_obras.setdefault(resp, {})
        obra_nom = row['obra_destino']
        resp_obras[resp][obra_nom] = float(row['litros'] or 0)

    # Build list of responsibles from actual Gasoline consumptions and authorizations
    all_resps = []
    for resp in sorted(resp_obras.keys()):
        if resp != 'S/R' and resp not in all_resps:
            all_resps.append(resp)

    tot_semanal = 0
    tot_consumo = 0
    tot_remanente = 0

    for resp in all_resps:
        obras_dict = resp_obras.get(resp, {})
        obras_sorted = sorted(obras_dict.keys()) if obras_dict else ['SIN CONSUMOS']
        con_ing = sum(obras_dict.values())
        
        # Matching autorizacion
        auto_dia = 0
        for k, v in auth_map.items():
            if k.upper() in resp.upper() or resp.upper() in k.upper():
                auto_dia = v
                break

        auto_sem = auto_dia * dias_worked
        remanente = auto_sem - con_ing
        tot_semanal += auto_sem
        tot_consumo += con_ing
        tot_remanente += remanente

        num_obras = len(obras_sorted)
        first = True
        for j, obra in enumerate(obras_sorted):
            con_obra = obras_dict.get(obra, 0)
            bg = COL_ALT1 if (all_resps.index(resp) % 2 == 0) else COL_ALT2

            fc = ws[f'F{r}']
            if first:
                style_ing(fc, resp.upper())
                if num_obras > 1: ws.merge_cells(f'F{r}:F{r+num_obras-1}')
            else:
                fc.fill = fill(COL_ING_FILL); fc.border = thin_border()

            gc = ws[f'G{r}']
            if first:
                style_data(gc, auto_dia if auto_dia else None, h='center', bg=bg)
                if num_obras > 1: ws.merge_cells(f'G{r}:G{r+num_obras-1}')
            else:
                gc.fill = fill(bg); gc.border = thin_border()

            hc = ws[f'H{r}']
            if first:
                style_data(hc, auto_sem if auto_sem else None, h='center', bg=bg)
                if num_obras > 1: ws.merge_cells(f'H{r}:H{r+num_obras-1}')
            else:
                hc.fill = fill(bg); hc.border = thin_border()

            ic = ws[f'I{r}']
            style_data(ic, obra, h='left' if obra != 'SIN CONSUMOS' else 'center', bg=bg)

            jc = ws[f'J{r}']
            style_data(jc, round(con_obra, 2) if con_obra else None, h='center', bg=bg)

            kc = ws[f'K{r}']
            if first:
                style_data(kc, round(con_ing, 2) if con_ing else None, h='center', bg=bg)
                kc.font = font(bold=True, size=9)
                if num_obras > 1: ws.merge_cells(f'K{r}:K{r+num_obras-1}')
            else:
                kc.fill = fill(bg); kc.border = thin_border()

            lc = ws[f'L{r}']
            if first:
                rem_bg = 'E6F4EA' if remanente >= 0 else 'FCE4E4'
                rem_fg = '166534' if remanente >= 0 else 'DC2626'
                lc.value = round(remanente, 2) if remanente != 0 else None
                lc.fill = fill(rem_bg); lc.font = font(bold=True, color=rem_fg, size=9)
                lc.alignment = align('center', 'center'); lc.border = thin_border()
                if num_obras > 1: ws.merge_cells(f'L{r}:L{r+num_obras-1}')
            else:
                lc.fill = fill(bg); lc.border = thin_border()

            ws.row_dimensions[r].height = 18
            r += 1
            first = False

    # Totals Row Tabla 1
    ws.merge_cells(f'F{r}:G{r}')
    tc = ws[f'F{r}']
    style_tot(tc, 'TOTALES:')
    ws[f'G{r}'].fill = fill(COL_TOT_FILL); ws[f'G{r}'].border = thin_border()
    style_tot(ws[f'H{r}'], round(tot_semanal, 2) if tot_semanal else '')
    ws[f'I{r}'].fill = fill(COL_TOT_FILL); ws[f'I{r}'].border = thin_border()
    style_tot(ws[f'J{r}'], round(tot_consumo, 2) if tot_consumo else '')
    style_tot(ws[f'K{r}'], round(tot_consumo, 2) if tot_consumo else '')
    style_tot(ws[f'L{r}'], round(tot_remanente, 2) if tot_remanente else '')
    ws.row_dimensions[r].height = 20
    r += 3

    # TABLA 2: RESUMEN DIARIO POR OBRA
    DIAS_ES_RD = {'Mon':'Lun','Tue':'Mar','Wed':'Mié','Thu':'Jue','Fri':'Vie','Sat':'Sáb','Sun':'Dom'}
    MESES_ES = {1:'ene',2:'feb',3:'mar',4:'abr',5:'may',6:'jun',7:'jul',8:'ago',9:'sep',10:'oct',11:'nov',12:'dic'}

    diario_por_obra = OrderedDict()
    for rd in rows_diario:
        ob = rd['obra']
        diario_por_obra.setdefault(ob, []).append(rd)

    ws.column_dimensions['F'].width = 18; ws.column_dimensions['G'].width = 18; ws.column_dimensions['H'].width = 16; ws.column_dimensions['I'].width = 18
    ws.column_dimensions['J'].width = 3
    ws.column_dimensions['K'].width = 18; ws.column_dimensions['L'].width = 18; ws.column_dimensions['M'].width = 16; ws.column_dimensions['N'].width = 18

    obras_items = list(diario_por_obra.items())

    for i in range(0, len(obras_items), 2):
        chunk = obras_items[i:i+2]
        r_start = r
        max_r = r
        
        for idx, (obra_nombre, obra_filas) in enumerate(chunk):
            col_offset = 6 if idx == 0 else 11
            curr_r = r_start
            
            ws.merge_cells(start_row=curr_r, start_column=col_offset, end_row=curr_r, end_column=col_offset+3)
            tc = ws.cell(row=curr_r, column=col_offset)
            tc.value = f'▶  {obra_nombre}'
            tc.fill = fill('1E3A5F'); tc.font = font(bold=True, color=WHITE, size=10); tc.alignment = align('left', 'center'); tc.border = thin_border()
            ws.row_dimensions[curr_r].height = 20
            curr_r += 1

            for c_idx, hdr_txt in enumerate(['DÍA', 'LITROS CONSUMIDOS', 'PRECIO PROM. ($/L)', 'IMPORTE TOTAL'], start=col_offset):
                c = ws.cell(row=curr_r, column=c_idx)
                style_hdr(c, hdr_txt)
            ws.row_dimensions[curr_r].height = 20
            curr_r += 1

            tot_lts_ob = 0
            tot_imp_ob = 0
            for rd_idx, rd in enumerate(obra_filas):
                rd_fecha = rd['fecha_str']
                rd_lts   = float(rd['total_litros'] or 0)
                rd_prec  = float(rd['precio_prom'] or 0)
                rd_imp   = float(rd['importe_total'] or 0)
                if rd_imp == 0 and rd_prec > 0: rd_imp = rd_lts * rd_prec
                tot_lts_ob += rd_lts
                tot_imp_ob += rd_imp

                bg_rd = COL_ALT1 if rd_idx % 2 == 0 else COL_ALT2

                try:
                    d_obj = dt_module.datetime.strptime(rd_fecha, '%Y-%m-%d')
                    dia_nom = DIAS_ES_RD.get(d_obj.strftime('%a'), d_obj.strftime('%a'))
                    mes_nom = MESES_ES.get(d_obj.month, str(d_obj.month))
                    fecha_label = f'{dia_nom} {d_obj.day:02d}-{mes_nom}'
                except:
                    fecha_label = rd_fecha

                c = ws.cell(row=curr_r, column=col_offset)
                c.value = fecha_label; c.fill = fill(bg_rd); c.font = font(bold=True, size=9); c.alignment = align('left', 'center'); c.border = thin_border()

                c = ws.cell(row=curr_r, column=col_offset+1)
                c.value = round(rd_lts, 3) if rd_lts else None; c.fill = fill(bg_rd); c.font = font(size=9); c.alignment = align('right', 'center'); c.border = thin_border(); c.number_format = '#,##0.000'

                c = ws.cell(row=curr_r, column=col_offset+2)
                c.value = round(rd_prec, 4) if rd_prec else None; c.fill = fill(bg_rd); c.font = font(size=9); c.alignment = align('right', 'center'); c.border = thin_border(); c.number_format = '"$"#,##0.0000'

                c = ws.cell(row=curr_r, column=col_offset+3)
                c.value = round(rd_imp, 2) if rd_imp else None; c.fill = fill(bg_rd); c.font = font(bold=True, size=9); c.alignment = align('right', 'center'); c.border = thin_border(); c.number_format = '"$"#,##0.00'

                ws.row_dimensions[curr_r].height = 18
                curr_r += 1

            c = ws.cell(row=curr_r, column=col_offset)
            c.value = f'TOTAL — {obra_nombre}'; c.fill = fill(COL_TOT_FILL); c.font = font(bold=True, color=WHITE, size=9); c.alignment = align('right', 'center'); c.border = thin_border()

            c = ws.cell(row=curr_r, column=col_offset+1)
            c.value = round(tot_lts_ob, 3) if tot_lts_ob else None; c.fill = fill(COL_TOT_FILL); c.font = font(bold=True, color=WHITE, size=9); c.alignment = align('right', 'center'); c.border = thin_border(); c.number_format = '#,##0.000'

            c = ws.cell(row=curr_r, column=col_offset+2)
            c.fill = fill(COL_TOT_FILL); c.border = thin_border()

            c = ws.cell(row=curr_r, column=col_offset+3)
            c.value = round(tot_imp_ob, 2) if tot_imp_ob else None; c.fill = fill(COL_TOT_FILL); c.font = font(bold=True, color=WHITE, size=9); c.alignment = align('right', 'center'); c.border = thin_border(); c.number_format = '"$"#,##0.00'
            ws.row_dimensions[curr_r].height = 20
            curr_r += 1

            if curr_r > max_r: max_r = curr_r
                
        r = max_r + 1

    output_filename = 'c:\\Users\\JOSE\\Desktop\\Reporte_Gasolina_Semana_30.xlsx'
    wb.save(output_filename)
    conn.close()
    print(f'=== Excel file saved successfully: {output_filename} ===')

if __name__ == '__main__':
    main()
