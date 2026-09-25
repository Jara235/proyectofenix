# -*- coding: utf-8 -*-
"""
Script de Consolidación y Conciliación de Tickets LEVET (Semanas 26 a 37)
- Extrae todas las transacciones de los 6 archivos en 'gasolina/conciliacion levet/'
- Deduplica inteligentemente resolviendo discrepancias y completando metadatos faltantes
- Genera libro Excel con pestañas por semana (listo para imprimir), resumen ejecutivo, base plana y auditoría de duplicados
- Genera PDF listo para impresión directa (1 semana por página)
"""

import os
import re
from datetime import datetime
from collections import defaultdict
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from reportlab.lib import pagesizes, colors
from reportlab.lib.pagesizes import letter, legal, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import ParagraphStyle

# Directorios
BASE_DIR = r'c:\Users\JOSE\Desktop\Proyecto fenix'
LEVET_DIR = os.path.join(BASE_DIR, 'gasolina', 'conciliacion levet')

def parse_and_extract_raw_records(folder):
    files = [f for f in os.listdir(folder) if f.endswith('.xlsx') and not f.startswith('~$') and not f.startswith('Conciliacion_')]
    
    valid_records = []
    ignored_rows = []
    
    for f in sorted(files):
        path = os.path.join(folder, f)
        wb = openpyxl.load_workbook(path, data_only=True)
        for sname in wb.sheetnames:
            ws = wb[sname]
            h_row = None
            col_map = {}
            for r in range(1, 15):
                row_vals = [str(ws.cell(r, c).value or '').strip().upper() for c in range(1, 15)]
                if any('TICKET' in v for v in row_vals):
                    h_row = r
                    for c in range(1, 15):
                        val = str(ws.cell(r, c).value or '').strip().upper()
                        if 'TICKET' in val: col_map['ticket'] = c
                        elif 'FECHA' in val: col_map['fecha'] = c
                        elif 'UNID' in val or 'PLACAS' in val: col_map['unidad'] = c
                        elif 'KILO' in val: col_map['km'] = c
                        elif 'CONDUCTOR' in val or 'RESPONSABLE' in val: col_map['conductor'] = c
                        elif 'OBRA' in val or 'CENTRO' in val: col_map['obra'] = c
                        elif 'LTS' in val or 'LITROS' in val: col_map['litros'] = c
                        elif 'PRECIO' in val: col_map['precio'] = c
                        elif 'IMPORTE' in val: col_map['importe'] = c
                    break
            
            if not h_row or 'ticket' not in col_map:
                continue
                
            for r in range(h_row + 1, ws.max_row + 1):
                tkt = ws.cell(r, col_map.get('ticket', 1)).value
                if tkt is None or str(tkt).strip() == '':
                    continue
                
                str_tkt = str(tkt).strip()
                # Excluir etiquetas de resúmenes contables
                if any(k in str_tkt.upper() for k in ['TOTAL', 'TRANSFERENCIA', 'FACTURA', 'X FACTURAR', 'SALDO', 'SUBTOTAL']):
                    ignored_rows.append({'file': f, 'sheet': sname, 'row': r, 'label': str_tkt})
                    continue
                
                dt = ws.cell(r, col_map.get('fecha', 2)).value
                unid = ws.cell(r, col_map.get('unidad', 3)).value
                km = ws.cell(r, col_map.get('km', 4)).value if 'km' in col_map else None
                cond = ws.cell(r, col_map.get('conductor', 5)).value if 'conductor' in col_map else None
                obra = ws.cell(r, col_map.get('obra', 6)).value if 'obra' in col_map else None
                lts = ws.cell(r, col_map.get('litros', 7)).value if 'litros' in col_map else None
                precio = ws.cell(r, col_map.get('precio', 8)).value if 'precio' in col_map else None
                imp = ws.cell(r, col_map.get('importe', 9)).value if 'importe' in col_map else None
                
                dt_clean = None
                if isinstance(dt, datetime):
                    dt_clean = dt.date()
                elif isinstance(dt, str):
                    try:
                        dt_clean = datetime.strptime(dt.strip()[:10], '%Y-%m-%d').date()
                    except:
                        pass
                
                # Conversión de números
                try:
                    lts_val = float(lts) if lts is not None and str(lts).strip() != '' else 0.0
                except:
                    lts_val = 0.0
                    
                try:
                    precio_val = float(precio) if precio is not None and str(precio).strip() != '' else 0.0
                except:
                    precio_val = 0.0
                    
                try:
                    imp_val = float(imp) if imp is not None and str(imp).strip() != '' else 0.0
                except:
                    imp_val = 0.0
                    
                valid_records.append({
                    'file': f,
                    'sheet': sname,
                    'row': r,
                    'ticket': str_tkt,
                    'fecha': dt_clean,
                    'fecha_raw': dt,
                    'unidad': str(unid or '').strip(),
                    'km': str(km or '').strip(),
                    'conductor': str(cond or '').strip(),
                    'obra': str(obra or '').strip(),
                    'litros': round(lts_val, 3),
                    'precio': round(precio_val, 2),
                    'importe': round(imp_val, 2)
                })
                
    return valid_records, ignored_rows

def deduplicate_records(raw_records):
    # Agrupar por clave única: (ticket, importe) para conservar casos legítimos donde un mismo ticket tenga 2 cargas distintas
    groups = defaultdict(list)
    for r in raw_records:
        key = (r['ticket'], r['importe'])
        groups[key].append(r)
        
    consolidated = []
    audit_duplicates = []
    
    for key, rec_list in groups.items():
        tkt, imp = key
        
        # Coalescer la mejor información disponible
        best_fecha = None
        best_unidad = ''
        best_km = ''
        best_conductor = ''
        best_obra = ''
        best_litros = 0.0
        best_precio = 0.0
        
        for r in rec_list:
            if r['fecha'] and not best_fecha:
                best_fecha = r['fecha']
            if r['unidad'] and (not best_unidad or len(r['unidad']) > len(best_unidad)):
                best_unidad = r['unidad']
            if r['km'] and (not best_km or len(r['km']) > len(best_km)):
                best_km = r['km']
            if r['conductor'] and (not best_conductor or len(r['conductor']) > len(best_conductor)):
                best_conductor = r['conductor']
            if r['obra'] and (not best_obra or len(r['obra']) > len(best_obra)):
                best_obra = r['obra']
            if r['litros'] > 0 and best_litros == 0:
                best_litros = r['litros']
            if r['precio'] > 0 and best_precio == 0:
                best_precio = r['precio']
                
        # Si precio o litros faltan, calcularlo
        if best_litros > 0 and best_precio > 0 and imp == 0:
            imp = round(best_litros * best_precio, 2)
        elif best_litros > 0 and imp > 0 and best_precio == 0:
            best_precio = round(imp / best_litros, 2)
        elif best_precio > 0 and imp > 0 and best_litros == 0:
            best_litros = round(imp / best_precio, 3)
            
        # Calcular semana ISO
        if best_fecha:
            iso_year, iso_week, iso_day = best_fecha.isocalendar()
            semana_num = iso_week
        else:
            semana_num = 0
            
        sources = [f"{x['file']} [{x['sheet']} R{x['row']}]" for x in rec_list]
        
        unified_record = {
            'ticket': tkt,
            'fecha': best_fecha,
            'semana': semana_num,
            'unidad': best_unidad,
            'km': best_km,
            'conductor': best_conductor,
            'obra': best_obra,
            'litros': best_litros,
            'precio': best_precio,
            'importe': imp,
            'proveedor': 'LEVET',
            'repeticiones': len(rec_list),
            'origenes': ' | '.join(sources)
        }
        consolidated.append(unified_record)
        
        if len(rec_list) > 1:
            audit_duplicates.append({
                'ticket': tkt,
                'importe': imp,
                'repeticiones': len(rec_list),
                'origenes': ' | '.join(sources),
                'unidad': best_unidad,
                'conductor': best_conductor,
                'fecha': str(best_fecha)
            })
            
    # Ordenar cronológicamente por fecha, semana y ticket
    consolidated.sort(key=lambda x: (x['semana'], x['fecha'] or datetime.min.date(), x['ticket']))
    return consolidated, audit_duplicates

def generate_excel_consolidation(consolidated_records, audit_duplicates, output_path):
    wb = openpyxl.Workbook()
    # Eliminar hoja default
    default_sheet = wb.active
    
    # Estilos
    f_title = Font(name='Calibri', size=13, bold=True, color='FFFFFF')
    f_subtitle = Font(name='Calibri', size=10, bold=True, color='333333')
    f_header = Font(name='Calibri', size=9, bold=True, color='FFFFFF')
    f_data = Font(name='Calibri', size=8.5, color='000000')
    f_total = Font(name='Calibri', size=9, bold=True, color='000000')
    
    fill_blue_title = PatternFill(start_color='1F4E79', end_color='1F4E79', fill_type='solid') # Azul corporativo
    fill_header = PatternFill(start_color='2E75B6', end_color='2E75B6', fill_type='solid')     # Azul medio
    fill_header_green = PatternFill(start_color='375623', end_color='375623', fill_type='solid') # Verde
    fill_zebra = PatternFill(start_color='F2F5F9', end_color='F2F5F9', fill_type='solid')     # Celeste muy suave
    fill_total = PatternFill(start_color='D9E1F2', end_color='D9E1F2', fill_type='solid')     # Azul claro total
    fill_peach = PatternFill(start_color='FCE4D6', end_color='FCE4D6', fill_type='solid')     # Melocotón
    
    thin_side = Side(border_style='thin', color='B0C4DE')
    double_side = Side(border_style='double', color='000000')
    thick_bottom = Side(border_style='medium', color='1F4E79')
    
    border_cell = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)
    border_total = Border(left=thin_side, right=thin_side, top=thin_side, bottom=double_side)
    
    align_center = Alignment(horizontal='center', vertical='center')
    align_left = Alignment(horizontal='left', vertical='center')
    align_right = Alignment(horizontal='right', vertical='center')
    align_header = Alignment(horizontal='center', vertical='center', wrap_text=True)

    # 1. HOJA RESUMEN EJECUTIVO
    ws_resumen = wb.create_sheet(title='Resumen Ejecutivo')
    ws_resumen.views.sheetView[0].showGridLines = True
    
    ws_resumen.merge_cells('A1:G1')
    ws_resumen['A1'] = "CONCILIACIÓN Y CONTROL DE TICKETS DE GASOLINA LEVET - 2026"
    ws_resumen['A1'].font = f_title
    ws_resumen['A1'].fill = fill_blue_title
    ws_resumen['A1'].alignment = align_center
    ws_resumen.row_dimensions[1].height = 28
    
    ws_resumen.merge_cells('A2:G2')
    ws_resumen['A2'] = "RESUMEN SEMANAL CONSOLIDADO (SEM. 26 A 37)"
    ws_resumen['A2'].font = Font(name='Calibri', size=10, bold=True, color='1F4E79')
    ws_resumen['A2'].alignment = align_center
    ws_resumen.row_dimensions[2].height = 18
    
    res_headers = ['SEMANA', 'FECHA INICIO', 'FECHA FIN', 'TOTAL TICKETS', 'TOTAL LITROS', 'PRECIO PROM.', 'IMPORTE TOTAL']
    for c_idx, h in enumerate(res_headers, 1):
        cell = ws_resumen.cell(3, c_idx, h)
        cell.font = f_header
        cell.fill = fill_header
        cell.alignment = align_header
        cell.border = border_cell
    ws_resumen.row_dimensions[3].height = 22
    
    # Agrupar por semanas
    weeks_dict = defaultdict(list)
    for r in consolidated_records:
        weeks_dict[r['semana']].append(r)
        
    r_idx = 4
    for wk in sorted(weeks_dict.keys()):
        w_recs = weeks_dict[wk]
        d_min = min(x['fecha'] for x in w_recs if x['fecha']) if any(x['fecha'] for x in w_recs) else ''
        d_max = max(x['fecha'] for x in w_recs if x['fecha']) if any(x['fecha'] for x in w_recs) else ''
        tot_tkts = len(w_recs)
        tot_lts = sum(x['litros'] for x in w_recs)
        tot_imp = sum(x['importe'] for x in w_recs)
        avg_precio = tot_imp / tot_lts if tot_lts > 0 else 0.0
        
        row_data = [
            f"Semana {wk:02d}",
            d_min.strftime('%d/%m/%Y') if d_min else '-',
            d_max.strftime('%d/%m/%Y') if d_max else '-',
            tot_tkts,
            tot_lts,
            avg_precio,
            tot_imp
        ]
        
        for c_idx, val in enumerate(row_data, 1):
            cell = ws_resumen.cell(r_idx, c_idx, val)
            cell.font = f_data
            cell.border = border_cell
            if (r_idx - 4) % 2 == 1:
                cell.fill = fill_zebra
                
            if c_idx in [1, 2, 3]:
                cell.alignment = align_center
            elif c_idx == 4:
                cell.alignment = align_center
                cell.number_format = '#,##0'
            elif c_idx == 5:
                cell.alignment = align_right
                cell.number_format = '#,##0.00 "Lts"'
            elif c_idx == 6:
                cell.alignment = align_right
                cell.number_format = '"$"#,##0.00'
            elif c_idx == 7:
                cell.alignment = align_right
                cell.number_format = '"$"#,##0.00'
                
        ws_resumen.row_dimensions[r_idx].height = 18
        r_idx += 1
        
    # Totales Resumen
    ws_resumen.cell(r_idx, 1, "GRAN TOTAL").font = f_total
    ws_resumen.cell(r_idx, 1).alignment = align_center
    ws_resumen.cell(r_idx, 1).fill = fill_total
    ws_resumen.cell(r_idx, 1).border = border_total
    
    ws_resumen.merge_cells(start_row=r_idx, start_column=1, end_row=r_idx, end_column=3)
    
    cell_tkts = ws_resumen.cell(r_idx, 4, f"=SUM(D4:D{r_idx-1})")
    cell_tkts.font = f_total
    cell_tkts.alignment = align_center
    cell_tkts.number_format = '#,##0'
    cell_tkts.fill = fill_total
    cell_tkts.border = border_total
    
    cell_lts = ws_resumen.cell(r_idx, 5, f"=SUM(E4:E{r_idx-1})")
    cell_lts.font = f_total
    cell_lts.alignment = align_right
    cell_lts.number_format = '#,##0.00 "Lts"'
    cell_lts.fill = fill_total
    cell_lts.border = border_total
    
    cell_p = ws_resumen.cell(r_idx, 6, f"=G{r_idx}/E{r_idx}")
    cell_p.font = f_total
    cell_p.alignment = align_right
    cell_p.number_format = '"$"#,##0.00'
    cell_p.fill = fill_total
    cell_p.border = border_total
    
    cell_imp = ws_resumen.cell(r_idx, 7, f"=SUM(G4:G{r_idx-1})")
    cell_imp.font = f_total
    cell_imp.alignment = align_right
    cell_imp.number_format = '"$"#,##0.00'
    cell_imp.fill = fill_total
    cell_imp.border = border_total
    ws_resumen.row_dimensions[r_idx].height = 20
    
    # Anchos columnas resumen
    res_widths = [14, 15, 15, 16, 18, 16, 20]
    for c_i, w in enumerate(res_widths, 1):
        ws_resumen.column_dimensions[get_column_letter(c_i)].width = w

    # 2. PESTAÑAS SEMANALES (Semana 26 a Semana 37)
    dias_semana_es = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    
    for wk in sorted(weeks_dict.keys()):
        sheet_title = f"Semana {wk:02d}"
        ws = wb.create_sheet(title=sheet_title)
        ws.views.sheetView[0].showGridLines = True
        
        # Configuración de página para impresión
        ws.page_setup.orientation = ws.ORIENTATION_LANDSCAPE
        ws.page_setup.paperSize = ws.PAPERSIZE_LETTER
        ws.page_setup.fitToPage = True
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 0
        ws.sheet_properties.pageSetUpPr.fitToPage = True
        ws.print_title_rows = '1:3' # Repetir encabezados al imprimir
        
        w_recs = weeks_dict[wk]
        d_min = min(x['fecha'] for x in w_recs if x['fecha']) if any(x['fecha'] for x in w_recs) else None
        d_max = max(x['fecha'] for x in w_recs if x['fecha']) if any(x['fecha'] for x in w_recs) else None
        
        date_range_str = f"Del {d_min.strftime('%d/%m/%Y')} al {d_max.strftime('%d/%m/%Y')}" if d_min else ''
        
        # Título
        ws.merge_cells('A1:J1')
        ws['A1'] = f"CONTROL Y CONCILIACIÓN DE COMBUSTIBLE - LEVET ({sheet_title.upper()})"
        ws['A1'].font = f_title
        ws['A1'].fill = fill_blue_title
        ws['A1'].alignment = align_center
        ws.row_dimensions[1].height = 24
        
        ws.merge_cells('A2:J2')
        ws['A2'] = f"PERÍODO: {date_range_str.upper()} | TOTAL TRANSACCIONES: {len(w_recs)}"
        ws['A2'].font = Font(name='Calibri', size=9.5, bold=True, color='1F4E79')
        ws['A2'].alignment = align_center
        ws.row_dimensions[2].height = 16
        
        headers = ['NO.', 'TICKET', 'FECHA', 'DÍA', 'UNIDAD / PLACAS', 'CONDUCTOR / RESPONSABLE', 'OBRA / DESTINO', 'LTS. COMBUST.', 'PRECIO', 'IMPORTE ($)']
        for c_idx, h in enumerate(headers, 1):
            cell = ws.cell(3, c_idx, h)
            cell.font = f_header
            cell.fill = fill_header
            cell.alignment = align_header
            cell.border = border_cell
        ws.row_dimensions[3].height = 20
        
        r_start = 4
        for idx, rec in enumerate(w_recs, 1):
            curr_r = r_start + idx - 1
            dt_obj = rec['fecha']
            dia_str = dias_semana_es[dt_obj.weekday()] if dt_obj else ''
            
            row_vals = [
                idx,
                rec['ticket'],
                dt_obj.strftime('%d/%m/%Y') if dt_obj else '',
                dia_str,
                rec['unidad'],
                rec['conductor'],
                rec['obra'],
                rec['litros'],
                rec['precio'],
                rec['importe']
            ]
            
            for c_idx, val in enumerate(row_vals, 1):
                cell = ws.cell(curr_r, c_idx, val)
                cell.font = f_data
                cell.border = border_cell
                if (idx % 2) == 0:
                    cell.fill = fill_zebra
                    
                if c_idx in [1, 2, 3, 4]:
                    cell.alignment = align_center
                elif c_idx in [5, 6, 7]:
                    cell.alignment = align_left
                elif c_idx == 8:
                    cell.alignment = align_right
                    cell.number_format = '#,##0.00'
                elif c_idx == 9:
                    cell.alignment = align_right
                    cell.number_format = '"$"#,##0.00'
                elif c_idx == 10:
                    cell.alignment = align_right
                    cell.number_format = '"$"#,##0.00'
                    
            ws.row_dimensions[curr_r].height = 16
            
        # Fila de Totales de la Semana
        tot_r = r_start + len(w_recs)
        ws.merge_cells(start_row=tot_r, start_column=1, end_row=tot_r, end_column=7)
        cell_lbl = ws.cell(tot_r, 1, f"TOTAL {sheet_title.upper()}")
        cell_lbl.font = f_total
        cell_lbl.alignment = Alignment(horizontal='right', vertical='center')
        cell_lbl.fill = fill_peach
        cell_lbl.border = border_total
        
        for c in range(2, 8):
            ws.cell(tot_r, c).fill = fill_peach
            ws.cell(tot_r, c).border = border_total
            
        # Formula suma litros
        cell_l = ws.cell(tot_r, 8, f"=SUM(H{r_start}:H{tot_r-1})")
        cell_l.font = f_total
        cell_l.alignment = align_right
        cell_l.number_format = '#,##0.00'
        cell_l.fill = fill_peach
        cell_l.border = border_total
        
        # Precio promedio ponderado
        cell_p = ws.cell(tot_r, 9, f"=J{tot_r}/H{tot_r}")
        cell_p.font = f_total
        cell_p.alignment = align_right
        cell_p.number_format = '"$"#,##0.00'
        cell_p.fill = fill_peach
        cell_p.border = border_total
        
        # Formula suma importe
        cell_i = ws.cell(tot_r, 10, f"=SUM(J{r_start}:J{tot_r-1})")
        cell_i.font = f_total
        cell_i.alignment = align_right
        cell_i.number_format = '"$"#,##0.00'
        cell_i.fill = fill_peach
        cell_i.border = border_total
        ws.row_dimensions[tot_r].height = 20
        
        # Ajustar anchos
        col_w = [5, 11, 12, 11, 16, 26, 32, 13, 10, 14]
        for c_i, w in enumerate(col_w, 1):
            ws.column_dimensions[get_column_letter(c_i)].width = w

    # 3. BASE GENERAL (480 TICKETS)
    ws_base = wb.create_sheet(title='Base General (480 Tickets)')
    ws_base.views.sheetView[0].showGridLines = True
    
    ws_base.merge_cells('A1:L1')
    ws_base['A1'] = "BASE MAESTRA CONSOLIDADA DE TICKETS DE COMBUSTIBLE (LEVET)"
    ws_base['A1'].font = f_title
    ws_base['A1'].fill = fill_blue_title
    ws_base['A1'].alignment = align_center
    ws_base.row_dimensions[1].height = 24
    
    base_headers = ['NO.', 'SEMANA', 'TICKET', 'FECHA', 'DÍA', 'UNIDAD / PLACAS', 'CONDUCTOR', 'OBRA / DESTINO', 'LITROS', 'PRECIO', 'IMPORTE ($)', 'ARCHIVOS ORIGEN']
    for c_idx, h in enumerate(base_headers, 1):
        cell = ws_base.cell(2, c_idx, h)
        cell.font = f_header
        cell.fill = fill_header
        cell.alignment = align_header
        cell.border = border_cell
    ws_base.row_dimensions[2].height = 20
    
    for idx, rec in enumerate(consolidated_records, 1):
        curr_r = 2 + idx
        dt_obj = rec['fecha']
        dia_str = dias_semana_es[dt_obj.weekday()] if dt_obj else ''
        
        row_vals = [
            idx,
            f"Semana {rec['semana']:02d}",
            rec['ticket'],
            dt_obj.strftime('%d/%m/%Y') if dt_obj else '',
            dia_str,
            rec['unidad'],
            rec['conductor'],
            rec['obra'],
            rec['litros'],
            rec['precio'],
            rec['importe'],
            rec['origenes']
        ]
        
        for c_idx, val in enumerate(row_vals, 1):
            cell = ws_base.cell(curr_r, c_idx, val)
            cell.font = f_data
            cell.border = border_cell
            if (idx % 2) == 0:
                cell.fill = fill_zebra
                
            if c_idx in [1, 2, 3, 4, 5]:
                cell.alignment = align_center
            elif c_idx in [6, 7, 8, 12]:
                cell.alignment = align_left
            elif c_idx == 9:
                cell.alignment = align_right
                cell.number_format = '#,##0.00'
            elif c_idx == 10:
                cell.alignment = align_right
                cell.number_format = '"$"#,##0.00'
            elif c_idx == 11:
                cell.alignment = align_right
                cell.number_format = '"$"#,##0.00'
                
        ws_base.row_dimensions[curr_r].height = 16
        
    # Totales Base General
    tot_base_r = 3 + len(consolidated_records)
    ws_base.merge_cells(start_row=tot_base_r, start_column=1, end_row=tot_base_r, end_column=8)
    cell_lbl_b = ws_base.cell(tot_base_r, 1, "TOTAL GENERAL")
    cell_lbl_b.font = f_total
    cell_lbl_b.alignment = Alignment(horizontal='right', vertical='center')
    cell_lbl_b.fill = fill_total
    cell_lbl_b.border = border_total
    
    for c in range(2, 9):
        ws_base.cell(tot_base_r, c).fill = fill_total
        ws_base.cell(tot_base_r, c).border = border_total
        
    cell_l_b = ws_base.cell(tot_base_r, 9, f"=SUM(I3:I{tot_base_r-1})")
    cell_l_b.font = f_total
    cell_l_b.alignment = align_right
    cell_l_b.number_format = '#,##0.00'
    cell_l_b.fill = fill_total
    cell_l_b.border = border_total
    
    cell_p_b = ws_base.cell(tot_base_r, 10, f"=K{tot_base_r}/I{tot_base_r}")
    cell_p_b.font = f_total
    cell_p_b.alignment = align_right
    cell_p_b.number_format = '"$"#,##0.00'
    cell_p_b.fill = fill_total
    cell_p_b.border = border_total
    
    cell_i_b = ws_base.cell(tot_base_r, 11, f"=SUM(K3:K{tot_base_r-1})")
    cell_i_b.font = f_total
    cell_i_b.alignment = align_right
    cell_i_b.number_format = '"$"#,##0.00'
    cell_i_b.fill = fill_total
    cell_i_b.border = border_total
    
    ws_base.cell(tot_base_r, 12).fill = fill_total
    ws_base.cell(tot_base_r, 12).border = border_total
    ws_base.row_dimensions[tot_base_r].height = 20
    
    base_w = [5, 12, 11, 12, 11, 16, 26, 30, 13, 10, 14, 45]
    for c_i, w in enumerate(base_w, 1):
        ws_base.column_dimensions[get_column_letter(c_i)].width = w

    # 4. AUDITORÍA DE DUPLICADOS
    ws_dup = wb.create_sheet(title='Auditoría de Duplicados')
    ws_dup.views.sheetView[0].showGridLines = True
    
    ws_dup.merge_cells('A1:F1')
    ws_dup['A1'] = f"AUDITORÍA DE DUPLICADOS ({len(audit_duplicates)} TICKETS REPETIDOS RESUELTOS)"
    ws_dup['A1'].font = f_title
    ws_dup['A1'].fill = fill_header_green
    ws_dup['A1'].alignment = align_center
    ws_dup.row_dimensions[1].height = 24
    
    dup_headers = ['NO.', 'TICKET', 'FECHA', 'CONDUCTOR / UNIDAD', 'IMPORTE', 'VECES REPETIDO Y ARCHIVOS ORIGEN']
    for c_idx, h in enumerate(dup_headers, 1):
        cell = ws_dup.cell(2, c_idx, h)
        cell.font = f_header
        cell.fill = fill_header_green
        cell.alignment = align_header
        cell.border = border_cell
    ws_dup.row_dimensions[2].height = 20
    
    for idx, d_rec in enumerate(audit_duplicates, 1):
        curr_r = 2 + idx
        row_vals = [
            idx,
            d_rec['ticket'],
            d_rec['fecha'],
            f"{d_rec['conductor']} ({d_rec['unidad']})",
            d_rec['importe'],
            f"Repetido {d_rec['repeticiones']} veces en: {d_rec['origenes']}"
        ]
        
        for c_idx, val in enumerate(row_vals, 1):
            cell = ws_dup.cell(curr_r, c_idx, val)
            cell.font = f_data
            cell.border = border_cell
            if (idx % 2) == 0:
                cell.fill = fill_zebra
                
            if c_idx in [1, 2, 3]:
                cell.alignment = align_center
            elif c_idx in [4, 6]:
                cell.alignment = align_left
            elif c_idx == 5:
                cell.alignment = align_right
                cell.number_format = '"$"#,##0.00'
                
        ws_dup.row_dimensions[curr_r].height = 16
        
    dup_w = [5, 12, 12, 30, 14, 70]
    for c_i, w in enumerate(dup_w, 1):
        ws_dup.column_dimensions[get_column_letter(c_i)].width = w

    # Eliminar la hoja vacía por defecto
    if default_sheet.title in wb.sheetnames:
        wb.remove(default_sheet)
        
    wb.save(output_path)
    print(f"Excel guardado exitosamente en: {output_path}")

def generate_pdf_consolidation(consolidated_records, output_path):
    # Generar PDF en tamaño Carta Landscape (Letter Landscape: 792 x 612 pt)
    # Margen izquierdo/derecho: 18 pt, Margen superior/inferior: 16 pt
    # Ancho disponible: 756 pt, Alto disponible: 580 pt
    
    doc = SimpleDocTemplate(
        output_path,
        pagesize=landscape(letter),
        leftMargin=18,
        rightMargin=18,
        topMargin=16,
        bottomMargin=16
    )
    
    C_BLUE_TITLE = colors.HexColor('#1F4E79')
    C_BLUE_HEAD = colors.HexColor('#2E75B6')
    C_PEACH_TOT = colors.HexColor('#FCE4D6')
    C_BORDER = colors.HexColor('#B0C4DE')
    C_ZEBRA = colors.HexColor('#F4F7FB')
    
    style_title = ParagraphStyle('PDFTitle', fontName='Helvetica-Bold', fontSize=8.5, leading=10.0, alignment=1, textColor=colors.white)
    style_subtitle = ParagraphStyle('PDFSubTitle', fontName='Helvetica-Bold', fontSize=6.5, leading=8.0, alignment=1, textColor=C_BLUE_TITLE)
    style_head = ParagraphStyle('PDFHead', fontName='Helvetica-Bold', fontSize=5.5, leading=6.5, alignment=1, textColor=colors.white)
    style_cell_center = ParagraphStyle('PDFCCenter', fontName='Helvetica', fontSize=5.2, leading=6.2, alignment=1, textColor=colors.black)
    style_cell_left = ParagraphStyle('PDFCLeft', fontName='Helvetica', fontSize=5.2, leading=6.2, alignment=0, textColor=colors.black)
    style_cell_right = ParagraphStyle('PDFCRight', fontName='Helvetica', fontSize=5.2, leading=6.2, alignment=2, textColor=colors.black)
    style_tot_label = ParagraphStyle('PDFTotLbl', fontName='Helvetica-Bold', fontSize=5.8, leading=6.8, alignment=2, textColor=colors.black)
    style_tot_val = ParagraphStyle('PDFTotVal', fontName='Helvetica-Bold', fontSize=5.8, leading=6.8, alignment=2, textColor=colors.black)

    # Agrupar por semanas
    weeks_dict = defaultdict(list)
    for r in consolidated_records:
        weeks_dict[r['semana']].append(r)
        
    dias_semana_es = ['LUN', 'MAR', 'MIÉ', 'JUE', 'VIE', 'SÁB', 'DOM']
    col_widths = [16, 42, 42, 28, 62, 110, 140, 52, 40, 56] # Total = 588 pt (en 756 pt disponible, se expande proporcionalmente a 756 pt)
    # Factor de escala para llenar exactamente 756 pt
    scale_factor = 756.0 / sum(col_widths)
    scaled_widths = [w * scale_factor for w in col_widths]
    
    story = []
    
    sorted_weeks = sorted(weeks_dict.keys())
    for w_idx, wk in enumerate(sorted_weeks):
        w_recs = weeks_dict[wk]
        d_min = min(x['fecha'] for x in w_recs if x['fecha']) if any(x['fecha'] for x in w_recs) else None
        d_max = max(x['fecha'] for x in w_recs if x['fecha']) if any(x['fecha'] for x in w_recs) else None
        date_range_str = f"DEL {d_min.strftime('%d/%m/%Y')} AL {d_max.strftime('%d/%m/%Y')}" if d_min else ''
        
        # Matrix de tabla
        table_matrix = []
        
        # Fila 1: Título principal
        title_text = f"CONCILIACIÓN DE COMBUSTIBLE LEVET - SEMANA {wk:02d}"
        table_matrix.append([Paragraph(title_text, style_title)] + [''] * 9)
        
        # Fila 2: Subtítulo con período
        sub_text = f"PERÍODO: {date_range_str} | TOTAL TICKETS: {len(w_recs)}"
        table_matrix.append([Paragraph(sub_text, style_subtitle)] + [''] * 9)
        
        # Fila 3: Encabezados de columnas
        h_row = [
            Paragraph('NO.', style_head),
            Paragraph('TICKET', style_head),
            Paragraph('FECHA', style_head),
            Paragraph('DÍA', style_head),
            Paragraph('UNIDAD / PLACAS', style_head),
            Paragraph('CONDUCTOR / RESPONSABLE', style_head),
            Paragraph('OBRA / DESTINO', style_head),
            Paragraph('LTS. COMBUST.', style_head),
            Paragraph('PRECIO', style_head),
            Paragraph('IMPORTE', style_head)
        ]
        table_matrix.append(h_row)
        
        # Filas de datos
        for idx, rec in enumerate(w_recs, 1):
            dt_obj = rec['fecha']
            dia_str = dias_semana_es[dt_obj.weekday()] if dt_obj else ''
            
            row_cells = [
                Paragraph(str(idx), style_cell_center),
                Paragraph(str(rec['ticket']), style_cell_center),
                Paragraph(dt_obj.strftime('%d/%m/%Y') if dt_obj else '-', style_cell_center),
                Paragraph(dia_str, style_cell_center),
                Paragraph(rec['unidad'][:16], style_cell_left),
                Paragraph(rec['conductor'][:28], style_cell_left),
                Paragraph(rec['obra'][:35], style_cell_left),
                Paragraph(f"{rec['litros']:,.2f}", style_cell_right),
                Paragraph(f"${rec['precio']:,.2f}", style_cell_right),
                Paragraph(f"${rec['importe']:,.2f}", style_cell_right)
            ]
            table_matrix.append(row_cells)
            
        # Fila de Totales
        tot_lts = sum(x['litros'] for x in w_recs)
        tot_imp = sum(x['importe'] for x in w_recs)
        avg_precio = tot_imp / tot_lts if tot_lts > 0 else 0.0
        
        tot_cells = [
            Paragraph(f"TOTAL SEMANA {wk:02d}", style_tot_label),
            '', '', '', '', '', '',
            Paragraph(f"{tot_lts:,.2f}", style_tot_val),
            Paragraph(f"${avg_precio:,.2f}", style_tot_val),
            Paragraph(f"${tot_imp:,.2f}", style_tot_val)
        ]
        table_matrix.append(tot_cells)
        
        tot_row_idx = len(table_matrix) - 1
        
        # Estilos de tabla
        t_spans = [
            ('SPAN', (0, 0), (-1, 0)),
            ('SPAN', (0, 1), (-1, 1)),
            ('SPAN', (0, tot_row_idx), (6, tot_row_idx)),
        ]
        
        num_data_rows = len(w_recs)
        # Altura dinámica: si hay muchas filas (ej. 45), fila de 8.8pt; si hay menos, 9.8pt
        data_row_h = 8.6 if num_data_rows > 40 else 9.6
        row_heights = [15.0, 11.0, 11.0] + [data_row_h] * num_data_rows + [13.0]
        
        t_style = [
            ('BACKGROUND', (0, 0), (-1, 0), C_BLUE_TITLE),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#EBF1F5')),
            ('BACKGROUND', (0, 2), (-1, 2), C_BLUE_HEAD),
            ('BACKGROUND', (0, tot_row_idx), (-1, tot_row_idx), C_PEACH_TOT),
            
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.3, C_BORDER),
            ('LINEBELOW', (0, tot_row_idx), (-1, tot_row_idx), 0.8, colors.black),
            
            ('TOPPADDING', (0, 0), (-1, -1), 0.4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0.4),
            ('LEFTPADDING', (0, 0), (-1, -1), 1.0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 1.0),
        ] + t_spans
        
        for r_i in range(3, tot_row_idx):
            if (r_i - 3) % 2 == 1:
                t_style.append(('BACKGROUND', (0, r_i), (-1, r_i), C_ZEBRA))
                
        table = Table(table_matrix, colWidths=scaled_widths, rowHeights=row_heights)
        table.setStyle(TableStyle(t_style))
        story.append(table)
        
        if w_idx < len(sorted_weeks) - 1:
            story.append(PageBreak())
            
    doc.build(story)
    print(f"PDF guardado exitosamente en: {output_path}")

if __name__ == '__main__':
    print("Iniciando consolidación de archivos LEVET...")
    raw_recs, ignored = parse_and_extract_raw_records(LEVET_DIR)
    print(f"Registros brutos extraídos: {len(raw_recs)}")
    print(f"Filas de resúmenes contables ignoradas: {len(ignored)}")
    
    consolidated, duplicates = deduplicate_records(raw_recs)
    print(f"Tickets únicos consolidados: {len(consolidated)}")
    print(f"Casos de duplicidad resueltos: {len(duplicates)}")
    
    # Destinos de archivo
    excel_levet = os.path.join(LEVET_DIR, 'Conciliacion_Tickets_Levet_Semanas_26_a_37.xlsx')
    excel_root = os.path.join(BASE_DIR, 'Conciliacion_Tickets_Levet_Semanas_26_a_37.xlsx')
    
    pdf_levet = os.path.join(LEVET_DIR, 'Conciliacion_Tickets_Levet_Semanas_26_a_37.pdf')
    pdf_root = os.path.join(BASE_DIR, 'Conciliacion_Tickets_Levet_Semanas_26_a_37.pdf')
    
    print("Generando archivo Excel consolidado...")
    generate_excel_consolidation(consolidated, duplicates, excel_levet)
    generate_excel_consolidation(consolidated, duplicates, excel_root)
    
    print("Generando archivo PDF consolidado para impresión...")
    generate_pdf_consolidation(consolidated, pdf_levet)
    generate_pdf_consolidation(consolidated, pdf_root)
    
    print("¡Consolidación y reportes generados con éxito!")
