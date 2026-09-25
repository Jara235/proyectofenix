import pandas as pd

# Histórico exacto del reverso del recibo CFE (Página 2):
# Nota: En abril y octubre hubo 2 cortes/facturaciones en el sistema CFE
data_historica = [
    {'mes': 'FEB 25', 'demanda_kw': 177, 'consumo_kwh': 8123, 'precio_medio': 3.8428, 'importe_est': 8123 * 3.8428},
    {'mes': 'MAR 25', 'demanda_kw': 180, 'consumo_kwh': 8617, 'precio_medio': 3.6995, 'importe_est': 8617 * 3.6995},
    {'mes': 'ABR 25 (1)', 'demanda_kw': 134, 'consumo_kwh': 1792, 'precio_medio': 2.4957, 'importe_est': 1792 * 2.4957},
    {'mes': 'ABR 25 (2)', 'demanda_kw': 134, 'consumo_kwh': 3024, 'precio_medio': 2.6423, 'importe_est': 3024 * 2.6423},
    {'mes': 'MAY 25', 'demanda_kw': 159, 'consumo_kwh': 4945, 'precio_medio': 2.5289, 'importe_est': 4945 * 2.5289},
    {'mes': 'JUN 25', 'demanda_kw': 166, 'consumo_kwh': 4217, 'precio_medio': 3.0060, 'importe_est': 4217 * 3.0060},
    {'mes': 'JUL 25', 'demanda_kw': 156, 'consumo_kwh': 5819, 'precio_medio': 2.6063, 'importe_est': 5819 * 2.6063},
    {'mes': 'AGO 25', 'demanda_kw': 149, 'consumo_kwh': 7125, 'precio_medio': 3.7788, 'importe_est': 7125 * 3.7788},
    {'mes': 'SEP 25', 'demanda_kw': 154, 'consumo_kwh': 5134, 'precio_medio': 2.9910, 'importe_est': 5134 * 2.9910},
    {'mes': 'OCT 25 (1)', 'demanda_kw': 148, 'consumo_kwh': 8809, 'precio_medio': 2.4444, 'importe_est': 8809 * 2.4444},
    {'mes': 'OCT 25 (2)', 'demanda_kw': 151, 'consumo_kwh': 3400, 'precio_medio': 3.5815, 'importe_est': 3400 * 3.5815},
    {'mes': 'NOV 25', 'demanda_kw': 155, 'consumo_kwh': 13411, 'precio_medio': 3.5101, 'importe_est': 13411 * 3.5101},
    {'mes': 'DIC 25', 'demanda_kw': 162, 'consumo_kwh': 19095, 'precio_medio': 3.2260, 'importe_est': 19095 * 3.2260},
    {'mes': 'ENE 26', 'demanda_kw': 178, 'consumo_kwh': 18849, 'precio_medio': 3.1459, 'importe_est': 70267.00},
    {'mes': 'FEB 26', 'demanda_kw': 174, 'consumo_kwh': 13496, 'precio_medio': 3.3430, 'importe_est': 53464.00},
    {'mes': 'MAR 26', 'demanda_kw': 161, 'consumo_kwh': 13557, 'precio_medio': 3.1756, 'importe_est': 51017.00},
]

df = pd.DataFrame(data_historica)

# Para FEBRERO 2026: Los 12 periodos anteriores (desde FEB 25 hasta ENE 26, total 14 registros considerando los dobles o agrupando por mes calendario)
# Agrupemos por mes calendario para tener exactamente los 12 meses:
# Feb-25: 8,123
# Mar-25: 8,617
# Abr-25: 1,792 + 3,024 = 4,816
# May-25: 4,945
# Jun-25: 4,217
# Jul-25: 5,819
# Ago-25: 7,125
# Sep-25: 5,134
# Oct-25: 8,809 + 3,400 = 12,209
# Nov-25: 13,411
# Dic-25: 19,095
# Ene-26: 18,849

meses_cal = [
    {'mes': 'Feb-25', 'kwh': 8123, 'demanda': 177, 'imp': 8123 * 3.8428},
    {'mes': 'Mar-25', 'kwh': 8617, 'demanda': 180, 'imp': 8617 * 3.6995},
    {'mes': 'Abr-25', 'kwh': 4816, 'demanda': 134, 'imp': 1792*2.4957 + 3024*2.6423},
    {'mes': 'May-25', 'kwh': 4945, 'demanda': 159, 'imp': 4945 * 2.5289},
    {'mes': 'Jun-25', 'kwh': 4217, 'demanda': 166, 'imp': 4217 * 3.0060},
    {'mes': 'Jul-25', 'kwh': 5819, 'demanda': 156, 'imp': 5819 * 2.6063},
    {'mes': 'Ago-25', 'kwh': 7125, 'demanda': 149, 'imp': 7125 * 3.7788},
    {'mes': 'Sep-25', 'kwh': 5134, 'demanda': 154, 'imp': 5134 * 2.9910},
    {'mes': 'Oct-25', 'kwh': 12209, 'demanda': 151, 'imp': 8809*2.4444 + 3400*3.5815},
    {'mes': 'Nov-25', 'kwh': 13411, 'demanda': 155, 'imp': 13411 * 3.5101},
    {'mes': 'Dic-25', 'kwh': 19095, 'demanda': 162, 'imp': 19095 * 3.2260},
    {'mes': 'Ene-26', 'kwh': 18849, 'demanda': 178, 'imp': 70267.00},
]

df_cal = pd.DataFrame(meses_cal)

# 12 MESES PREVIOS A FEBRERO 2026 (Feb-25 a Ene-26):
prom_12m_feb26_kwh = df_cal['kwh'].mean()
prom_12m_feb26_imp = df_cal['imp'].mean()
prom_12m_feb26_dem = df_cal['demanda'].mean()

# 12 MESES PREVIOS A MARZO 2026 (Mar-25 a Feb-26):
meses_cal_mar = meses_cal[1:] + [{'mes': 'Feb-26', 'kwh': 13496, 'demanda': 174, 'imp': 53464.00}]
df_cal_mar = pd.DataFrame(meses_cal_mar)
prom_12m_mar26_kwh = df_cal_mar['kwh'].mean()
prom_12m_mar26_imp = df_cal_mar['imp'].mean()
prom_12m_mar26_dem = df_cal_mar['demanda'].mean()

print("=== PROMEDIO 12 MESES ANTERIORES PARA FEBRERO 2026 ===")
print(f"Promedio 12m Previos Consumo: {prom_12m_feb26_kwh:,.1f} kWh")
print(f"Promedio 12m Previos Importe: ${prom_12m_feb26_imp:,.2f} MXN")
print(f"Promedio 12m Previos Demanda: {prom_12m_feb26_dem:,.1f} kW")
print(f"Real Febrero 2026: 13,496 kWh | $53,464.00 MXN | 174 kW")
dif_feb_kwh = 13496 - prom_12m_feb26_kwh
dif_feb_pct_kwh = (dif_feb_kwh / prom_12m_feb26_kwh) * 100
dif_feb_imp = 53464.00 - prom_12m_feb26_imp
dif_feb_pct_imp = (dif_feb_imp / prom_12m_feb26_imp) * 100
print(f"Diferencia Consumo: +{dif_feb_kwh:,.1f} kWh ({dif_feb_pct_kwh:+.1f}%) -> SUPERA: {'SÍ' if dif_feb_kwh > 0 else 'NO'}")
print(f"Diferencia Importe: +${dif_feb_imp:,.2f} MXN ({dif_feb_pct_imp:+.1f}%) -> SUPERA: {'SÍ' if dif_feb_imp > 0 else 'NO'}")

print("\n=== PROMEDIO 12 MESES ANTERIORES PARA MARZO 2026 ===")
print(f"Promedio 12m Previos Consumo: {prom_12m_mar26_kwh:,.1f} kWh")
print(f"Promedio 12m Previos Importe: ${prom_12m_mar26_imp:,.2f} MXN")
print(f"Promedio 12m Previos Demanda: {prom_12m_mar26_dem:,.1f} kW")
print(f"Real Marzo 2026: 13,557 kWh | $51,017.00 MXN | 161 kW")
dif_mar_kwh = 13557 - prom_12m_mar26_kwh
dif_mar_pct_kwh = (dif_mar_kwh / prom_12m_mar26_kwh) * 100
dif_mar_imp = 51017.00 - prom_12m_mar26_imp
dif_mar_pct_imp = (dif_mar_imp / prom_12m_mar26_imp) * 100
print(f"Diferencia Consumo: +{dif_mar_kwh:,.1f} kWh ({dif_mar_pct_kwh:+.1f}%) -> SUPERA: {'SÍ' if dif_mar_kwh > 0 else 'NO'}")
print(f"Diferencia Importe: +${dif_mar_imp:,.2f} MXN ({dif_mar_pct_imp:+.1f}%) -> SUPERA: {'SÍ' if dif_mar_imp > 0 else 'NO'}")
