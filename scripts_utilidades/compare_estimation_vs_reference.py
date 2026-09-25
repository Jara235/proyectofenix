import pandas as pd
import numpy as np

# Valores base de Referencia Real Promedio Mensual
REF_DIESEL_LTS = 18909.8
REF_DIESEL_IMP = 510563.40
REF_GAS_LTS = 3439.9
REF_GAS_IMP = 82214.50
REF_TOTAL_LTS = REF_DIESEL_LTS + REF_GAS_LTS # 22,349.7 L
REF_TOTAL_IMP = REF_DIESEL_IMP + REF_GAS_IMP # $592,777.90 MXN

datos_meses = [
    {
        'mes': 'Enero',
        'diesel_lts': 13778.4,
        'diesel_imp': 372017.79,
        'gas_lts': 2823.5,
        'gas_imp': 67480.93,
        'razon_supera': 'NO SUPERA (-25.9%). Retraso de tiros por heladas matutinas (-2°C a 4°C en Toluca/La Marquesa) y arranque paulatino post-vacaciones.'
    },
    {
        'mes': 'Febrero',
        'diesel_lts': 16678.4,
        'diesel_imp': 450317.98,
        'gas_lts': 2949.5,
        'gas_imp': 70493.24,
        'razon_supera': 'NO SUPERA (-12.1%). A pesar de buen clima seco, el mes tiene 28 días naturales (20 hábiles), reduciendo el consumo calendario total.'
    },
    {
        'mes': 'Marzo',
        'diesel_lts': 21950.7,
        'diesel_imp': 592668.49,
        'gas_lts': 4004.9,
        'gas_imp': 95716.37,
        'razon_supera': 'SÍ SUPERA (+16.1%). Clima seco óptimo (estiaje), cero lluvias y temperaturas cálidas ideales para asfalto caliente, activando turnos extendidos de fresado.'
    },
    {
        'mes': 'Abril',
        'diesel_lts': 18120.7,
        'diesel_imp': 489259.76,
        'gas_lts': 3287.5,
        'gas_imp': 78571.55,
        'razon_supera': 'NO SUPERA (-4.2%). Excelente clima pero compensado a la baja por el paro técnico de Semana Santa (3-4 días hábiles) usado para mantenimiento de maquinaria.'
    },
    {
        'mes': 'Mayo',
        'diesel_lts': 25017.7,
        'diesel_imp': 675476.97,
        'gas_lts': 4391.0,
        'gas_imp': 104945.67,
        'razon_supera': 'SÍ SUPERA (+31.7%). MES PICO ANUAL. Máxima aceleración de frentes constructivos para cerrar metas antes del temporal de lluvias. Dobles turnos y frentes nocturnos simultáneos.'
    },
    {
        'mes': 'Junio',
        'diesel_lts': 12286.5,
        'diesel_imp': 331734.24,
        'gas_lts': 2724.4,
        'gas_imp': 65113.18,
        'razon_supera': 'NO SUPERA (-33.1%). Inicio de lluvias intensas y tormentas en montaña. Imposibilidad de regar liga o tirar asfalto sobre mojado; equipos entran a taller.'
    }
]

res = []
for d in datos_meses:
    tot_lts = d['diesel_lts'] + d['gas_lts']
    tot_imp = d['diesel_imp'] + d['gas_imp']
    dif_imp = tot_imp - REF_TOTAL_IMP
    dif_pct = (dif_imp / REF_TOTAL_IMP) * 100
    supera = "SÍ" if tot_imp > REF_TOTAL_IMP else "NO"
    
    res.append({
        'Mes': d['mes'],
        'Diesel_Est_L': d['diesel_lts'],
        'Gas_Est_L': d['gas_lts'],
        'Total_Est_L': tot_lts,
        'Total_Est_Imp': tot_imp,
        'Ref_Prom_Imp': REF_TOTAL_IMP,
        'Dif_Imp': dif_imp,
        'Dif_Pct': dif_pct,
        'Supera_Ref': supera,
        'Justificacion': d['razon_supera']
    })

df_comp = pd.DataFrame(res)
print(df_comp[['Mes', 'Total_Est_L', 'Total_Est_Imp', 'Ref_Prom_Imp', 'Dif_Imp', 'Dif_Pct', 'Supera_Ref']].to_string())
