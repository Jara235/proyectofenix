import pandas as pd
import numpy as np

# Catálogo calibrado de los 12 equipos con sus horas base mensuales (mes base = 1.0x)
equipos = [
    {'id': 1, 'nombre': 'Perfiladora Rodatec RX600E (Principal)', 'tipo': 'Fresado', 'l_hora': 65.0, 'horas_base': 33.5},
    {'id': 2, 'nombre': 'Perfiladora Rodatec RX600-4 (Apoyo)', 'tipo': 'Fresado', 'l_hora': 65.0, 'horas_base': 17.0},
    {'id': 3, 'nombre': 'Pavimentadora Vögele Super 1800-3 (Principal)', 'tipo': 'Pavimentación', 'l_hora': 14.5, 'horas_base': 68.0},
    {'id': 4, 'nombre': 'Pavimentadora Vögele Super 1800-3i (Apoyo)', 'tipo': 'Pavimentación', 'l_hora': 14.5, 'horas_base': 33.0},
    {'id': 5, 'nombre': 'Doble Rodillo Hamm HD+120VV (Principal)', 'tipo': 'Compactación', 'l_hora': 12.0, 'horas_base': 70.0},
    {'id': 6, 'nombre': 'Doble Rodillo Caterpillar CB66B (Apoyo)', 'tipo': 'Compactación', 'l_hora': 12.0, 'horas_base': 38.0},
    {'id': 7, 'nombre': 'Compactador Neumático Volvo PT240R (Principal)', 'tipo': 'Compactación', 'l_hora': 9.5, 'horas_base': 52.0},
    {'id': 8, 'nombre': 'Compactador Neumático Dynapac CP271 (Apoyo)', 'tipo': 'Compactación', 'l_hora': 9.5, 'horas_base': 34.0},
    {'id': 9, 'nombre': 'Retroexcavadora Case 580N (Unidad 1)', 'tipo': 'Excavación/Bacheo', 'l_hora': 6.5, 'horas_base': 66.0},
    {'id': 10, 'nombre': 'Retroexcavadora Case 580N (Unidad 2)', 'tipo': 'Excavación/Bacheo', 'l_hora': 6.5, 'horas_base': 34.0},
    {'id': 11, 'nombre': 'Barredora Laymor SM400', 'tipo': 'Barrido/Limpieza', 'l_hora': 7.5, 'horas_base': 42.0},
    {'id': 12, 'nombre': 'Barredora Super Broom 2004 / Broce', 'tipo': 'Barrido/Limpieza', 'l_hora': 7.5, 'horas_base': 27.0},
]

# Factores de Lerma - Tres Marías de Marzo a Agosto:
meses = [
    {'mes': 'Marzo', 'factor': 1.161},
    {'mes': 'Abril', 'factor': 0.958},
    {'mes': 'Mayo', 'factor': 1.323},
    {'mes': 'Junio', 'factor': 0.650},
    {'mes': 'Julio', 'factor': 1.415},
    {'mes': 'Agosto', 'factor': 0.950},
]

res = []
for eq in equipos:
    h_base = eq['horas_base']
    h_mes = {}
    h_acum = 0
    bitacoras_200h_meses = []
    
    for m in meses:
        h = round(h_base * m['factor'], 1)
        h_mes[m['mes']] = h
        h_acum_prev = h_acum
        h_acum += h
        
        # Verificar si cruza múltiplos de 200 horas
        prev_count = int(h_acum_prev // 200)
        curr_count = int(h_acum // 200)
        if curr_count > prev_count:
            for k in range(prev_count + 1, curr_count + 1):
                bitacoras_200h_meses.append(f"{m['mes']} ({k*200}h)")
                
    num_200h = int(h_acum // 200)
    num_1000h = int(h_acum // 1000)
    num_2000h = int(h_acum // 2000)
    
    res.append({
        'id': eq['id'],
        'nombre': eq['nombre'],
        'tipo': eq['tipo'],
        'mar': h_mes['Marzo'],
        'abr': h_mes['Abril'],
        'may': h_mes['Mayo'],
        'jun': h_mes['Junio'],
        'jul': h_mes['Julio'],
        'ago': h_mes['Agosto'],
        'total_horas_6m': round(h_acum, 1),
        'bitacoras_200h': num_200h,
        'meses_200h': ", ".join(bitacoras_200h_meses) if bitacoras_200h_meses else "No alcanza 200h (Requiere acumulado anual)",
        'bitacoras_1000h': num_1000h,
        'bitacoras_2000h': num_2000h,
    })

df_res = pd.DataFrame(res)
print(df_res.to_string())
