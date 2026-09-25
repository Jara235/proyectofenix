import openpyxl
wb = openpyxl.load_workbook('c:/Users/JOSE/Desktop/Proyecto fenix/MAESTRO_CONTROL_DIESEL_NUEVO.xlsx', data_only=True, read_only=True)
for sheet in ['BD_DIESEL', 'BD_FACTURAS']:
    ws = wb[sheet]
    headers = []
    for r, row in enumerate(ws.iter_rows(min_row=1, max_row=5, values_only=True)):
        if any(row):
            headers = [str(c) if c else '' for c in row]
            print(f'--- {sheet} Headers ---')
            print(headers)
            break

