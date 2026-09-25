import openpyxl
wb = openpyxl.load_workbook('c:/Users/JOSE/Desktop/Proyecto fenix/MAESTRO_CONTROL_DIESEL_NUEVO.xlsx', data_only=True, read_only=True)
for sheet in ['BD_DIESEL', 'BD_FACTURAS']:
    ws = wb[sheet]
    count = 0
    for r in ws.iter_rows(values_only=True):
        if any(r): count += 1
    print(f'{sheet} has {count} rows')

