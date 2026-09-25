import pandas as pd

maestro_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_GASOLINA_NUEVO.xlsx'

# Show BD_GASOLINA full detail - all rows, all semanas
bd_gas = pd.read_excel(maestro_path, sheet_name='BD_GASOLINA')
bd_fac = pd.read_excel(maestro_path, sheet_name='BD_FACTURAS')

print('=== BD_GASOLINA - SUMA POR SEMANA Y ORIGEN ===')
bd_gas['IMPORTE_TOTAL'] = pd.to_numeric(bd_gas['IMPORTE_TOTAL'], errors='coerce').fillna(0)
print(bd_gas.groupby(['SEMANA','ORIGEN'])['IMPORTE_TOTAL'].sum().reset_index().to_string())

print(f'\nTotal BD_GASOLINA: {bd_gas.IMPORTE_TOTAL.sum():,.2f}')
print(f'Total registros: {len(bd_gas)}')

print('\n=== BD_FACTURAS - SUMA POR SEMANA Y PROVEEDOR ===')
bd_fac['IMPORTE_TOTAL'] = pd.to_numeric(bd_fac['IMPORTE_TOTAL'], errors='coerce').fillna(0)
print(bd_fac.groupby(['SEMANA','PROVEEDOR'])['IMPORTE_TOTAL'].sum().reset_index().to_string())

print(f'\nTotal BD_FACTURAS: {bd_fac.IMPORTE_TOTAL.sum():,.2f}')
print(f'Total registros: {len(bd_fac)}')

print('\n=== SOLO LEVET EN FACTURAS ===')
levet = bd_fac[bd_fac['PROVEEDOR'].str.upper().str.contains('LEVET', na=False)]
print(f'Total LEVET facturado: {levet.IMPORTE_TOTAL.sum():,.2f}')
print(f'Registros LEVET: {len(levet)}')
print(levet[['SEMANA','FOLIO_FACTURA','LITROS_FACTURADOS','IMPORTE_TOTAL']].to_string())
