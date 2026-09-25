import pandas as pd
import sqlite3
import math

maestro_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_GASOLINA_NUEVO.xlsx'
db_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\fenix_v2.db'

# Read Excel
df_auth = pd.read_excel(maestro_path, sheet_name='BD_AUTORIZACIONES')
df_gas = pd.read_excel(maestro_path, sheet_name='BD_GASOLINA')
df_fac = pd.read_excel(maestro_path, sheet_name='BD_FACTURAS')

# Connect DB
conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("DELETE FROM gasolina_autorizaciones")
cur.execute("DELETE FROM gasolina_consumos")
cur.execute("DELETE FROM gasolina_facturas")

def clean_val(v):
    if pd.isna(v) or str(v).lower() == 'nan':
        return None
    if isinstance(v, pd.Timestamp):
        return v.strftime('%Y-%m-%d')
    if isinstance(v, float) and math.isnan(v):
        return None
    # Stringify everything else that isn't float/int
    if not isinstance(v, (int, float, bool)):
        return str(v).strip()
    return v

# 2. Insert Autorizaciones
auth_count = 0
for _, row in df_auth.iterrows():
    cur.execute('''
        INSERT INTO gasolina_autorizaciones (folio_conciliacion, fecha, semana, obra_destino, vehiculo, placa, litros_autorizados, importe_autorizado, responsable, estatus_autorizacion)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        clean_val(row.get('FOLIO_CONCILIACION')),
        clean_val(row.get('FECHA')),
        clean_val(row.get('SEMANA')),
        clean_val(row.get('OBRA_DESTINO')),
        clean_val(row.get('VEHICULO')),
        clean_val(row.get('PLACA')),
        clean_val(row.get('LITROS_AUTORIZADOS')),
        clean_val(row.get('IMPORTE_AUTORIZADO')),
        clean_val(row.get('RESPONSABLE')),
        clean_val(row.get('ESTATUS_AUTORIZACION'))
    ))
    auth_count += 1

# 3. Insert Consumos
gas_count = 0
for _, row in df_gas.iterrows():
    cur.execute('''
        INSERT INTO gasolina_consumos (folio_conciliacion, fecha, semana, origen, obra_destino, vehiculo, placa, kilometraje, litros, costo_por_litro, importe_total, conductor, observaciones)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        clean_val(row.get('FOLIO_CONCILIACION')),
        clean_val(row.get('FECHA')),
        clean_val(row.get('SEMANA')),
        clean_val(row.get('ORIGEN')),
        clean_val(row.get('OBRA_DESTINO')),
        clean_val(row.get('VEHICULO')),
        clean_val(row.get('PLACA')),
        clean_val(row.get('KILOMETRAJE')),
        clean_val(row.get('LITROS')),
        clean_val(row.get('COSTO_POR_LITRO')),
        clean_val(row.get('IMPORTE_TOTAL')),
        clean_val(row.get('CONDUCTOR')),
        clean_val(row.get('OBSERVACIONES'))
    ))
    gas_count += 1

# 4. Insert Facturas
fac_count = 0
for _, row in df_fac.iterrows():
    cur.execute('''
        INSERT INTO gasolina_facturas (folio_conciliacion, folio_factura, fecha_factura, semana, proveedor, litros_facturados, importe_total)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        clean_val(row.get('FOLIO_CONCILIACION')),
        clean_val(row.get('FOLIO_FACTURA')),
        clean_val(row.get('FECHA_FACTURA')),
        clean_val(row.get('SEMANA')),
        clean_val(row.get('PROVEEDOR')),
        clean_val(row.get('LITROS_FACTURADOS')),
        clean_val(row.get('IMPORTE_TOTAL'))
    ))
    fac_count += 1

conn.commit()
conn.close()

print(f"Migrated {auth_count} autorizaciones.")
print(f"Migrated {gas_count} consumos.")
print(f"Migrated {fac_count} facturas.")
print("All data migrated to fenix_v2.db successfully.")
