import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

def style_headers(ws):
    header_font = Font(bold=True, color='FFFFFF')
    header_fill = PatternFill(start_color='1F4E78', end_color='1F4E78', fill_type='solid')
    align = Alignment(horizontal='center', vertical='center')
    for cell in ws[1]:
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = align
        ws.column_dimensions[cell.column_letter].width = 20

def create_gasolina():
    wb = openpyxl.Workbook()
    ws_cat = wb.active
    ws_cat.title = 'CATALOGOS'
    ws_cat.append(['OBRAS', 'CODIGO_OBRA', 'RESPONSABLE', 'VEHICULOS', 'PLACA', 'CONDUCTORES', 'TIPO_MOVIMIENTO', 'ORIGEN'])
    
    ws_aut = wb.create_sheet('BD_AUTORIZACIONES')
    ws_aut.append(['FOLIO_CONCILIACION', 'FECHA', 'SEMANA', 'ORIGEN', 'OBRA_DESTINO', 'VEHICULO', 'PLACA', 'LITROS_AUTORIZADOS', 'IMPORTE_AUTORIZADO', 'RESPONSABLE', 'ESTATUS_AUTORIZACION', 'OBSERVACIONES'])
    
    ws_mov = wb.create_sheet('BD_GASOLINA')
    ws_mov.append(['FOLIO_CONCILIACION', 'FECHA', 'SEMANA', 'ORIGEN', 'TIPO_MOVIMIENTO', 'OBRA_DESTINO', 'VEHICULO', 'PLACA', 'KILOMETRAJE', 'LITROS', 'COSTO_POR_LITRO', 'IMPORTE_TOTAL', 'CONDUCTOR', 'ESTATUS_CONCILIACION', 'OBSERVACIONES'])
    
    ws_fac = wb.create_sheet('BD_FACTURAS')
    ws_fac.append(['FOLIO_CONCILIACION', 'FOLIO_FACTURA', 'FECHA_FACTURA', 'SEMANA', 'PROVEEDOR', 'PUNTO_DE_CARGA', 'LITROS_FACTURADOS', 'PRECIO_UNITARIO', 'IMPORTE', 'I.V.A', 'IMPORTE_TOTAL', 'TIPO_COMBUSTIBLE', 'ESTATUS_CONCILIACION'])
    
    ws_td = wb.create_sheet('TABLAS_DINAMICAS')
    ws_td.append(['Aquí puedes insertar tus tablas dinámicas de resumen'])
    
    for sheet in wb.sheetnames:
        style_headers(wb[sheet])
    
    # Add formulas for ESTATUS_CONCILIACION starting from row 2 to 1000
    # En BD_GASOLINA, revisamos si el FOLIO_CONCILIACION existe en BD_FACTURAS y coinciden importes
    for i in range(2, 501):
        ws_mov[f'N{i}'] = f'=IF(A{i}="", "", IF(SUMIFS(BD_FACTURAS!I:I, BD_FACTURAS!A:A, A{i}) = L{i}, "✅ Cuadrado", "⚠️ Diferencia"))'

    wb.save('c:/Users/JOSE/Desktop/Proyecto fenix/MAESTRO_CONTROL_GASOLINA_NUEVO.xlsx')
    print('Created Gasolina')

create_gasolina()

