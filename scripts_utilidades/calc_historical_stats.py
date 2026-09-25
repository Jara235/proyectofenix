import psycopg2
from psycopg2.extras import DictCursor
import pandas as pd
import numpy as np

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

# ── 1. DIESEL REAL POR MES Y SEMANA ──
cur.execute("""
    SELECT 
        CASE 
            WHEN obra_destino ILIKE '%TOLUCA%' AND obra_destino NOT ILIKE '%BACHEO%' THEN 'MÉXICO-TOLUCA'
            WHEN obra_destino ILIKE '%LERMA%' THEN 'LERMA-TRES MARÍAS'
            ELSE obra_destino 
        END as obra,
        TO_CHAR(TO_DATE(fecha, 'YYYY-MM-DD'), 'YYYY-MM') as mes,
        semana,
        litros,
        costo_por_litro,
        importe_total,
        equipo,
        responsable
    FROM diesel.consumos
    WHERE (obra_destino ILIKE '%TOLUCA%' AND obra_destino NOT ILIKE '%BACHEO%')
       OR obra_destino ILIKE '%LERMA%'
    ORDER BY obra, fecha;
""")
diesel_rows = cur.fetchall()
df_diesel = pd.DataFrame([dict(r) for r in diesel_rows])
df_diesel['litros'] = df_diesel['litros'].astype(float)
df_diesel['importe_total'] = df_diesel['importe_total'].astype(float)
df_diesel['costo_por_litro'] = df_diesel['costo_por_litro'].astype(float)

# ── 2. GASOLINA REAL POR MES Y SEMANA ──
# Note: filter out the S/P bulk diesel tickets captured in gasolina (costo == 0 or litros > 250)
cur.execute("""
    SELECT 
        CASE 
            WHEN obra_destino ILIKE '%TOLUCA%' AND obra_destino NOT ILIKE '%BACHEO%' THEN 'MÉXICO-TOLUCA'
            WHEN obra_destino ILIKE '%LERMA%' THEN 'LERMA-TRES MARÍAS'
            ELSE obra_destino 
        END as obra,
        TO_CHAR(TO_DATE(fecha, 'YYYY-MM-DD'), 'YYYY-MM') as mes,
        semana,
        litros,
        costo_por_litro,
        importe_total,
        vehiculo,
        conductor
    FROM gasolina.consumos
    WHERE ((obra_destino ILIKE '%TOLUCA%' AND obra_destino NOT ILIKE '%BACHEO%')
       OR obra_destino ILIKE '%LERMA%')
       AND (costo_por_litro > 0 OR importe_total > 0)
       AND (vehiculo != 'S/P' OR vehiculo IS NULL)
    ORDER BY obra, fecha;
""")
gasolina_rows = cur.fetchall()
df_gas = pd.DataFrame([dict(r) for r in gasolina_rows])
df_gas['litros'] = df_gas['litros'].astype(float)
df_gas['importe_total'] = df_gas['importe_total'].astype(float)
df_gas['costo_por_litro'] = df_gas['costo_por_litro'].astype(float)

print("=== RESUMEN REAL DIESEL POR MES ===")
res_diesel_mes = df_diesel.groupby(['obra', 'mes']).agg(
    cargas=('litros', 'count'),
    litros=('litros', 'sum'),
    importe=('importe_total', 'sum'),
    precio_prom=('costo_por_litro', 'mean')
).reset_index()
print(res_diesel_mes)

print("\n=== RESUMEN REAL DIESEL POR SEMANA ===")
res_diesel_sem = df_diesel.groupby(['obra', 'semana']).agg(
    cargas=('litros', 'count'),
    litros=('litros', 'sum'),
    importe=('importe_total', 'sum')
).reset_index()
print(res_diesel_sem)

print("\n=== RESUMEN REAL GASOLINA POR MES ===")
res_gas_mes = df_gas.groupby(['obra', 'mes']).agg(
    cargas=('litros', 'count'),
    litros=('litros', 'sum'),
    importe=('importe_total', 'sum'),
    precio_prom=('costo_por_litro', 'mean')
).reset_index()
print(res_gas_mes)

print("\n=== RESUMEN REAL GASOLINA POR SEMANA ===")
res_gas_sem = df_gas.groupby(['obra', 'semana']).agg(
    cargas=('litros', 'count'),
    litros=('litros', 'sum'),
    importe=('importe_total', 'sum')
).reset_index()
print(res_gas_sem)

conn.close()
