import pandas as pd
maestro_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_GASOLINA_NUEVO.xlsx'

df_gas = pd.read_excel(maestro_path, sheet_name='BD_GASOLINA')
df_fac = pd.read_excel(maestro_path, sheet_name='BD_FACTURAS')

# Filter for LEVET
df_gas_levet = df_gas[df_gas['ORIGEN'].str.contains('LEVET', case=False, na=False)].copy()
df_fac_levet = df_fac[df_fac['PROVEEDOR'].str.contains('LEVET', case=False, na=False)].copy()

print(f"Gasolina LEVET count: {len(df_gas_levet)}")
print("Sample Gasolina (Reportado):")
print(df_gas_levet[['FECHA', 'VEHICULO', 'LITROS', 'IMPORTE_TOTAL']].head())

print(f"\nFacturas LEVET count: {len(df_fac_levet)}")
print("Sample Facturas:")
print(df_fac_levet[['FECHA_FACTURA', 'LITROS_FACTURADOS', 'IMPORTE_TOTAL']].head())
