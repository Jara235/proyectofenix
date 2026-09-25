import psycopg2
from psycopg2.extras import DictCursor
import pandas as pd

conn = psycopg2.connect(
    dbname="fenix_db",
    user="postgres",
    password="Bupito*268",
    host="localhost"
)

# 1. Total overview of gasolina.consumos
df_gas = pd.read_sql("""
    SELECT 
        id, fecha, semana, origen, obra_destino, vehiculo, placa,
        litros, costo_por_litro, importe_total, conductor, gasolineria, estatus_revision
    FROM gasolina.consumos
""", conn)

print("=== OVERVIEW GASOLINA.CONSUMOS ===")
print(f"Total registros: {len(df_gas)}")
print(f"Semanas registradas: {sorted(df_gas['semana'].dropna().unique().tolist())}")
print(f"Total Litros: {df_gas['litros'].sum():,.2f} L")
print(f"Total Importe: ${df_gas['importe_total'].sum():,.2f}")
print(f"Costo promedio por litro: ${df_gas['costo_por_litro'].mean():.2f}")

# 2. Consumo por Obra en Gasolina
df_obras_gas = df_gas.groupby('obra_destino').agg(
    total_litros=('litros', 'sum'),
    total_importe=('importe_total', 'sum'),
    cargas=('id', 'count'),
    promedio_litros_carga=('litros', 'mean')
).sort_values(by='total_litros', ascending=False)

print("\n=== TOP OBRAS POR CONSUMO DE GASOLINA ===")
print(df_obras_gas.to_string())

# 3. Consumo promedio semanal por Obra en Gasolina
df_gas_semana = df_gas.groupby(['obra_destino', 'semana']).agg(
    litros_semana=('litros', 'sum')
).reset_index()

df_gas_stats = df_gas_semana.groupby('obra_destino').agg(
    semanas_activas=('semana', 'count'),
    promedio_semanal_litros=('litros_semana', 'mean'),
    min_semanal_litros=('litros_semana', 'min'),
    max_semanal_litros=('litros_semana', 'max'),
    std_semanal_litros=('litros_semana', 'std')
).sort_values(by='promedio_semanal_litros', ascending=False)

print("\n=== PROMEDIO SEMANAL Y VARIABILIDAD EN GASOLINA POR OBRA ===")
print(df_gas_stats.to_string())

conn.close()
