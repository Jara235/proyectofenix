import pandas as pd
import numpy as np

maestro_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_GASOLINA_NUEVO.xlsx'

df_gas = pd.read_excel(maestro_path, sheet_name='BD_GASOLINA')
df_fac = pd.read_excel(maestro_path, sheet_name='BD_FACTURAS')

# Filter for LEVET
df_gas_levet = df_gas[df_gas['ORIGEN'].str.contains('LEVET', case=False, na=False)].copy()
df_fac_levet = df_fac[df_fac['PROVEEDOR'].str.contains('LEVET', case=False, na=False)].copy()

gas_records = df_gas_levet.to_dict('records')
fac_records = df_fac_levet.to_dict('records')

matched_pairs = []
unmatched_gas = []
unmatched_fac = fac_records.copy()

# Try exact match first
for g in gas_records:
    g_importe = float(g.get('IMPORTE_TOTAL', 0))
    match_found = False
    
    for f in unmatched_fac:
        f_importe = float(f.get('IMPORTE_TOTAL', 0))
        if abs(g_importe - f_importe) < 1.0: # Exact or within 1 peso (rounding)
            matched_pairs.append({
                'REPORTE_FECHA': g.get('FECHA', ''),
                'REPORTE_VEHICULO': g.get('VEHICULO', ''),
                'REPORTE_OBRA': g.get('OBRA_DESTINO', ''),
                'REPORTE_IMPORTE': g_importe,
                'FACTURA_FOLIO': f.get('FOLIO_CONCILIACION', ''),
                'FACTURA_LITROS': f.get('LITROS_FACTURADOS', 0),
                'FACTURA_IMPORTE': f_importe,
                'DIFERENCIA': g_importe - f_importe,
                'ESTATUS': 'Conciliado'
            })
            unmatched_fac.remove(f)
            match_found = True
            break
            
    if not match_found:
        unmatched_gas.append(g)

# Build final table
final_data = []

# 1. Matched
for m in matched_pairs:
    final_data.append(m)

# 2. Falta Factura
for g in unmatched_gas:
    final_data.append({
        'REPORTE_FECHA': g.get('FECHA', ''),
        'REPORTE_VEHICULO': g.get('VEHICULO', ''),
        'REPORTE_OBRA': g.get('OBRA_DESTINO', ''),
        'REPORTE_IMPORTE': float(g.get('IMPORTE_TOTAL', 0)),
        'FACTURA_FOLIO': '',
        'FACTURA_LITROS': 0,
        'FACTURA_IMPORTE': 0,
        'DIFERENCIA': float(g.get('IMPORTE_TOTAL', 0)),
        'ESTATUS': 'Falta Factura'
    })

# 3. Falta Reporte
for f in unmatched_fac:
    final_data.append({
        'REPORTE_FECHA': '',
        'REPORTE_VEHICULO': '',
        'REPORTE_OBRA': '',
        'REPORTE_IMPORTE': 0,
        'FACTURA_FOLIO': f.get('FOLIO_CONCILIACION', ''),
        'FACTURA_LITROS': f.get('LITROS_FACTURADOS', 0),
        'FACTURA_IMPORTE': float(f.get('IMPORTE_TOTAL', 0)),
        'DIFERENCIA': -float(f.get('IMPORTE_TOTAL', 0)),
        'ESTATUS': 'Falta Reporte'
    })

df_final = pd.DataFrame(final_data)
# Sort to have Conciliado first, then Falta Factura, then Falta Reporte
df_final = df_final.sort_values(by=['ESTATUS', 'REPORTE_FECHA', 'REPORTE_IMPORTE'], ascending=[True, True, False])

with pd.ExcelWriter(maestro_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    df_final.to_excel(writer, sheet_name='Comparativa_Levet', index=False)

print(f"Comparativa_Levet generada con {len(df_final)} registros.")
print(f"  Conciliados: {len(matched_pairs)}")
print(f"  Falta Factura: {len(unmatched_gas)}")
print(f"  Falta Reporte: {len(unmatched_fac)}")
