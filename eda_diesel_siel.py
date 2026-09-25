import psycopg2
from psycopg2.extras import DictCursor
import json
import pandas as pd

conn = psycopg2.connect(
    dbname="fenix_db",
    user="postgres",
    password="Bupito*268",
    host="localhost"
)

# 1. Total overview of diesel.consumos
df_consumos = pd.read_sql("""
    SELECT 
        id, fecha, semana, origen, tipo_movimiento, obra_destino, 
        equipo, equipo_economico, litros, costo_por_litro, importe_total, 
        responsable, operador, estatus_revision
    FROM diesel.consumos
""", conn)

print("=== OVERVIEW DIESEL.CONSUMOS ===")
print(f"Total registros: {len(df_consumos)}")
print(f"Semanas registradas: {sorted(df_consumos['semana'].dropna().unique().tolist())}")
print(f"Total Litros: {df_consumos['litros'].sum():,.2f} L")
print(f"Total Importe: ${df_consumos['importe_total'].sum():,.2f}")
print(f"Costo promedio por litro: ${df_consumos['costo_por_litro'].mean():.2f}")

# 2. Consumo por Obra
df_obras = df_consumos.groupby('obra_destino').agg(
    total_litros=('litros', 'sum'),
    total_importe=('importe_total', 'sum'),
    cargas=('id', 'count'),
    promedio_litros_carga=('litros', 'mean'),
    equipos_unicos=('equipo_economico', 'nunique')
).sort_values(by='total_litros', ascending=False)

print("\n=== TOP 10 OBRAS POR CONSUMO DE DIESEL ===")
print(df_obras.head(15).to_string())

# 3. Consumo promedio semanal por Obra
df_obra_semana = df_consumos.groupby(['obra_destino', 'semana']).agg(
    litros_semana=('litros', 'sum')
).reset_index()

df_obra_stats = df_obra_semana.groupby('obra_destino').agg(
    semanas_activas=('semana', 'count'),
    promedio_semanal_litros=('litros_semana', 'mean'),
    min_semanal_litros=('litros_semana', 'min'),
    max_semanal_litros=('litros_semana', 'max'),
    std_semanal_litros=('litros_semana', 'std')
).sort_values(by='promedio_semanal_litros', ascending=False)

print("\n=== PROMEDIO SEMANAL Y VARIABILIDAD POR OBRA ===")
print(df_obra_stats.head(15).to_string())

# 4. Consumo por tipo de equipo / maquinaria
df_equipos = df_consumos.groupby(['equipo_economico', 'equipo']).agg(
    total_litros=('litros', 'sum'),
    cargas=('id', 'count'),
    promedio_litros_por_carga=('litros', 'mean')
).sort_values(by='total_litros', ascending=False)

print("\n=== TOP 15 EQUIPOS CON MAYOR CONSUMO ===")
print(df_equipos.head(15).to_string())

# 5. Check bitácora maquinaria
df_bitacora = pd.read_sql("""
    SELECT * FROM catalogos.bitacora_maquinaria
""", conn)
print(f"\n=== BITACORA MAQUINARIA ({len(df_bitacora)} registros) ===")
if len(df_bitacora) > 0:
    print(df_bitacora[['fecha', 'semana', 'equipo_maquinaria', 'horas_trabajadas', 'litros_diesel_est', 'obra_destino']].to_string())

# 6. Check diesel.jalisco_movimientos
df_jalisco = pd.read_sql("""
    SELECT * FROM diesel.jalisco_movimientos
""", conn)
print(f"\n=== JALISCO MOVIMIENTOS ({len(df_jalisco)} registros) ===")
print(f"Total Litros Jalisco: {df_jalisco['litros'].sum():,.2f} L")
print(f"Total Importe Jalisco: ${df_jalisco['importe_total'].sum():,.2f}")

conn.close()
