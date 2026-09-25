import pandas as pd
import numpy as np

# Catálogo oficial de maquinaria solicitada con su rendimiento L/h
equipos = [
    {
        'id': 1,
        'equipo': 'PERFILADORA RODATEC RX600E (Principal)',
        'tipo': 'Fresado / Perfilado',
        'marca': 'RODATEC',
        'modelo': 'RX600E',
        'l_hora': 65.0,
        'tren': 'Tren de Fresado',
        'horas_mes_base': 35.0, # ~4.4 jornadas de fresado al mes
    },
    {
        'id': 2,
        'equipo': 'PERFILADORA RODATEC RX600-4 (Apoyo / Renta)',
        'tipo': 'Fresado / Perfilado',
        'marca': 'RODATEC',
        'modelo': 'RX600-4',
        'l_hora': 65.0,
        'tren': 'Tren de Fresado',
        'horas_mes_base': 18.0, # ~2.2 jornadas de apoyo
    },
    {
        'id': 3,
        'equipo': 'PAVIMENTADORA VOGELE SUPER 1800-3',
        'tipo': 'Tendido de Mezcla Asfáltica',
        'marca': 'VOGELE',
        'modelo': 'SUPER 1800-3',
        'l_hora': 14.5,
        'tren': 'Tren de Pavimentación',
        'horas_mes_base': 70.0, # ~8.8 jornadas al mes
    },
    {
        'id': 4,
        'equipo': 'PAVIMENTADORA VOGELE SUPER 1800-3i',
        'tipo': 'Tendido de Mezcla Asfáltica',
        'marca': 'VOGELE',
        'modelo': 'SUPER 1800-3i',
        'l_hora': 14.5,
        'tren': 'Tren de Pavimentación',
        'horas_mes_base': 35.0, # ~4.4 jornadas de apoyo/tiro continuo
    },
    {
        'id': 5,
        'equipo': 'DOBLE RODILLO HAMM HD+120VV',
        'tipo': 'Compactación Asfáltica Tándem',
        'marca': 'HAMM',
        'modelo': 'HD+120VV',
        'l_hora': 12.0,
        'tren': 'Tren de Compactación',
        'horas_mes_base': 72.0, # ~9.0 jornadas
    },
    {
        'id': 6,
        'equipo': 'DOBLE RODILLO CATERPILLAR CB66B',
        'tipo': 'Compactación Asfáltica Tándem',
        'marca': 'CATERPILLAR',
        'modelo': 'CB66B',
        'l_hora': 12.0,
        'tren': 'Tren de Compactación',
        'horas_mes_base': 40.0, # ~5.0 jornadas
    },
    {
        'id': 7,
        'equipo': 'NEUMÁTICO VOLVO PT240R',
        'tipo': 'Compactación Neumática / Sellado',
        'marca': 'VOLVO',
        'modelo': 'PT240R',
        'l_hora': 9.5,
        'tren': 'Tren de Compactación',
        'horas_mes_base': 55.0, # ~6.9 jornadas
    },
    {
        'id': 8,
        'equipo': 'NEUMÁTICO DYNAPAC CP271',
        'tipo': 'Compactación Neumática / Sellado',
        'marca': 'DYNAPAC',
        'modelo': 'CP271',
        'l_hora': 9.5,
        'tren': 'Tren de Compactación',
        'horas_mes_base': 35.0, # ~4.4 jornadas
    },
    {
        'id': 9,
        'equipo': 'RETROEXCAVADORA CASE 580N (Unidad 1)',
        'tipo': 'Carga / Despalme / Bacheo',
        'marca': 'CASE',
        'modelo': '580N',
        'l_hora': 6.5,
        'tren': 'Cuadrilla de Bacheo / Apoyo',
        'horas_mes_base': 68.0, # ~8.5 jornadas
    },
    {
        'id': 10,
        'equipo': 'RETROEXCAVADORA CASE 580N (Unidad 2)',
        'tipo': 'Carga / Despalme / Bacheo',
        'marca': 'CASE',
        'modelo': '580N',
        'l_hora': 6.5,
        'tren': 'Cuadrilla de Bacheo / Apoyo',
        'horas_mes_base': 35.0, # ~4.4 jornadas
    },
    {
        'id': 11,
        'equipo': 'BARREDORA LAYMOR SM400',
        'tipo': 'Limpieza y Barrido de Superficie',
        'marca': 'LAYMOR',
        'modelo': 'SM400',
        'l_hora': 7.5,
        'tren': 'Tren de Fresado / Limpieza',
        'horas_mes_base': 45.0, # ~5.6 jornadas
    },
    {
        'id': 12,
        'equipo': 'BARREDORA SUPER BROOM 2004 / BROCE',
        'tipo': 'Limpieza y Barrido de Superficie',
        'marca': 'SUPER BROOM',
        'modelo': 'DT80J / 2004',
        'l_hora': 7.5,
        'tren': 'Tren de Fresado / Limpieza',
        'horas_mes_base': 30.0, # ~3.8 jornadas
    }
]

df_eq = pd.DataFrame(equipos)
df_eq['l_jornada_8h'] = df_eq['l_hora'] * 8.0
df_eq['litros_mes_base'] = df_eq['l_hora'] * df_eq['horas_mes_base']
df_eq['jornadas_mes_base'] = df_eq['horas_mes_base'] / 8.0

total_lts_base = df_eq['litros_mes_base'].sum()
print("=== CATÁLOGO Y ESTIMACIÓN DE MAQUINARIA LERMA - TRES MARÍAS (MES BASE) ===")
print(df_eq[['equipo', 'l_hora', 'l_jornada_8h', 'horas_mes_base', 'jornadas_mes_base', 'litros_mes_base']].to_string())
print(f"\nTotal Litros Mes Base Calculado: {total_lts_base:,.1f} L (Meta de Referencia: 8,027.9 L)")

# Proyección por mes de horas y litros
meses_factores = [
    ('Enero', 0.729, 5845.5),
    ('Febrero', 0.882, 7080.6),
    ('Marzo', 1.161, 9320.4),
    ('Abril', 0.958, 7690.7),
    ('Mayo', 1.323, 10620.9),
    ('Junio', 0.650, 5218.1),
    ('Julio', 1.415, 11360.3),
    ('Agosto', 0.950, 7626.0)
]

print("\n=== DISTRIBUCIÓN MENSUAL ALINEADA ===")
for mes, factor, target in meses_factores:
    horas_totales = (df_eq['horas_mes_base'] * factor).sum()
    litros_totales = (df_eq['litros_mes_base'] * factor).sum()
    print(f"{mes:7} | Factor: {factor:.3f}x | Horas Máquina Totales: {horas_totales:>6.1f} hrs | Litros Calculados: {litros_totales:>8.1f} L | Meta: {target:>8.1f} L")
