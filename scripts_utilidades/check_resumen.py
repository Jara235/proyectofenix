import openpyxl
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
wb = openpyxl.load_workbook('c:/Users/JOSE/Desktop/Proyecto fenix/GC-COMB-3.1_Excel_Maestro_Control_Combustible_Grupo_Trujano_LIMPIO.xlsx')
ws = wb['Captura_Facturas_Mobil']
# Check what formula the Resumen_Ejecutivo uses to read from Captura_Facturas_Mobil
ws2 = wb['Resumen_Ejecutivo']
for r in range(1, 50):
    for c in range(1, 20):
        val = ws2.cell(row=r, column=c).value
        if isinstance(val, str) and 'Captura_Facturas' in val:
            print(f'Resumen_Ejecutivo R{r}C{c}: {val[:200]}')

