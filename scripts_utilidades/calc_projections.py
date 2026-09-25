import pandas as pd
import numpy as np

# Semanas en cada mes de Enero a Junio
meses_info = [
    {'mes': 'Enero', 'dias': 31, 'semanas': 31 / 7.0},
    {'mes': 'Febrero', 'dias': 28, 'semanas': 28 / 7.0},
    {'mes': 'Marzo', 'dias': 31, 'semanas': 31 / 7.0},
    {'mes': 'Abril', 'dias': 30, 'semanas': 30 / 7.0},
    {'mes': 'Mayo', 'dias': 31, 'semanas': 31 / 7.0},
    {'mes': 'Junio', 'dias': 30, 'semanas': 30 / 7.0},
]

# Tasas base semanales (Litros/semana) basadas en histórico real depurado
# MÉXICO-TOLUCA
mextol_diesel_lts_sem = 2511.20   # Promedio histórico real semanal
mextol_gas_lts_sem = 392.75       # Promedio histórico real semanal

# LERMA-TRES MARÍAS
lerma_diesel_lts_sem = 1852.59    # Promedio histórico real semanal
lerma_gas_lts_sem = 401.08        # Promedio histórico real semanal

# Precios promedio de mercado / contrato actual
PRECIO_DIESEL = 27.00
PRECIO_GASOLINA = 23.90

# Cálculos mensuales
proyeccion = []
for m in meses_info:
    sem = m['semanas']
    
    # México - Toluca
    mt_d_lts = mextol_diesel_lts_sem * sem
    mt_d_imp = mt_d_lts * PRECIO_DIESEL
    mt_g_lts = mextol_gas_lts_sem * sem
    mt_g_imp = mt_g_lts * PRECIO_GASOLINA
    mt_tot_imp = mt_d_imp + mt_g_imp
    
    # Lerma - Tres Marías
    lt_d_lts = lerma_diesel_lts_sem * sem
    lt_d_imp = lt_d_lts * PRECIO_DIESEL
    lt_g_lts = lerma_gas_lts_sem * sem
    lt_g_imp = lt_g_lts * PRECIO_GASOLINA
    lt_tot_imp = lt_d_imp + lt_g_imp
    
    # Totales del mes
    tot_diesel_lts = mt_d_lts + lt_d_lts
    tot_diesel_imp = mt_d_imp + lt_d_imp
    tot_gas_lts = mt_g_lts + lt_g_lts
    tot_gas_imp = mt_g_imp + lt_g_imp
    gran_total_imp = tot_diesel_imp + tot_gas_imp
    
    proyeccion.append({
        'Mes': m['mes'],
        'Días': m['dias'],
        'Semanas': round(sem, 2),
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
        'Tot_Diesel_Lts': round(tot_diesel_lts, 1),
        'Tot_Diesel_Imp': round(tot_diesel_imp, 2),
        'Tot_Gas_Lts': round(tot_gas_lts, 1),
        'Tot_Gas_Imp': round(tot_gas_imp, 2),
        'Gran_Total_Imp': round(gran_total_imp, 2),
    })

df_proj = pd.DataFrame(proyeccion)
print("=== TABLA DE PROYECCIÓN ENERO - JUNIO ===")
print(df_proj.to_string())

print("\n=== TOTALES SEMESTRE (ENERO - JUNIO) ===")
print("TOTAL DIESEL LITROS:", df_proj['Tot_Diesel_Lts'].sum())
print("TOTAL DIESEL IMPORTE ($):", f"${df_proj['Tot_Diesel_Imp'].sum():,.2f}")
print("TOTAL GASOLINA LITROS:", df_proj['Tot_Gas_Lts'].sum())
print("TOTAL GASOLINA IMPORTE ($):", f"${df_proj['Tot_Gas_Imp'].sum():,.2f}")
print("GRAN TOTAL COMBUSTIBLE ($):", f"${df_proj['Gran_Total_Imp'].sum():,.2f}")
