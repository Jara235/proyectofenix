import psycopg2
from psycopg2.extras import DictCursor
import pandas as pd

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

# ── DIESEL ──
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
        importe_total
    FROM diesel.consumos
    WHERE (obra_destino ILIKE '%TOLUCA%' AND obra_destino NOT ILIKE '%BACHEO%')
       OR obra_destino ILIKE '%LERMA%'
""")
df_d = pd.DataFrame([dict(r) for r in cur.fetchall()])
df_d['litros'] = df_d['litros'].astype(float)
df_d['importe_total'] = df_d['importe_total'].astype(float)

# ── GASOLINA ──
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
        importe_total
    FROM gasolina.consumos
    WHERE ((obra_destino ILIKE '%TOLUCA%' AND obra_destino NOT ILIKE '%BACHEO%')
       OR obra_destino ILIKE '%LERMA%')
       AND (costo_por_litro > 0 OR importe_total > 0)
       AND (vehiculo != 'S/P' OR vehiculo IS NULL)
""")
df_g = pd.DataFrame([dict(r) for r in cur.fetchall()])
df_g['litros'] = df_g['litros'].astype(float)
df_g['importe_total'] = df_g['importe_total'].astype(float)

# Análisis por mes
print("=== DIESEL POR MES ===")
print(df_d.groupby(['obra', 'mes'])[['litros', 'importe_total']].sum())

print("\n=== GASOLINA POR MES ===")
print(df_g.groupby(['obra', 'mes'])[['litros', 'importe_total']].sum())

# Análisis por semanas activas
semanas_d_mt = df_d[df_d['obra'] == 'MÉXICO-TOLUCA']['semana'].nunique()
semanas_d_lt = df_d[df_d['obra'] == 'LERMA-TRES MARÍAS']['semana'].nunique()
semanas_g_mt = df_g[df_g['obra'] == 'MÉXICO-TOLUCA']['semana'].nunique()
semanas_g_lt = df_g[df_g['obra'] == 'LERMA-TRES MARÍAS']['semana'].nunique()

print("\nSemanas activas Diesel MT:", semanas_d_mt, "| Litros totales:", df_d[df_d['obra'] == 'MÉXICO-TOLUCA']['litros'].sum())
print("Semanas activas Diesel LT:", semanas_d_lt, "| Litros totales:", df_d[df_d['obra'] == 'LERMA-TRES MARÍAS']['litros'].sum())
print("Semanas activas Gasolina MT:", semanas_g_mt, "| Litros totales:", df_g[df_g['obra'] == 'MÉXICO-TOLUCA']['litros'].sum())
print("Semanas activas Gasolina LT:", semanas_g_lt, "| Litros totales:", df_g[df_g['obra'] == 'LERMA-TRES MARÍAS']['litros'].sum())

# Mes cerrado completo: Julio 2026 (Sem 27 a 31)
print("\n=== CONSUMO DEL MES COMPLETO (JULIO 2026) ===")
jul_d = df_d[df_d['mes'] == '2026-07'].groupby('obra')[['litros', 'importe_total']].sum()
jul_g = df_g[df_g['mes'] == '2026-07'].groupby('obra')[['litros', 'importe_total']].sum()
print("Diesel Julio:\n", jul_d)
print("Gasolina Julio:\n", jul_g)

conn.close()
