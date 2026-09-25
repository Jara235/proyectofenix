import pandas as pd
import numpy as np

# Referencias individuales por obra
# MÉXICO - TOLUCA
REF_MT_DIESEL_LTS = 10881.9
REF_MT_DIESEL_IMP = 293810.40
REF_MT_GAS_LTS = 1701.9
REF_MT_GAS_IMP = 40676.00
REF_MT_TOT_LTS = REF_MT_DIESEL_LTS + REF_MT_GAS_LTS # 12,583.8 L
REF_MT_TOT_IMP = REF_MT_DIESEL_IMP + REF_MT_GAS_IMP # $334,486.40 MXN

# LERMA - TRES MARÍAS
REF_LT_DIESEL_LTS = 8027.9
REF_LT_DIESEL_IMP = 216753.00
REF_LT_GAS_LTS = 1738.0
REF_LT_GAS_IMP = 41538.50
REF_LT_TOT_LTS = REF_LT_DIESEL_LTS + REF_LT_GAS_LTS # 9,765.9 L
REF_LT_TOT_IMP = REF_LT_DIESEL_IMP + REF_LT_GAS_IMP # $258,291.50 MXN

meses_mt = [
    {
        'mes': 'Enero', 'd_lts': 7932.9, 'd_imp': 214188.30, 'g_lts': 1395.6, 'g_imp': 33354.84, 'tot_imp': 247543.14,
        'razon': 'Heladas matutinas en el tramo de montaña y La Marquesa retrasan el arranque de fresado y tendido hasta las 10:30 hrs. Arranque escalonado.'
    },
    {
        'mes': 'Febrero', 'd_lts': 9597.8, 'd_imp': 259140.60, 'g_lts': 1457.8, 'g_imp': 34841.42, 'tot_imp': 293982.02,
        'razon': 'Operación en ascenso con buen clima seco, pero mes corto de 28 días (20 días hábiles) reduce el volumen acumulado.'
    },
    {
        'mes': 'Marzo', 'd_lts': 12633.9, 'd_imp': 341115.30, 'g_lts': 1979.0, 'g_imp': 47298.10, 'tot_imp': 388413.40,
        'razon': 'Estiaje pleno en autopista México-Toluca: frentes continuos de fresado nocturno y tiros largos de mezcla asfáltica sin lluvia.'
    },
    {
        'mes': 'Abril', 'd_lts': 10424.9, 'd_imp': 281472.30, 'g_lts': 1624.5, 'g_imp': 38825.55, 'tot_imp': 320297.85,
        'razon': 'Buen avance físico pero ajustado por el paro de Semana Santa y cambio de picas en la perfiladora de asfalto.'
    },
    {
        'mes': 'Mayo', 'd_lts': 14396.8, 'd_imp': 388713.60, 'g_lts': 2169.8, 'g_imp': 51858.22, 'tot_imp': 440571.82,
        'razon': 'MES PICO: Cierre acelerado de tramos de autopista antes de lluvias. Pavimentadora Vögele y compactadores en dobles turnos continuos.'
    },
    {
        'mes': 'Junio', 'd_lts': 7073.2, 'd_imp': 190976.40, 'g_lts': 1346.2, 'g_imp': 32174.18, 'tot_imp': 223150.58,
        'razon': 'Inicio de lluvias y tormentas fuertes en zona alta (La Marquesa/Salazar), impidiendo el riego de liga y tendido; traslados a taller.'
    }
]

meses_lt = [
    {
        'mes': 'Enero', 'd_lts': 5845.5, 'd_imp': 157828.50, 'g_lts': 1427.9, 'g_imp': 34126.81, 'tot_imp': 191955.31,
        'razon': 'Temperaturas gélidas en la zona lacustre/sierra de Lerma; calibración y mantenimiento general de maquinaria pesada.'
    },
    {
        'mes': 'Febrero', 'd_lts': 7080.6, 'd_imp': 191176.20, 'g_lts': 1491.7, 'g_imp': 35651.63, 'tot_imp': 226827.83,
        'razon': 'Buen ritmo en tramos de terracería y base, pero limitado por 28 días naturales del mes.'
    },
    {
        'mes': 'Marzo', 'd_lts': 9320.4, 'd_imp': 251650.80, 'g_lts': 2025.9, 'g_imp': 48418.81, 'tot_imp': 300069.61,
        'razon': 'Condiciones óptimas de estiaje para carpeta asfáltica en carretera Lerma-Tres Marías, frentes activos de bacheo profundo y compactación.'
    },
    {
        'mes': 'Abril', 'd_lts': 7690.7, 'd_imp': 207648.90, 'g_lts': 1663.0, 'g_imp': 39745.70, 'tot_imp': 247394.60,
        'razon': 'Interrupción programada de frentes en Semana Santa, utilizada para mantenimiento de la petrolizadora y rodillos Hamm.'
    },
    {
        'mes': 'Mayo', 'd_lts': 10620.9, 'd_imp': 286764.30, 'g_lts': 2221.2, 'g_imp': 53086.68, 'tot_imp': 339850.98,
        'razon': 'MES PICO: Máxima intensidad para proteger terracerías y tender carpeta corrida antes del temporal en la sierra.'
    },
    {
        'mes': 'Junio', 'd_lts': 5218.1, 'd_imp': 140888.70, 'g_lts': 1378.2, 'g_imp': 32938.98, 'tot_imp': 173827.68,
        'razon': 'Temporal de lluvias en la sierra Lerma-Tres Marías frena colocación de emulsión y asfalto; cuadrillas se enfocan en desasolve/drenaje.'
    }
]

print("=== MÉXICO - TOLUCA ===")
for m in meses_mt:
    dif = m['tot_imp'] - REF_MT_TOT_IMP
    pct = (dif / REF_MT_TOT_IMP) * 100
    sup = "SÍ" if dif > 0 else "NO"
    print(f"{m['mes']:7} | Total: ${m['tot_imp']:>10,.2f} | Ref: ${REF_MT_TOT_IMP:>10,.2f} | Dif: ${dif:>10,.2f} ({pct:>+5.1f}%) | Supera: {sup}")

print("\n=== LERMA - TRES MARÍAS ===")
for m in meses_lt:
    dif = m['tot_imp'] - REF_LT_TOT_IMP
    pct = (dif / REF_LT_TOT_IMP) * 100
    sup = "SÍ" if dif > 0 else "NO"
    print(f"{m['mes']:7} | Total: ${m['tot_imp']:>10,.2f} | Ref: ${REF_LT_TOT_IMP:>10,.2f} | Dif: ${dif:>10,.2f} ({pct:>+5.1f}%) | Supera: {sup}")
