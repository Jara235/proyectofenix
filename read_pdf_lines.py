import PyPDF2
import sys
import re
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')
file_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\facturas\FACTURA J.D.J. JUNIO2026.pdf'

text = ""
with open(file_path, 'rb') as f:
    reader = PyPDF2.PdfReader(f)
    for page in reader.pages:
        text += page.extract_text() + "\n"

# We want to match: [cantidad]PL/24182... \n Folionota=... [clave] [desc] [importe] LTR 002Tasa...
# Actually let's just find lines with "LTR 002Tasa"

cargas = []
lines = text.split('\n')
for i, line in enumerate(lines):
    if 'LTR 002Tasa' in line:
        # Prev line has Cantidad
        prev_line = lines[i-1] if i > 0 else ""
        cantidad = 0.0
        if 'PL/' in prev_line:
            try:
                cantidad = float(prev_line.split('PL/')[0].strip())
            except:
                pass
                
        # Current line: Folionota=39907815101514 32011MAGNA 1471.57 LTR 002Tasa1427.60.1600228.43 19.8143
        # Look for MAGNA or PREMIUM
        tipo = "Gasolina"
        if 'MAGNA' in line:
            tipo = "Magna"
        elif 'PREMIUM' in line:
            tipo = "Premium"
        elif 'DIESEL' in line or '15101505' in line:
            tipo = "Diesel"
            
        # Extract Importe and IVA
        # MAGNA 1471.57 LTR
        importe = 0.0
        match_importe = re.search(r'(MAGNA|PREMIUM|DIESEL)\s+([0-9.]+)\s+LTR', line)
        if not match_importe:
            match_importe = re.search(r'([A-Z]+)\s+([0-9.]+)\s+LTR', line)
        if match_importe:
            importe = float(match_importe.group(2))
            
        # 0.1600[IVA_AMOUNT] [precio_unitario]
        iva = 0.0
        match_iva = re.search(r'0\.1600([0-9.]+)\s+[0-9.]+$', line)
        if match_iva:
            iva = float(match_iva.group(1))
            
        if tipo in ['Magna', 'Premium'] and cantidad > 0:
            cargas.append({
                'cantidad': cantidad,
                'importe': importe,
                'iva': iva,
                'tipo': tipo
            })

print(f"Encontradas {len(cargas)} cargas en PDF:")
for c in cargas:
    print(c)

# Now append to Excel
maestro_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_GASOLINA_NUEVO.xlsx'
df_facturas = pd.read_excel(maestro_path, sheet_name='BD_FACTURAS')

new_rows = []
for i, c in enumerate(cargas):
    total = c['importe'] + c['iva']
    precio_u = c['importe'] / c['cantidad'] if c['cantidad'] > 0 else 0
    
    new_rows.append({
        'FOLIO_CONCILIACION': f'FAC-GAS-27-099-{i+1}',
        'FOLIO_FACTURA': '4LV4025',
        'FECHA_FACTURA': '2026-06-30',
        'SEMANA': 27,
        'PROVEEDOR': 'SERVICIO LEVET',
        'PUNTO_DE_CARGA': 'LEVET',
        'LITROS_FACTURADOS': round(c['cantidad'], 2),
        'PRECIO_UNITARIO': round(precio_u, 2),
        'IMPORTE': round(c['importe'], 2),
        'I.V.A': round(c['iva'], 2),
        'IMPORTE_TOTAL': round(total, 2),
        'TIPO_COMBUSTIBLE': c['tipo'],
        'ESTATUS_CONCILIACION': 'EN ESPERA'
    })

if new_rows:
    df_facturas = pd.concat([df_facturas, pd.DataFrame(new_rows)], ignore_index=True)
    with pd.ExcelWriter(maestro_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df_facturas.to_excel(writer, sheet_name='BD_FACTURAS', index=False)
    print(f"Added {len(new_rows)} rows to BD_FACTURAS")

