import sqlite3, openpyxl, datetime
import pandas as pd

wb = openpyxl.load_workbook('c:/Users/JOSE/Desktop/Proyecto fenix/MAESTRO_CONTROL_DIESEL_NUEVO.xlsx', data_only=True, read_only=True)
db = sqlite3.connect('c:/Users/JOSE/Desktop/Proyecto fenix/fenix_v2.db')
c = db.cursor()

print('Loading Consumos...')
ws_c = wb['BD_DIESEL']
df_c = pd.DataFrame(ws_c.values)
headers = df_c.iloc[0]
df_c = df_c[1:]
df_c.columns = headers
df_c = df_c.dropna(subset=['FOLIO_CONCILIACION', 'LITROS'], how='any')

for _, row in df_c.iterrows():
    try:
        c.execute('''INSERT OR IGNORE INTO diesel_consumos 
            (folio_conciliacion, fecha, semana, origen, tipo_movimiento, obra_destino, equipo, equipo_economico, litros, costo_por_litro, importe_total, responsable, operador, observaciones) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
            (str(row['FOLIO_CONCILIACION']), str(row['FECHA'])[:10], row['SEMANA'], str(row['ORIGEN']), str(row['TIPO_MOVIMIENTO']), 
             str(row['OBRA_DESTINO']), str(row['EQUIPO']), str(row['EQUIPO_ECONOMICO']), float(row['LITROS']), float(row['COSTO_POR_LITRO'] or 0), 
             float(row['IMPORTE_TOTAL'] or 0), str(row['RESPONSABLE']), str(row['OPERADOR']), str(row['OBSERVACIONES'])))
    except Exception as e:
        print(f'Error row {row['FOLIO_CONCILIACION']}: {e}')

print('Loading Facturas...')
ws_f = wb['BD_FACTURAS']
df_f = pd.DataFrame(ws_f.values)
headers = df_f.iloc[0]
df_f = df_f[1:]
df_f.columns = headers
df_f = df_f.dropna(subset=['FOLIO_CONCILIACION', 'LITROS_FACTURADOS'], how='any')

for _, row in df_f.iterrows():
    try:
        c.execute('''INSERT OR IGNORE INTO diesel_facturas 
            (folio_conciliacion, folio_factura, fecha_factura, semana, proveedor, punto_de_carga, litros_facturados, precio_unitario, importe, iva, importe_total) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
            (str(row['FOLIO_CONCILIACION']), str(row['FOLIO_FACTURA']), str(row['FECHA_FACTURA'])[:10], row['SEMANA'], str(row['PROVEEDOR']), 
             str(row['PUNTO_DE_CARGA']), float(row['LITROS_FACTURADOS']), float(row['PRECIO_UNITARIO'] or 0), float(row['IMPORTE'] or 0), 
             float(row['I.V.A'] or 0), float(row['IMPORTE_TOTAL'] or 0)))
    except Exception as e:
        print(f'Error row {row['FOLIO_CONCILIACION']}: {e}')

db.commit()
db.close()
print('Migration complete!')

