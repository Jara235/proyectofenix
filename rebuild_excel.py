import sqlite3, openpyxl, datetime
import pandas as pd

wb = openpyxl.load_workbook('c:/Users/JOSE/Desktop/Proyecto fenix/GC-COMB-3.1_Excel_Maestro_Control_Combustible_Grupo_Trujano_LIMPIO.xlsx')
ws = wb['Captura_Facturas_Mobil']
db = sqlite3.connect('c:/Users/JOSE/Desktop/Proyecto fenix/fenix.db')
df = pd.read_sql("SELECT folio, fecha_emision, destino_suministro, litros_totales, total FROM fenix_facturas_documentos WHERE tipo_combustible='Diesel' ORDER BY fecha_emision ASC", db)

for r in range(ws.max_row, 4, -1):
    ws.delete_rows(r)

for index, row in df.iterrows():
    r = index + 5
    folio = f"A-{row['folio']}" if not str(row['folio']).startswith('A-') else str(row['folio'])
    try:
        fecha = datetime.datetime.strptime(str(row['fecha_emision']).split('.')[0].replace('T', ' '), '%Y-%m-%d %H:%M:%S')
    except:
        fecha = datetime.datetime.strptime(str(row['fecha_emision']).split('T')[0], '%Y-%m-%d')
    
    destino = str(row['destino_suministro']) if not pd.isna(row['destino_suministro']) else 'México-Toluca'
    if 'pegaso' in destino.lower(): destino = 'Maquinaria Pegaso'
    elif 'planta' in destino.lower() or 'lerma' in destino.lower(): destino = 'Planta Asflato Huixquilucan'
    else: destino = 'México-Toluca'
    
    lts = float(row['litros_totales'] or 0)
    monto = float(row['total'] or 0)
    precio = round(monto / lts, 2) if lts > 0 else 27.00
    
    ws.cell(row=r, column=1).value = folio
    ws.cell(row=r, column=2).value = fecha
    ws.cell(row=r, column=3).value = 39
    ws.cell(row=r, column=4).value = destino
    ws.cell(row=r, column=5).value = lts
    ws.cell(row=r, column=6).value = precio
    ws.cell(row=r, column=7).value = monto
    ws.cell(row=r, column=14).value = fecha.isocalendar().week

wb.save('c:/Users/JOSE/Desktop/Proyecto fenix/GC-COMB-3.1_Excel_Maestro_Control_Combustible_Grupo_Trujano_LIMPIO.xlsx')
print('Excel rebuilt from DB successfully!')

