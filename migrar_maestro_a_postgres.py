import psycopg2
import pandas as pd
import sys, io
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

MAESTRO_PATH = r"c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_DIESEL_NUEVO.xlsx"

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor()
print("Conectado a PostgreSQL")

# ─────────────────────────────────────────
# Agregar UNIQUE constraint a facturas si no existe
# ─────────────────────────────────────────
try:
    cur.execute("ALTER TABLE diesel.facturas ADD CONSTRAINT facturas_folio_unique UNIQUE (folio_conciliacion)")
    conn.commit()
    print("Constraint UNIQUE agregado a diesel.facturas.folio_conciliacion")
except Exception as e:
    conn.rollback()
    print(f"Constraint ya existe o error: {e}")

# ─────────────────────────────────────────
# 1. MIGRAR CONSUMOS
# ─────────────────────────────────────────
print("\n=== MIGRANDO CONSUMOS ===")
df = pd.read_excel(MAESTRO_PATH, sheet_name='BD_DIESEL')

# Filtro estricto: solo filas con folio valido
df['FOLIO_CONCILIACION'] = df['FOLIO_CONCILIACION'].astype(str).str.strip()
df_validos = df[
    df['FOLIO_CONCILIACION'].notna() & 
    (df['FOLIO_CONCILIACION'] != 'nan') & 
    (df['FOLIO_CONCILIACION'] != '') & 
    (df['FOLIO_CONCILIACION'] != 'None') &
    (df['LITROS'].notna()) &
    (df['LITROS'] > 0)
].copy()
print(f"  Filas validas en Excel: {len(df_validos)}")

cur.execute("SELECT folio_conciliacion FROM diesel.consumos WHERE folio_conciliacion IS NOT NULL")
folios_pg = set([r[0] for r in cur.fetchall()])
print(f"  Ya en Postgres: {len(folios_pg)}")

df_nuevos = df_validos[~df_validos['FOLIO_CONCILIACION'].isin(folios_pg)].copy()
print(f"  Nuevos a insertar: {len(df_nuevos)}")

insertados = 0
errores = 0

for idx, row in df_nuevos.iterrows():
    try:
        folio = str(row['FOLIO_CONCILIACION']).strip()
        
        fecha = row.get('FECHA')
        if pd.isna(fecha) if not isinstance(fecha, str) else not fecha:
            fecha = None
        elif hasattr(fecha, 'date'):
            fecha = str(fecha.date())
        elif isinstance(fecha, str):
            fecha = fecha[:10]
        
        semana   = str(row.get('SEMANA', '') or '').strip() or None
        origen   = str(row.get('ORIGEN', '') or '').strip() or None
        tipo_mov = str(row.get('TIPO_MOVIMIENTO', '') or '').strip() or 'CARGA MAQUINARIA'
        obra     = str(row.get('OBRA_DESTINO', '') or '').strip() or None
        equipo   = str(row.get('EQUIPO', '') or '').strip() or None
        equipo_e = str(row.get('EQUIPO_ECONOMICO', '') or '').strip() or None
        
        # Corregir 'nan' strings
        for field in [semana, origen, tipo_mov, obra, equipo, equipo_e]:
            if field == 'nan': field = None
        if semana == 'nan': semana = None
        if origen == 'nan': origen = None
        if tipo_mov == 'nan': tipo_mov = 'CARGA MAQUINARIA'
        if obra == 'nan': obra = None
        if equipo == 'nan': equipo = None
        if equipo_e == 'nan': equipo_e = None

        litros       = float(row.get('LITROS', 0) or 0)
        costo_litro  = float(row.get('COSTO_POR_LITRO', 27) or 27)
        importe      = float(row.get('IMPORTE_TOTAL', 0) or 0) or (litros * costo_litro)
        responsable  = str(row.get('RESPONSABLE', '') or '').strip() or None
        operador     = str(row.get('OPERADOR', '') or '').strip() or None
        estatus      = str(row.get('ESTATUS_CONCILIACION', '') or '').strip() or 'PENDIENTE'
        obs          = str(row.get('OBSERVACIONES', '') or '').strip() or None
        if responsable == 'nan': responsable = None
        if operador == 'nan': operador = None
        if estatus == 'nan': estatus = 'PENDIENTE'
        if obs == 'nan': obs = None

        cur.execute("""
            INSERT INTO diesel.consumos (
                folio_conciliacion, fecha, semana, origen, tipo_movimiento,
                obra_destino, equipo, equipo_economico, litros, costo_por_litro,
                importe_total, responsable, operador, estatus_revision, observaciones
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (folio, fecha, semana, origen, tipo_mov, obra, equipo, equipo_e,
              litros, costo_litro, importe, responsable, operador, estatus, obs))
        
        insertados += 1
        if insertados % 50 == 0:
            conn.commit()
            print(f"  ... {insertados} insertados")
            
    except Exception as e:
        errores += 1
        conn.rollback()
        if errores <= 3:  # Solo mostrar primeros 3 errores
            print(f"  ERROR fila {idx}: {e}")

conn.commit()
print(f"\n  Consumos: {insertados} insertados, {errores} errores")

# ─────────────────────────────────────────
# 2. MIGRAR FACTURAS DEL EXCEL
# ─────────────────────────────────────────
print("\n=== MIGRANDO FACTURAS DEL EXCEL ===")
df_fac = pd.read_excel(MAESTRO_PATH, sheet_name='BD_FACTURAS')
df_fac['FOLIO_CONCILIACION'] = df_fac['FOLIO_CONCILIACION'].astype(str).str.strip()
df_fac = df_fac[~df_fac['FOLIO_CONCILIACION'].isin(['nan', '', 'None'])].copy()
print(f"  Facturas validas en Excel: {len(df_fac)}")

cur.execute("SELECT folio_conciliacion FROM diesel.facturas WHERE folio_conciliacion IS NOT NULL")
folios_fac_pg = set([r[0] for r in cur.fetchall()])
print(f"  Ya en Postgres: {len(folios_fac_pg)}")

df_fac_nuevas = df_fac[~df_fac['FOLIO_CONCILIACION'].isin(folios_fac_pg)].copy()
print(f"  Nuevas a insertar: {len(df_fac_nuevas)}")

ins_fac = 0
err_fac = 0

for idx, row in df_fac_nuevas.iterrows():
    try:
        folio     = str(row['FOLIO_CONCILIACION']).strip()
        folio_fac = str(row.get('FOLIO_FACTURA', '') or '').strip() or None
        if folio_fac == 'nan': folio_fac = None
        
        fecha = row.get('FECHA_FACTURA')
        if pd.isna(fecha) if not isinstance(fecha, str) else not fecha:
            fecha = None
        elif hasattr(fecha, 'date'):
            fecha = str(fecha.date())
        
        semana     = str(row.get('SEMANA', '') or '').strip() or None
        proveedor  = str(row.get('PROVEEDOR', '') or '').strip() or None
        punto      = str(row.get('PUNTO_DE_CARGA', '') or '').strip() or None
        for f in ['nan']:
            if semana == f: semana = None
            if proveedor == f: proveedor = None
            if punto == f: punto = None
        
        litros  = float(row.get('LITROS_FACTURADOS', 0) or 0)
        precio  = float(row.get('PRECIO_UNITARIO', 0) or 0)
        importe = float(row.get('IMPORTE', 0) or 0)
        iva     = float(row.get('I.V.A', 0) or 0)
        total   = float(row.get('IMPORTE_TOTAL', 0) or 0)
        
        # Verificar si ya existe antes de insertar (folio_conciliacion ya tiene UNIQUE constraint)
        cur.execute("SELECT id FROM diesel.facturas WHERE folio_conciliacion = %s", (folio,))
        if cur.fetchone():
            continue  # Ya existe, saltar
        
        cur.execute("""
            INSERT INTO diesel.facturas (
                folio_conciliacion, folio_factura, fecha_factura, semana, proveedor,
                punto_de_carga, litros_facturados, precio_unitario, importe, iva,
                importe_total, estatus_revision
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (folio, folio_fac, fecha, semana, proveedor, punto, litros, precio, importe, iva, total, 'PENDIENTE'))
        
        ins_fac += 1
    except Exception as e:
        err_fac += 1
        conn.rollback()
        if err_fac <= 3:
            print(f"  ERROR factura fila {idx}: {e}")

conn.commit()
print(f"  Facturas: {ins_fac} insertadas, {err_fac} errores")

# ─────────────────────────────────────────
# VERIFICACION FINAL
# ─────────────────────────────────────────
cur.execute("SELECT COUNT(*) FROM diesel.consumos")
total_consumos = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM diesel.facturas")
total_facturas = cur.fetchone()[0]
cur.execute("SELECT semana, COUNT(*) FROM diesel.consumos GROUP BY semana ORDER BY semana")
resumen = cur.fetchall()

print(f"\n=== VERIFICACION FINAL ===")
print(f"  diesel.consumos:  {total_consumos} registros")
print(f"  diesel.facturas:  {total_facturas} registros")
print(f"\n  Consumos por semana:")
for r in resumen:
    print(f"    {r[0]}: {r[1]}")

cur.close()
conn.close()
print("\nMigracion completada!")
