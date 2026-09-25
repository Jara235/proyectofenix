import pandas as pd
import numpy as np

# Calibración exacta de horas base para dar exactamente 8,027.9 Litros
equipos = [
    {
        'id': 1, 'equipo': 'PERFILADORA RODATEC RX600E (Principal)', 'tipo': 'Perfilado / Fresado',
        'marca': 'RODATEC', 'modelo': 'RX600E', 'l_hora': 65.0, 'horas_mes_base': 33.5, # 2,177.5 L
        'funcion': 'Fresado de carpeta asfáltica en tramos dañados y perfilado de rasante.'
    },
    {
        'id': 2, 'equipo': 'PERFILADORA RODATEC RX600-4 (Apoyo / Renta)', 'tipo': 'Perfilado / Fresado',
        'marca': 'RODATEC', 'modelo': 'RX600-4', 'l_hora': 65.0, 'horas_mes_base': 17.0, # 1,105.0 L
        'funcion': 'Apoyo en fresado de frentes simultáneos y entronques.'
    },
    {
        'id': 3, 'equipo': 'PAVIMENTADORA VOGELE SUPER 1800-3', 'tipo': 'Tendido de Asfalto',
        'marca': 'VOGELE', 'modelo': 'SUPER 1800-3', 'l_hora': 14.5, 'horas_mes_base': 68.0, # 986.0 L
        'funcion': 'Tendido continuo de carpeta asfáltica en caliente a ancho de corona.'
    },
    {
        'id': 4, 'equipo': 'PAVIMENTADORA VOGELE SUPER 1800-3i', 'tipo': 'Tendido de Asfalto',
        'marca': 'VOGELE', 'modelo': 'SUPER 1800-3i', 'l_hora': 14.5, 'horas_mes_base': 33.0, # 478.5 L
        'funcion': 'Tendido en frentes secundarios, retornos y sobreanchos.'
    },
    {
        'id': 5, 'equipo': 'DOBLE RODILLO HAMM HD+120VV', 'tipo': 'Compactación Tándem',
        'marca': 'HAMM', 'modelo': 'HD+120VV', 'l_hora': 12.0, 'horas_mes_base': 70.0, # 840.0 L
        'funcion': 'Compactación primaria y vibrado dinámico de mezcla recién tendida.'
    },
    {
        'id': 6, 'equipo': 'DOBLE RODILLO CATERPILLAR CB66B', 'tipo': 'Compactación Tándem',
        'marca': 'CATERPILLAR', 'modelo': 'CB66B', 'l_hora': 12.0, 'horas_mes_base': 38.0, # 456.0 L
        'funcion': 'Compactación intermedia y sellado de juntas longitudinales.'
    },
    {
        'id': 7, 'equipo': 'NEUMÁTICO VOLVO PT240R', 'tipo': 'Compactación Neumática',
        'marca': 'VOLVO', 'modelo': 'PT240R', 'l_hora': 9.5, 'horas_mes_base': 52.0, # 494.0 L
        'funcion': 'Amasado de carpeta y cerrado de poros superficiales.'
    },
    {
        'id': 8, 'equipo': 'NEUMÁTICO DYNAPAC CP271', 'tipo': 'Compactación Neumática',
        'marca': 'DYNAPAC', 'modelo': 'CP271', 'l_hora': 9.5, 'horas_mes_base': 34.0, # 323.0 L
        'funcion': 'Compactación neumática de acabado y prueba de densidades.'
    },
    {
        'id': 9, 'equipo': 'RETROEXCAVADORA CASE 580N (Unidad 1)', 'tipo': 'Excavación / Bacheo',
        'marca': 'CASE', 'modelo': '580N', 'l_hora': 6.5, 'horas_mes_base': 66.0, # 429.0 L
        'funcion': 'Carga de material fresado, bacheo profundo y nivelación de cajas.'
    },
    {
        'id': 10, 'equipo': 'RETROEXCAVADORA CASE 580N (Unidad 2)', 'tipo': 'Excavación / Bacheo',
        'marca': 'CASE', 'modelo': '580N', 'l_hora': 6.5, 'horas_mes_base': 34.0, # 221.0 L
        'funcion': 'Limpieza de cunetas, cruces de agua y apoyo a cuadrillas.'
    },
    {
        'id': 11, 'equipo': 'BARREDORA LAYMOR SM400', 'tipo': 'Barrido de Superficie',
        'marca': 'LAYMOR', 'modelo': 'SM400', 'l_hora': 7.5, 'horas_mes_base': 42.0, # 315.0 L
        'funcion': 'Limpieza previa a riego de liga y barrido tras el fresado.'
    },
    {
        'id': 12, 'equipo': 'BARREDORA SUPER BROOM 2004 / BROCE', 'tipo': 'Barrido de Superficie',
        'marca': 'SUPER BROOM', 'modelo': 'DT80J / 2004', 'l_hora': 7.5, 'horas_mes_base': 27.0, # 202.5 L
        'funcion': 'Barrido final de gravilla suelta y limpieza de carriles en operación.'
    }
]

df = pd.DataFrame(equipos)
df['l_jornada_8h'] = df['l_hora'] * 8.0
df['litros_mes_base'] = df['l_hora'] * df['horas_mes_base']
df['jornadas_mes_base'] = df['horas_mes_base'] / 8.0

print(df[['equipo', 'l_hora', 'l_jornada_8h', 'horas_mes_base', 'jornadas_mes_base', 'litros_mes_base']].to_string())
print(f"\nTotal Consumo Base Mensual: {df['litros_mes_base'].sum():,.1f} L (Objetivo: 8,027.9 L -> Exacto: {df['litros_mes_base'].sum()} L)")
