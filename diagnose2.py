import pandas as pd

maestro_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_GASOLINA_NUEVO.xlsx'
bd_gas = pd.read_excel(maestro_path, sheet_name='BD_GASOLINA')
bd_gas['IMPORTE_TOTAL'] = pd.to_numeric(bd_gas['IMPORTE_TOTAL'], errors='coerce').fillna(0)

# Show all columns for semana 26 LEVET specifically
levet26 = bd_gas[(bd_gas['SEMANA'] == 26) & (bd_gas['ORIGEN'].str.upper().str.contains('LEVET', na=False))]
print(f'BD_GASOLINA - LEVET semana 26: {len(levet26)} registros, Total: {levet26.IMPORTE_TOTAL.sum():,.2f}')
print()
print(levet26[['FOLIO_CONCILIACION','PLACA','VEHICULO','OBRA_DESTINO','IMPORTE_TOTAL','CONDUCTOR']].to_string())

print('\n')
# The GT file says ,400 authorized, BD_GASOLINA has ,102 for LEVET semana 26 alone
# The estados de cuenta was comparing IMPORTE_AUTORIZADO (GT file) vs CONSUMO_REAL (BD_GASOLINA grouped by PLACA)
# But GT file has importe_autorizado = weekly budget per vehicle
# BD_GASOLINA has actual charges per ticket

# What did the merge give us?
gt26 = pd.read_excel(r'c:\Users\JOSE\Desktop\Proyecto fenix\CONSUMOS_DE_GASOLINA_SEMANALES_GT.xlsx',
    sheet_name='Consumos Semanales GT', header=2)
gt26.columns = ['_idx','RESPONSABLE','VEHICULO','PLACA','OBRA_DESTINO','IMPORTE_AUTORIZADO','GASOLINERA']
gt26 = gt26[gt26['RESPONSABLE'].notna() & (gt26['RESPONSABLE'] != 'RESPONSABLE') & (gt26['RESPONSABLE'] != 'Total General')].copy()
gt26['PLACA'] = gt26['PLACA'].astype(str).str.strip().str.upper().str.replace(r'[\s\-]','',regex=True)
gt26['IMPORTE_AUTORIZADO'] = pd.to_numeric(gt26['IMPORTE_AUTORIZADO'], errors='coerce').fillna(0)
gt26.loc[gt26['PLACA'] == 'NAN', 'PLACA'] = 'S/P'
print('=== GT26 PLACAS vs BD_GASOLINA PLACAS ===')
print('GT26 placas:', sorted(gt26['PLACA'].unique().tolist()))

bd_placas = sorted(levet26['PLACA'].dropna().astype(str).str.strip().str.upper().str.replace(r'[\s\-]','',regex=True).unique().tolist())
print('BD_GASOLINA sem26 LEVET placas:', bd_placas)
