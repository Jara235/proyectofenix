import pandas as pd
import numpy as np

# Referencias
REF_MT_TOT_IMP = 334486.40 # MT Ref Mensual ($)
REF_LT_TOT_IMP = 258291.50 # LT Ref Mensual ($)
REF_GLOBAL_IMP = 592777.90 # Global Ref Mensual ($)

# 8 Meses: Enero a Agosto
# MÉXICO - TOLUCA
meses_mt_8 = [
    {
        'mes': 'Enero', 'tipo': 'Estimación Dinámica', 'd_lts': 7932.9, 'd_imp': 214188.30, 'g_lts': 1395.6, 'g_imp': 33354.84, 'tot_imp': 247543.14,
        'razon': 'Heladas matutinas en tramo de montaña y La Marquesa retrasan colado de asfalto caliente hasta después de las 10:30 hrs. Arranque escalonado.'
    },
    {
        'mes': 'Febrero', 'tipo': 'Estimación Dinámica', 'd_lts': 9597.8, 'd_imp': 259140.60, 'g_lts': 1457.8, 'g_imp': 34841.42, 'tot_imp': 293982.02,
        'razon': 'Operación en ascenso con buen clima seco, pero mes corto de 28 días (20 días hábiles) reduce el volumen acumulado mensual.'
    },
    {
        'mes': 'Marzo', 'tipo': 'Estimación Dinámica', 'd_lts': 12633.9, 'd_imp': 341115.30, 'g_lts': 1979.0, 'g_imp': 47298.10, 'tot_imp': 388413.40,
        'razon': 'Estiaje pleno en autopista México-Toluca: frentes continuos de fresado nocturno y tiros largos de mezcla asfáltica sin lluvia.'
    },
    {
        'mes': 'Abril', 'tipo': 'Estimación Dinámica', 'd_lts': 10424.9, 'd_imp': 281472.30, 'g_lts': 1624.5, 'g_imp': 38825.55, 'tot_imp': 320297.85,
        'razon': 'Buen avance pero ajustado por el paro de Semana Santa y cambio programado de picas en la perfiladora de asfalto.'
    },
    {
        'mes': 'Mayo', 'tipo': 'Estimación Dinámica', 'd_lts': 14396.8, 'd_imp': 388713.60, 'g_lts': 2169.8, 'g_imp': 51858.22, 'tot_imp': 440571.82,
        'razon': 'MES PICO: Cierre acelerado de tramos de autopista antes de lluvias. Pavimentadora Vögele y compactadores en dobles turnos continuos.'
    },
    {
        'mes': 'Junio', 'tipo': 'Histórico / Estimación', 'd_lts': 7073.2, 'd_imp': 190976.40, 'g_lts': 1346.2, 'g_imp': 32174.18, 'tot_imp': 223150.58,
        'razon': 'Inicio de lluvias y tormentas fuertes en zona alta (La Marquesa/Salazar), impidiendo el riego de liga y tendido; traslados a taller.'
    },
    {
        'mes': 'Julio', 'tipo': 'Histórico Real Registrado', 'd_lts': 11691.0, 'd_imp': 258120.00, 'g_lts': 1882.6, 'g_imp': 45200.01, 'tot_imp': 303320.01,
        'razon': 'Mes completo auditado con 5 semanas: Frentes activos continuos con suministro regular de autotanque Castilla, moderado por lluvias intermitentes.'
    },
    {
        'mes': 'Agosto', 'tipo': 'Histórico + Proy. Mes Completo', 'd_lts': 11980.0, 'd_imp': 323460.00, 'g_lts': 1814.0, 'g_imp': 43354.60, 'tot_imp': 366814.60,
        'razon': 'Ventana de Canícula (días secos a mediados de agosto) aprovechados para intensificar tiros de asfalto y bacheo en tramos críticos.'
    }
]

# LERMA - TRES MARÍAS
meses_lt_8 = [
    {
        'mes': 'Enero', 'tipo': 'Estimación Dinámica', 'd_lts': 5845.5, 'd_imp': 157828.50, 'g_lts': 1427.9, 'g_imp': 34126.81, 'tot_imp': 191955.31,
        'razon': 'Temperaturas gélidas en la zona lacustre y sierra de Lerma; calibración y mantenimiento general de maquinaria pesada.'
    },
    {
        'mes': 'Febrero', 'tipo': 'Estimación Dinámica', 'd_lts': 7080.6, 'd_imp': 191176.20, 'g_lts': 1491.7, 'g_imp': 35651.63, 'tot_imp': 226827.83,
        'razon': 'Buen avance en tramos de terracerías, base y bacheo, pero limitado por contar con 28 días naturales (20 días de operación).'
    },
    {
        'mes': 'Marzo', 'tipo': 'Estimación Dinámica', 'd_lts': 9320.4, 'd_imp': 251650.80, 'g_lts': 2025.9, 'g_imp': 48418.81, 'tot_imp': 300069.61,
        'razon': 'Condiciones óptimas de estiaje para carpeta asfáltica en carretera Lerma-Tres Marías, frentes activos de bacheo profundo y compactación.'
    },
    {
        'mes': 'Abril', 'tipo': 'Estimación Dinámica', 'd_lts': 7690.7, 'd_imp': 207648.90, 'g_lts': 1663.0, 'g_imp': 39745.70, 'tot_imp': 247394.60,
        'razon': 'Interrupción programada de frentes durante Semana Santa, destinada al mantenimiento de la petrolizadora y rodillos Hamm.'
    },
    {
        'mes': 'Mayo', 'tipo': 'Estimación Dinámica', 'd_lts': 10620.9, 'd_imp': 286764.30, 'g_lts': 2221.2, 'g_imp': 53086.68, 'tot_imp': 339850.98,
        'razon': 'MES PICO: Máxima intensidad para proteger terracerías y colocar carpeta corrida antes del temporal en la sierra.'
    },
    {
        'mes': 'Junio', 'tipo': 'Histórico / Estimación', 'd_lts': 5218.1, 'd_imp': 140888.70, 'g_lts': 1378.2, 'g_imp': 32938.98, 'tot_imp': 173827.68,
        'razon': 'Temporal de lluvias en la sierra Lerma-Tres Marías frena colocación de emulsión y asfalto; cuadrillas se enfocan en desasolve/drenaje.'
    },
    {
        'mes': 'Julio', 'tipo': 'Histórico Real Registrado', 'd_lts': 11360.3, 'd_imp': 203830.18, 'g_lts': 1980.2, 'g_imp': 46497.27, 'tot_imp': 250327.45,
        'razon': 'Mes completo auditado con 5 semanas: Alta actividad en fresado (Semana 29 pico con 6,205 L) compensado por semanas lluviosas.'
    },
    {
        'mes': 'Agosto', 'tipo': 'Histórico + Proy. Mes Completo', 'd_lts': 7626.0, 'd_imp': 205902.00, 'g_lts': 1626.0, 'g_imp': 38861.40, 'tot_imp': 244763.40,
        'razon': 'Lluvias persistentes en la parte alta de la sierra de Tres Marías; jornadas intermitentes de bacheo y riego de impregnación.'
    }
]

print("=== MÉXICO - TOLUCA (ENERO A AGOSTO) ===")
for m in meses_mt_8:
    dif = m['tot_imp'] - REF_MT_TOT_IMP
    pct = (dif / REF_MT_TOT_IMP) * 100
    sup = "SÍ" if dif > 0 else "NO"
    print(f"{m['mes']:7} | Total: ${m['tot_imp']:>10,.2f} | Ref: ${REF_MT_TOT_IMP:>10,.2f} | Dif: ${dif:>10,.2f} ({pct:>+5.1f}%) | Supera: {sup}")

print("\n=== LERMA - TRES MARÍAS (ENERO A AGOSTO) ===")
for m in meses_lt_8:
    dif = m['tot_imp'] - REF_LT_TOT_IMP
    pct = (dif / REF_LT_TOT_IMP) * 100
    sup = "SÍ" if dif > 0 else "NO"
    print(f"{m['mes']:7} | Total: ${m['tot_imp']:>10,.2f} | Ref: ${REF_LT_TOT_IMP:>10,.2f} | Dif: ${dif:>10,.2f} ({pct:>+5.1f}%) | Supera: {sup}")
