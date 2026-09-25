# -*- coding: utf-8 -*-
import openpyxl
wb = openpyxl.load_workbook('c:/Users/JOSE/Desktop/Proyecto fenix/GC-COMB-3.1_Excel_Maestro_Control_Combustible_Grupo_Trujano ultimo(1).xlsx')
ws = wb['Captura_Facturas_Mobil']
factura_col = None
for col in range(1, 20):
    if ws.cell(row=4, column=col).value == 'No. Factura': factura_col = col
gasolinas = ['A-10166', 'A-10168', 'A-10090', 'A-10255', 'A-10265', 'A-10266', 'A-10267', 'A-10268', 'A-10272', 'A-10273', 'A-10274', 'A-10278', 'A-10321', 'A-10322', 'A-10329', 'A-10213', 'A-10214', 'A-10217']
for r in range(ws.max_row, 4, -1):
    if ws.cell(row=r, column=factura_col).value in gasolinas:
        ws.delete_rows(r)
        print(f'Deleted Gasolina {ws.cell(row=r, column=factura_col).value}')
wb.save('c:/Users/JOSE/Desktop/Proyecto fenix/GC-COMB-3.1_Excel_Maestro_Control_Combustible_Grupo_Trujano_LIMPIO.xlsx')

