import pandas as pd

maestro_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_GASOLINA_NUEVO.xlsx'
bd_gas = pd.read_excel(maestro_path, sheet_name='BD_GASOLINA')
bd_gas['IMPORTE_TOTAL'] = pd.to_numeric(bd_gas['IMPORTE_TOTAL'], errors='coerce').fillna(0)

# The REAL totals in BD_GASOLINA for semana 26
levet26 = bd_gas[(bd_gas['SEMANA'] == 26) & (bd_gas['ORIGEN'].str.upper().str.contains('LEVET', na=False))]
total_levet26 = levet26['IMPORTE_TOTAL'].sum()
print(f'BD_GASOLINA - LEVET sem 26: {len(levet26)} registros | Total: ')

# Breakdown showing the Sindicato COSUM records that are NOT in the GT authorization file
sindicato = levet26[levet26['OBRA_DESTINO'].str.upper().str.contains('SINDI|COSUM', na=False)]
print(f'\nRegistros SINDICATO (no estan en GT auth): {len(sindicato)}, Total: ')

# Regular GT vehicles
regular = levet26[~levet26['OBRA_DESTINO'].str.upper().str.contains('SINDI|COSUM', na=False)]
print(f'Registros regulares GT: {len(regular)}, Total: ')

print('\n=== GT AUTHORIZATION TOTAL ===')
gt26 = pd.read_excel(r'c:\Users\JOSE\Desktop\Proyecto fenix\CONSUMOS_DE_GASOLINA_SEMANALES_GT.xlsx',
    sheet_name='Consumos Semanales GT', header=2)
gt26.columns = ['_idx','RESPONSABLE','VEHICULO','PLACA','OBRA_DESTINO','IMPORTE_AUTORIZADO','GASOLINERA']
gt26 = gt26[gt26['RESPONSABLE'].notna() & (gt26['RESPONSABLE'] != 'RESPONSABLE') & (gt26['RESPONSABLE'] != 'Total General')].copy()
gt26['IMPORTE_AUTORIZADO'] = pd.to_numeric(gt26['IMPORTE_AUTORIZADO'], errors='coerce').fillna(0)
print(f'GT Semana 26 - Total Autorizado: ')
print(f'GT Semana 26 - Total unidades: {len(gt26)}')

print('\n=== DIFERENCIA EXPLICADA ===')
print(f'Total en BD_GASOLINA (LEVET s26): ')
print(f'Total GT Autorizado (s26):         ')
print(f'Diferencia:                        ')
print(f'(Se explica por Sindicato COSUM):  ')

print('\n=== LEVET FACTURAS vs CONTROL PROVISIONAL (,754) ===')
bd_fac = pd.read_excel(maestro_path, sheet_name='BD_FACTURAS')
bd_fac['IMPORTE_TOTAL'] = pd.to_numeric(bd_fac['IMPORTE_TOTAL'], errors='coerce').fillna(0)
levet_fac = bd_fac[bd_fac['PROVEEDOR'].str.upper().str.contains('LEVET', na=False)]
print(f'Facturas LEVET total (todas semanas): ')
print(f'Facturas LEVET sem 26: ')
print(f'Facturas LEVET sem 27: ')
print()
print('El control provisional (,754) cubre semanas 26+27 de Levet juntas')
print(f'Nuestro total levet s26+s27 en facturas: ')
print(f'Diferencia vs ,754: ')
