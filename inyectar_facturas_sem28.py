import pandas as pd
import json
import openpyxl
import shutil
import sys, io
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

MAESTRO_PATH = r"c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_DIESEL_NUEVO.xlsx"
JSON_PATH = r"c:\Users\JOSE\Desktop\Proyecto fenix\facturas_sem28_clasificadas.json"

# Respaldar
shutil.copy(MAESTRO_PATH, MAESTRO_PATH.replace('.xlsx', '_backup2.xlsx'))
print("Backup creado: MAESTRO_CONTROL_DIESEL_NUEVO_backup2.xlsx")

# Leer el JSON con los datos extraidos
with open(JSON_PATH, 'r', encoding='utf-8') as f:
    facturas = json.load(f)

# Filtrar solo diesel
facturas_diesel = [f for f in facturas if f['tipo'] == 'diesel']
print(f"Facturas diesel a insertar: {len(facturas_diesel)}")

# Leer el archivo actual para ver cuantas filas tiene y el ultimo folio
df_actual = pd.read_excel(MAESTRO_PATH, sheet_name='BD_FACTURAS')
ultimo_num = len(df_actual)
print(f"Filas actuales en BD_FACTURAS: {ultimo_num}")

# Abrir con openpyxl para agregar filas
wb = openpyxl.load_workbook(MAESTRO_PATH)
ws = wb['BD_FACTURAS']

# Ver la ultima fila con datos reales
last_row = ws.max_row
print(f"Ultima fila en excel: {last_row}")

# Extraer el ultimo folio para continuar la numeracion
ultimo_folio_num = ultimo_num  # ya tenemos 78

def generar_folio(datos, num):
    """Genera un folio siguiendo el patron FA-XX-28-NNN"""
    # Intentar detectar la obra por descripcion
    desc = datos.get('descripcion', '').upper()
    # Mapeo de palabras clave a codigo de obra
    if 'BACHEO' in desc or 'TOL' in desc:
        obra = 'BT'
    elif 'TOLUCA' in desc or 'MEX' in desc:
        obra = 'MT'
    elif 'HUIX' in desc or 'PLANTA' in desc:
        obra = 'HX'
    elif 'LERMA' in desc or 'TEN' in desc:
        obra = 'LT'
    elif 'PEGASO' in desc:
        obra = 'PG'
    else:
        obra = 'XX'
    return f"FA-{obra}-28-{str(num).zfill(3)}"

# Definir color de fondo para las filas nuevas (ligero tono diferente para distinguir sem28)
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
fill_new = PatternFill(start_color="EBF1DE", end_color="EBF1DE", fill_type="solid")
border_side = Side(border_style="thin", color="CCCCCC")
border = Border(left=border_side, right=border_side, top=border_side, bottom=border_side)
align_center = Alignment(horizontal="center", vertical="center")

# Insertar facturas
for i, fac in enumerate(facturas_diesel):
    row_num = last_row + 1 + i
    num_folio = ultimo_folio_num + 1 + i
    folio = generar_folio(fac, num_folio)
    
    # Detectar proveedor
    proveedor = fac.get('emisor_nombre', 'DERIVADOS DE PETROLEO CASTILLA').strip()
    if not proveedor:
        proveedor = 'DERIVADOS DE PETROLEO CASTILLA'
    
    # Detectar punto de carga por descripcion
    desc = fac.get('descripcion', '').upper()
    if 'BACHEO' in desc:
        punto = 'Bacheo Toluca'
    elif '1245' in desc or '1246' in desc or 'MEX' in desc:
        punto = 'Mexico-Toluca'
    elif 'HUIX' in desc or '1247' in desc:
        punto = 'Planta de Asfalto Huixquilucan'
    elif 'LERMA' in desc or 'TEN' in desc:
        punto = 'Lerma-Tenango'
    else:
        punto = 'Por Asignar'
    
    litros = fac.get('cantidad', 0)
    precio_unitario = fac.get('precio_unitario', 0)
    importe = fac.get('importe', 0)
    iva = fac.get('iva', 0)
    total = fac.get('total', 0)
    fecha = fac.get('fecha', '')
    semana = fac.get('semana', 'Semana 28')
    folio_fac = fac.get('folio', '')
    
    # Escribir la fila
    valores = [
        folio,           # FOLIO_CONCILIACION
        folio_fac,       # FOLIO_FACTURA
        fecha,           # FECHA_FACTURA
        semana,          # SEMANA
        proveedor,       # PROVEEDOR
        punto,           # PUNTO_DE_CARGA
        litros,          # LITROS_FACTURADOS
        precio_unitario, # PRECIO_UNITARIO
        importe,         # IMPORTE
        iva,             # I.V.A
        total,           # IMPORTE_TOTAL
        'Diesel',        # TIPO_COMBUSTIBLE
        'PENDIENTE',     # ESTATUS_CONCILIACION
        None             # Columna1
    ]
    
    for col_idx, val in enumerate(valores, 1):
        cell = ws.cell(row=row_num, column=col_idx, value=val)
        cell.border = border
        cell.alignment = align_center
        if col_idx in [7, 8, 9, 10, 11]:  # columnas numericas
            cell.number_format = '#,##0.000'
    
    print(f"  [{num_folio:3d}] {folio} | {fecha} | {punto[:25]:25s} | {litros:8.3f} Lts | ${total:12,.2f}")

wb.save(MAESTRO_PATH)
print(f"\nExito! Se agregaron {len(facturas_diesel)} facturas en BD_FACTURAS")
print(f"Total de filas ahora: {ultimo_num + len(facturas_diesel)}")
