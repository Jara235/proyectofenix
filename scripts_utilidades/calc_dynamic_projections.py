import pandas as pd
import numpy as np

# Tasas de referencia base mensual (Litros/mes en operación normal 1.00x)
# México-Toluca
MT_DIESEL_BASE = 10881.9
MT_GAS_BASE = 1701.9

# Lerma-Tres Marías
LT_DIESEL_BASE = 8027.9
LT_GAS_BASE = 1738.0

PRECIO_DIESEL = 27.00
PRECIO_GASOLINA = 23.90

# Factores dinámicos por mes
meses_factores = [
    {
        'mes': 'Enero',
        'dias': 31,
        'f_clima': 0.90, # Frío intenso matutino en montaña/Toluca retrasa colado de asfalto caliente
        'f_maq': 0.88,   # Reactivación y calibración de maquinaria tras receso
        'f_cal': 0.92,   # Arranque paulatino semana 1
        'f_gas_factor': 0.90, # Menos vueltas de supervisión
        'fase_obra': 'Arranque de Año y Mantenimientos'
    },
    {
        'mes': 'Febrero',
        'dias': 28,
        'f_clima': 0.98, # Clima seco favorable
        'f_maq': 1.00,   # Maquinaria al 100% de disponibilidad
        'f_cal': 0.90,   # Mes corto (28 días)
        'f_gas_factor': 0.92,
        'fase_obra': 'Operación Regular Creciente'
    },
    {
        'mes': 'Marzo',
        'dias': 31,
        'f_clima': 1.15, # Temporada seca óptima (estiaje), turnos extendidos
        'f_maq': 0.98,   # Operación continua
        'f_cal': 1.03,   # 22 días hábiles completos
        'f_gas_factor': 1.08,
        'fase_obra': 'Temporada Alta de Asfaltado (Estiaje)'
    },
    {
        'mes': 'Abril',
        'dias': 30,
        'f_clima': 1.12, # Clima seco y caluroso, ideal para mezcla
        'f_maq': 0.92,   # Mantenimiento preventivo intermedio (Semana Santa)
        'f_cal': 0.93,   # Paro de Semana Santa (Jueves/Viernes/Sábado)
        'f_gas_factor': 0.95,
        'fase_obra': 'Avance Fuerte / Paro Semana Santa'
    },
    {
        'mes': 'Mayo',
        'dias': 31,
        'f_clima': 1.20, # Clima seco óptimo previo a lluvias, máxima aceleración
        'f_maq': 1.05,   # Dobles turnos, frentes nocturnos de fresado y tendido
        'f_cal': 1.05,   # Máxima actividad en días hábiles
        'f_gas_factor': 1.15,
        'fase_obra': 'Mes Pico de Producción y Rendimiento'
    },
    {
        'mes': 'Junio',
        'dias': 30,
        'f_clima': 0.78, # Inicio de lluvias intensas (paros forzados de tendido de asfalto)
        'f_maq': 0.85,   # Entrada a taller de equipos para mantenimiento mayor
        'f_cal': 0.98,   # Días hábiles estándar
        'f_gas_factor': 0.88,
        'fase_obra': 'Temporada de Lluvias y Mantenimiento Mayor'
    }
]

resultados = []
for m in meses_factores:
    f_comp_diesel = m['f_clima'] * m['f_maq'] * m['f_cal']
    f_comp_gas = (m['f_clima'] * 0.4 + m['f_cal'] * 0.6) * m['f_gas_factor'] # Gasolina varía menos por clima pero sí por supervisión
    
    # México - Toluca
    mt_d_lts = MT_DIESEL_BASE * f_comp_diesel
    mt_d_imp = mt_d_lts * PRECIO_DIESEL
    mt_g_lts = MT_GAS_BASE * f_comp_gas
    mt_g_imp = mt_g_lts * PRECIO_GASOLINA
    mt_tot_imp = mt_d_imp + mt_g_imp
    
    # Lerma - Tres Marías
    lt_d_lts = LT_DIESEL_BASE * f_comp_diesel
    lt_d_imp = lt_d_lts * PRECIO_DIESEL
    lt_g_lts = LT_GAS_BASE * f_comp_gas
    lt_g_imp = lt_g_lts * PRECIO_GASOLINA
    lt_tot_imp = lt_d_imp + lt_g_imp
    
    # Consolidado
    tot_d_lts = mt_d_lts + lt_d_lts
    tot_d_imp = mt_d_imp + lt_d_imp
    tot_g_lts = mt_g_lts + lt_g_lts
    tot_g_imp = mt_g_imp + lt_g_imp
    gran_tot = tot_d_imp + tot_g_imp
    
    resultados.append({
        'Mes': m['mes'],
        'Fase de Obra': m['fase_obra'],
        'Factor_Diesel': round(f_comp_diesel, 3),
        'Factor_Gasolina': round(f_comp_gas, 3),
        'MT_Diesel_Lts': round(mt_d_lts, 1),
        'MT_Diesel_Imp': round(mt_d_imp, 2),
        'MT_Gas_Lts': round(mt_g_lts, 1),
        'MT_Gas_Imp': round(mt_g_imp, 2),
        'MT_Total_Imp': round(mt_tot_imp, 2),
        'LT_Diesel_Lts': round(lt_d_lts, 1),
        'LT_Diesel_Imp': round(lt_d_imp, 2),
        'LT_Gas_Lts': round(lt_g_lts, 1),
        'LT_Gas_Imp': round(lt_g_imp, 2),
        'LT_Total_Imp': round(lt_tot_imp, 2),
        'Tot_Diesel_Lts': round(tot_d_lts, 1),
        'Tot_Diesel_Imp': round(tot_d_imp, 2),
        'Tot_Gas_Lts': round(tot_g_lts, 1),
        'Tot_Gas_Imp': round(tot_g_imp, 2),
        'Gran_Total_Imp': round(gran_tot, 2)
    })

df_dyn = pd.DataFrame(resultados)
print("=== ESTIMACIÓN DINÁMICA MULTIFACTORIAL (ENERO - JUNIO) ===")
cols_show = ['Mes', 'Factor_Diesel', 'Tot_Diesel_Lts', 'Tot_Diesel_Imp', 'Tot_Gas_Lts', 'Tot_Gas_Imp', 'Gran_Total_Imp']
print(df_dyn[cols_show].to_string())

print("\n=== TOTALES DEL SEMESTRE (MODELO DINÁMICO) ===")
print(f"Total Diesel Litros: {df_dyn['Tot_Diesel_Lts'].sum():,.1f} L")
print(f"Total Diesel Importe: ${df_dyn['Tot_Diesel_Imp'].sum():,.2f} MXN")
print(f"Total Gasolina Litros: {df_dyn['Tot_Gas_Lts'].sum():,.1f} L")
print(f"Total Gasolina Importe: ${df_dyn['Tot_Gas_Imp'].sum():,.2f} MXN")
print(f"Gran Total Semestre: ${df_dyn['Gran_Total_Imp'].sum():,.2f} MXN")
