import pandas as pd
import numpy as np
import os

# Configurar rutas
base_dir = r"C:\Users\JOSE\Desktop\Proyecto fenix\gasolina"
file_semana26 = os.path.join(base_dir, "SEMANA 26.xlsx")
file_jdj = os.path.join(base_dir, "CONTROL JDJ PROVISIONAL semana 27.xlsx")
file_gt = os.path.join(base_dir, "CONSUMOS  DE GASOLINA SEMANALES GT.xlsx")
output_file = os.path.join(base_dir, "Maestro_Conciliacion_Gasolina.xlsx")

def clean_currency(x):
    if isinstance(x, str):
        x = x.replace('$', '').replace(',', '').strip()
        try:
            return float(x)
        except ValueError:
            return 0.0
    return float(x) if pd.notna(x) else 0.0

def generate_folios(prefix, week, count):
    return [f"{prefix}-{week}-{str(i).zfill(3)}" for i in range(1, count + 1)]

try:
    print("Leyendo SEMANA 26 (1).xlsx...")
    df_semana26 = pd.read_excel(file_semana26, sheet_name="SEMANA 26", skiprows=1)
    df_semana26.rename(columns={df_semana26.columns[1]: 'RESPONSABLE_REAL', 'IMPORTE SEMANAL AUTORIZADO ': 'IMPORTE SEMANAL AUTORIZADO'}, inplace=True)
    
    # Rellenar celdas combinadas de Excel para 'CENTRO DE TRABAJO' antes de limpiar
    if 'CENTRO DE TRABAJO' in df_semana26.columns:
        df_semana26['CENTRO DE TRABAJO'] = df_semana26['CENTRO DE TRABAJO'].ffill()
    
    # Extraer catalogo y quitar duplicados (No borrar si no tiene placa, usar 'S/P' o nombre de equipo)
    df_catalogo = df_semana26[['RESPONSABLE_REAL', 'CENTRO DE TRABAJO', 'UNIDAD / EQUIPO', 'PLACAS']].copy()
    df_catalogo = df_catalogo[df_catalogo['UNIDAD / EQUIPO'] != 'UNIDAD / EQUIPO']
    df_catalogo['PLACAS'] = df_catalogo['PLACAS'].fillna('S/P - ' + df_catalogo['UNIDAD / EQUIPO'] + ' - ' + df_catalogo.index.astype(str))
    df_catalogo['PLACAS'] = df_catalogo['PLACAS'].astype(str).str.replace('-', '').str.strip().str.upper()
    df_catalogo.rename(columns={'RESPONSABLE_REAL': 'RESPONSABLE'}, inplace=True)
    df_catalogo['TIPO_EQUIPO'] = 'Automotor / Vehículo'
    df_catalogo['TIPO_COMBUSTIBLE'] = 'Gasolina'
    df_catalogo['TIPO_RENDIMIENTO'] = 'kilometros'
    df_catalogo = df_catalogo.drop_duplicates(subset=['PLACAS'])
    
    # Catalogo Centros de Trabajo
    df_centros = pd.DataFrame(df_catalogo['CENTRO DE TRABAJO'].unique(), columns=['CENTRO DE TRABAJO']).dropna()
    
    # Extraer autorizaciones (agrupando por si hay placas duplicadas en el reporte)
    df_autorizaciones_raw = df_semana26[['RESPONSABLE_REAL', 'CENTRO DE TRABAJO', 'UNIDAD / EQUIPO', 'PLACAS', 'IMPORTE SEMANAL AUTORIZADO']].copy()
    df_autorizaciones_raw = df_autorizaciones_raw.dropna(subset=['UNIDAD / EQUIPO'])
    df_autorizaciones_raw = df_autorizaciones_raw[df_autorizaciones_raw['UNIDAD / EQUIPO'] != 'UNIDAD / EQUIPO']
    df_autorizaciones_raw['PLACAS'] = df_autorizaciones_raw['PLACAS'].fillna('S/P - ' + df_autorizaciones_raw['UNIDAD / EQUIPO'] + ' - ' + df_autorizaciones_raw.index.astype(str))
    df_autorizaciones_raw['PLACAS'] = df_autorizaciones_raw['PLACAS'].astype(str).str.replace('-', '').str.strip().str.upper()
    df_autorizaciones_raw['IMPORTE SEMANAL AUTORIZADO'] = df_autorizaciones_raw['IMPORTE SEMANAL AUTORIZADO'].apply(clean_currency)
    df_autorizaciones_raw.rename(columns={'RESPONSABLE_REAL': 'RESPONSABLE'}, inplace=True)
    
    # Agrupar para sumar autorizaciones si una placa sale 2 veces y quedarse con la primera info
    df_autorizaciones = df_autorizaciones_raw.groupby('PLACAS', as_index=False).agg({
        'RESPONSABLE': 'first',
        'CENTRO DE TRABAJO': 'first',
        'UNIDAD / EQUIPO': 'first',
        'IMPORTE SEMANAL AUTORIZADO': 'sum'
    })
    
    # Agregar FOLIO y SEMANA
    df_autorizaciones.insert(0, 'FOLIO', generate_folios('AU', '26', len(df_autorizaciones)))
    df_autorizaciones.insert(1, 'SEMANA', 26)
    
except Exception as e:
    print(f"Error procesando SEMANA 26: {e}")

try:
    print("Leyendo CONTROL JDJ PROVISIONAL semana 27.xlsx...")
    df_jdj = pd.read_excel(file_jdj, sheet_name="JUNIO 2026", skiprows=3)
    df_jdj.columns = df_jdj.columns.str.strip()
    df_levet = df_jdj.copy()
    
    # Preparar para consolidada
    df_cons_levet = pd.DataFrame({
        'TICKET': df_levet['TICKET'],
        'FECHA': df_levet['FECHA'],
        'PLACAS': df_levet['UNID.'],
        'CONDUCTOR': df_levet['CONDUCTOR'],
        'KILOMETRAJE': df_levet['KILOMETRAJE'],
        'LTS_DE_COMBUSTIBLE': df_levet['LTS. DE COMBUST.'],
        'PRECIO_POR_LITRO': df_levet['PRECIO'],
        'IMPORTE_DE_CARGA': df_levet['IMPORTE DE CARGA'],
        'GASOLINERA_ORIGEN': 'Levet'
    }).dropna(subset=['PLACAS'])
    df_cons_levet['IMPORTE_DE_CARGA'] = df_cons_levet['IMPORTE_DE_CARGA'].apply(clean_currency)
    df_cons_levet['PLACAS'] = df_cons_levet['PLACAS'].astype(str).str.replace('-', '').str.strip().str.upper()
    
    # Agregar FOLIO
    df_cons_levet.insert(0, 'FOLIO', generate_folios('LE', '27', len(df_cons_levet)))
    
except Exception as e:
    print(f"Error procesando JDJ: {e}")

try:
    print("Leyendo CONSUMOS DE GASOLINA SEMANALES GT.xlsx...")
    df_gt = pd.read_excel(file_gt, sheet_name="UT", skiprows=2)
    df_gt.columns = df_gt.columns.str.strip()
    df_huix = df_gt.copy()
    
    # Preparar para consolidada
    df_cons_huix = pd.DataFrame({
        'TICKET': None,
        'FECHA': df_huix['FECHA DE CARGA'],
        'PLACAS': df_huix['PLACAS'],
        'CONDUCTOR': df_huix['RESONSABLE'] if 'RESONSABLE' in df_huix.columns else df_huix.iloc[:, 0],
        'KILOMETRAJE': None,
        'LTS_DE_COMBUSTIBLE': None,
        'PRECIO_POR_LITRO': None,
        'IMPORTE_DE_CARGA': df_huix['CONSUMO'],
        'GASOLINERA_ORIGEN': 'Huixquilucan'
    }).dropna(subset=['PLACAS', 'IMPORTE_DE_CARGA'])
    df_cons_huix['IMPORTE_DE_CARGA'] = df_cons_huix['IMPORTE_DE_CARGA'].apply(clean_currency)
    df_cons_huix['PLACAS'] = df_cons_huix['PLACAS'].astype(str).str.replace('-', '').str.strip().str.upper()
    
    # Agregar FOLIO (se asume semana 26 por las fechas de los consumos)
    df_cons_huix.insert(0, 'FOLIO', generate_folios('HU', '26', len(df_cons_huix)))
    
except Exception as e:
    print(f"Error procesando GT: {e}")

try:
    print("Creando Base de Datos Consolidada...")
    df_consolidada = pd.concat([df_cons_levet, df_cons_huix], ignore_index=True)
    
    # Cruzar datos de catálogo hacia consolidada para tener el Centro de Trabajo (ahora df_catalogo es unico por placa)
    df_consolidada = df_consolidada.merge(df_catalogo[['PLACAS', 'RESPONSABLE', 'CENTRO DE TRABAJO', 'UNIDAD / EQUIPO']], on='PLACAS', how='left')
    
    # Calcular Consumo Real y Saldo para Autorizaciones
    consumo_por_placa = df_consolidada.groupby('PLACAS')['IMPORTE_DE_CARGA'].sum().reset_index()
    consumo_por_placa.rename(columns={'IMPORTE_DE_CARGA': 'CONSUMO_REAL'}, inplace=True)
    
    # Usar OUTER JOIN para capturar unidades que cargaron gasolina pero NO estaban autorizadas
    df_autorizaciones = df_autorizaciones.merge(consumo_por_placa, on='PLACAS', how='outer')
    
    # Limpiar y rellenar nulos resultantes del outer join
    df_autorizaciones['IMPORTE SEMANAL AUTORIZADO'] = df_autorizaciones['IMPORTE SEMANAL AUTORIZADO'].fillna(0)
    df_autorizaciones['CONSUMO_REAL'] = df_autorizaciones['CONSUMO_REAL'].fillna(0)
    df_autorizaciones['CENTRO DE TRABAJO'] = df_autorizaciones['CENTRO DE TRABAJO'].fillna('NO AUTORIZADO (CARGO GASOLINA)')
    df_autorizaciones['RESPONSABLE'] = df_autorizaciones['RESPONSABLE'].fillna('DESCONOCIDO')
    df_autorizaciones['UNIDAD / EQUIPO'] = df_autorizaciones['UNIDAD / EQUIPO'].fillna('DESCONOCIDO')
    
    # Recalcular Saldo
    df_autorizaciones['SALDO_RESTANTE'] = df_autorizaciones['IMPORTE SEMANAL AUTORIZADO'] - df_autorizaciones['CONSUMO_REAL']
    
    # Asegurar que tengan folio las no autorizadas
    mask_no_folio = df_autorizaciones['FOLIO'].isna()
    if mask_no_folio.any():
        df_autorizaciones.loc[mask_no_folio, 'FOLIO'] = ['EX-' + str(i).zfill(3) for i in range(1, mask_no_folio.sum() + 1)]
        df_autorizaciones.loc[mask_no_folio, 'SEMANA'] = 26
        
    print("Creando Tablas de Evaluacion...")
    pt_gasolineria = pd.pivot_table(df_consolidada, values='IMPORTE_DE_CARGA', index='GASOLINERA_ORIGEN', aggfunc=np.sum).reset_index()
    pt_gasolineria.rename(columns={'IMPORTE_DE_CARGA': 'GASTO TOTAL'}, inplace=True)
    
    eval_unidades = df_autorizaciones.copy()
    
except Exception as e:
    print(f"Error creando consolidados: {e}")

try:
    print("Escribiendo al archivo Excel...")
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        # 2. Catálogos
        df_catalogo.to_excel(writer, sheet_name='catalogos', index=False)
        df_centros.to_excel(writer, sheet_name='catalogos', startcol=df_catalogo.shape[1] + 2, index=False)
        df_autorizaciones.to_excel(writer, sheet_name='autorizaciones por unidad', index=False)
        df_levet.to_excel(writer, sheet_name='gasolineria levet', index=False)
        df_huix.to_excel(writer, sheet_name='gasolineria huixquilucan', index=False)
        df_consolidada.to_excel(writer, sheet_name='base de datos consolidada', index=False)
        
        # Escribir tablas de evaluación
        pt_gasolineria.to_excel(writer, sheet_name='tabla de evaluacion', startrow=1, startcol=1, index=False)
        worksheet = writer.sheets['tabla de evaluacion']
        worksheet.write_string(0, 1, 'GASTOS DE LA SEMANA POR GASOLINERIA')
        
        eval_unidades.to_excel(writer, sheet_name='tabla de evaluacion', startrow=pt_gasolineria.shape[0] + 5, startcol=1, index=False)
        worksheet.write_string(pt_gasolineria.shape[0] + 4, 1, 'SALDO RESTANTE DE CARGA AUTORIZADA POR UNIDAD')
        
    print(f"Archivo generado exitosamente en: {output_file}")
except Exception as e:
    print(f"Error al escribir Excel: {e}")
