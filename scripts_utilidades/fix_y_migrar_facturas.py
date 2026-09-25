import psycopg2, sys, io
from datetime import datetime
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

MAESTRO_PATH = r"c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_DIESEL_NUEVO.xlsx"

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor()
print("Conectado a PostgreSQL")

# Resetear la secuencia del ID de la tabla facturas
cur.execute("SELECT MAX(id) FROM diesel.facturas")
max_id = cur.fetchone()[0]
print(f"Max ID actual en diesel.facturas: {max_id}")

# Buscar el nombre de la secuencia
cur.execute("SELECT pg_get_serial_sequence('diesel.facturas', 'id')")
seq_name = cur.fetchone()[0]
print(f"Secuencia: {seq_name}")

# Resetear la secuencia al valor correcto
cur.execute(f"SELECT setval('{seq_name}', {max_id})")
conn.commit()
print(f"Secuencia reseteada a {max_id}")

# Ahora leer las facturas del Excel que faltan
df_fac = pd.read_excel(MAESTRO_PATH, sheet_name='BD_FACTURAS')
df_fac['FOLIO_CONCILIACION'] = df_fac['FOLIO_CONCILIACION'].astype(str).str.strip()
df_fac = df_fac[~df_fac['FOLIO_CONCILIACION'].isin(['nan', '', 'None'])].copy()

cur.execute("SELECT folio_conciliacion FROM diesel.facturas")
folios_pg = set([r[0] for r in cur.fetchall()])
print(f"\nFacturas en Postgres: {len(folios_pg)}")

df_nuevas = df_fac[~df_fac['FOLIO_CONCILIACION'].isin(folios_pg)].copy()
print(f"Facturas nuevas a insertar: {len(df_nuevas)}")

ins = 0
err = 0
for idx, row in df_nuevas.iterrows():
    try:
        folio = str(row['FOLIO_CONCILIACION']).strip()
        folio_fac = str(row.get('FOLIO_FACTURA', '') or '').strip()
        if folio_fac == 'nan': folio_fac = None

        fecha = row.get('FECHA_FACTURA')
        if pd.isna(fecha) if not isinstance(fecha, str) else not fecha:
            fecha = None
        elif hasattr(fecha, 'date'):
            fecha = str(fecha.date())

        semana    = str(row.get('SEMANA', '') or '').strip() or None
        proveedor = str(row.get('PROVEEDOR', '') or '').strip() or None
        punto     = str(row.get('PUNTO_DE_CARGA', '') or '').strip() or None
        if semana == 'nan': semana = None
        if proveedor == 'nan': proveedor = None
        if punto == 'nan': punto = None

        litros  = float(row.get('LITROS_FACTURADOS', 0) or 0)
        precio  = float(row.get('PRECIO_UNITARIO', 0) or 0)
        importe = float(row.get('IMPORTE', 0) or 0)
        iva     = float(row.get('I.V.A', 0) or 0)
        total   = float(row.get('IMPORTE_TOTAL', 0) or 0)

        cur.execute("""
            INSERT INTO diesel.facturas (
                folio_conciliacion, folio_factura, fecha_factura, semana, proveedor,
                punto_de_carga, litros_facturados, precio_unitario, importe, iva,
                importe_total, estatus_revision
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (folio, folio_fac, fecha, semana, proveedor, punto, litros, precio, importe, iva, total, 'PENDIENTE'))
        ins += 1
    except Exception as e:
        err += 1
        conn.rollback()
        print(f"  ERROR fila {idx} ({row.get('FOLIO_CONCILIACION')}): {e}")

conn.commit()
print(f"\nFacturas: {ins} insertadas, {err} errores")

# RESUMEN FINAL
cur.execute("SELECT COUNT(*) FROM diesel.consumos")
print(f"\nFINAL diesel.consumos:  {cur.fetchone()[0]} registros")
cur.execute("SELECT COUNT(*) FROM diesel.facturas")
print(f"FINAL diesel.facturas:  {cur.fetchone()[0]} registros")
cur.execute("SELECT semana, COUNT(*) FROM diesel.consumos GROUP BY semana ORDER BY semana")
print("\nConsumos por semana:")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]}")
cur.execute("SELECT semana, COUNT(*), SUM(litros_facturados) FROM diesel.facturas GROUP BY semana ORDER BY semana")
print("\nFacturas por semana (Litros):")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]} facturas | {r[2]:.1f} Lts")

conn.close()
print("\nTodo completado!")
