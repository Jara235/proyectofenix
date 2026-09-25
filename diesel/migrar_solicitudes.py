import pandas as pd
import psycopg2
import math

excel_file = r'c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_DIESEL_NUEVO.xlsx'

print("Leyendo Excel...")
df = pd.read_excel(excel_file, sheet_name='BD_SOLICITUD ')

# Clean NaN
df = df.where(pd.notnull(df), None)

print("Conectando a BD...")
conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
conn.autocommit = True
cur = conn.cursor()

print("Creando tabla diesel.solicitudes...")
cur.execute("""
    DROP TABLE IF EXISTS diesel.solicitudes CASCADE;
    CREATE TABLE diesel.solicitudes (
        id SERIAL PRIMARY KEY,
        folio_solicitud VARCHAR(100),
        fecha DATE,
        semana VARCHAR(50),
        solicitante VARCHAR(200),
        tipo_movimiento VARCHAR(100),
        obra_destino VARCHAR(200),
        equipo VARCHAR(200),
        equipo_economico VARCHAR(100),
        litros DECIMAL(10,2),
        costo_por_litro DECIMAL(10,2),
        importe_total DECIMAL(12,2),
        responsable VARCHAR(200),
        operador VARCHAR(200),
        estatus_conciliacion VARCHAR(50) DEFAULT 'PENDIENTE',
        observaciones TEXT
    );
    TRUNCATE TABLE diesel.solicitudes RESTART IDENTITY;
""")

print("Insertando registros...")
for _, row in df.iterrows():
    # If folio is null, skip
    if not row['FOLIO_CONCILIACION']: continue
    
    fecha = row['FECHA']
    if pd.isnull(fecha): fecha = None
    elif isinstance(fecha, pd.Timestamp): fecha = fecha.date()
    
    litros = float(row['LITROS']) if row['LITROS'] is not None else 0.0
    costo = float(row['COSTO_POR_LITRO']) if row['COSTO_POR_LITRO'] is not None else 0.0
    importe = float(row['IMPORTE_TOTAL']) if row['IMPORTE_TOTAL'] is not None else 0.0
    
    if math.isnan(litros): litros = 0.0
    if math.isnan(costo): costo = 0.0
    if math.isnan(importe): importe = 0.0
    
    cur.execute("""
        INSERT INTO diesel.solicitudes (
            folio_solicitud, fecha, semana, solicitante, tipo_movimiento, obra_destino,
            equipo, equipo_economico, litros, costo_por_litro, importe_total,
            responsable, operador, estatus_conciliacion, observaciones
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        str(row['FOLIO_CONCILIACION']).strip(),
        fecha,
        str(row['SEMANA']) if row['SEMANA'] else None,
        row['SOLICITANTE'],
        row['TIPO_MOVIMIENTO'],
        row['OBRA_DESTINO'],
        row['EQUIPO'],
        row['EQUIPO_ECONOMICO'],
        litros,
        costo,
        importe,
        row['RESPONSABLE'],
        row['OPERADOR'],
        row['ESTATUS_CONCILIACION'] if row['ESTATUS_CONCILIACION'] else 'PENDIENTE',
        row['OBSERVACIONES']
    ))

print("Migración completada con éxito.")
