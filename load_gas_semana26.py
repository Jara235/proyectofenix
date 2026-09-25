import pandas as pd
import openpyxl

df_in = pd.read_excel('c:/Users/JOSE/Desktop/Proyecto fenix/gasolina/SEMANA 26.xlsx', header=1)
df_in = df_in.dropna(subset=['CENTRO DE TRABAJO', 'UNIDAD / EQUIPO', 'IMPORTE SEMANAL AUTORIZADO '], how='all')

catalogos = []
autorizaciones = []
folio_counter = 1

for index, row in df_in.iterrows():
    frente = str(row.get('CENTRO DE TRABAJO', '')).strip()
    resp = str(row.get('RESONSABLE', '')).strip()
    vehiculo = str(row.get('UNIDAD / EQUIPO', '')).strip()
    placa = str(row.get('PLACAS', '')).strip()
    importe = row.get('IMPORTE SEMANAL AUTORIZADO ')
    
    if frente == 'nan': frente = ''
    if resp == 'nan': resp = ''
    if vehiculo == 'nan': vehiculo = ''
    if placa == 'nan': placa = ''
    
    if vehiculo:
        # Append to catalog
        catalogos.append({
            'FRENTE DE TRABAJO': frente,
            'CODIGO_OBRA': '',
            'RESPONSABLE DE FRENTE DE TRABAJO': '',
            'VEHICULOS': vehiculo,
            'PLACA': placa,
            'CONDUCTORES': resp,
            'TIPO_MOVIMIENTO': '',
            'ORIGEN': ''
        })
        
        # Append to autorizaciones if there is an importe
        try:
            imp_val = float(importe)
            if imp_val > 0:
                autorizaciones.append({
                    'FOLIO_CONCILIACION': f'AUT-S26-{folio_counter:03d}',
                    'FECHA': '2026-06-22',
                    'SEMANA': 26,
                    'ORIGEN': 'TARJETA',
                    'OBRA_DESTINO': frente,
                    'VEHICULO': vehiculo,
                    'PLACA': placa,
                    'LITROS_AUTORIZADOS': 0,
                    'IMPORTE_AUTORIZADO': imp_val,
                    'RESPONSABLE': resp,
                    'ESTATUS_AUTORIZACION': 'AUTORIZADO',
                    'OBSERVACIONES': ''
                })
                folio_counter += 1
        except:
            pass

df_cat = pd.DataFrame(catalogos).drop_duplicates(subset=['VEHICULOS', 'PLACA'])
df_aut = pd.DataFrame(autorizaciones)

with pd.ExcelWriter('c:/Users/JOSE/Desktop/Proyecto fenix/MAESTRO_CONTROL_GASOLINA_NUEVO.xlsx', engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
    df_cat.to_excel(writer, sheet_name='CATALOGOS', index=False, header=False, startrow=2)
    df_aut.to_excel(writer, sheet_name='BD_AUTORIZACIONES', index=False, header=False, startrow=2)

print(f'Importados {len(df_cat)} registros a CATALOGOS y {len(df_aut)} registros a BD_AUTORIZACIONES')

