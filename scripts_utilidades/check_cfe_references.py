import pandas as pd
import numpy as np

# Datos del reverso de los recibos CFE (histórico 2025)
hist = [
    {'periodo': 'FEB 25', 'demanda_kw': 177, 'consumo_kwh': 8123, 'fp': 74.35, 'fc': 6.83, 'precio_medio': 3.8428},
    {'periodo': 'MAR 25', 'demanda_kw': 180, 'consumo_kwh': 8617, 'fp': 74.80, 'fc': 6.43, 'precio_medio': 3.6995},
    {'periodo': 'ABR 25 (1)', 'demanda_kw': 134, 'consumo_kwh': 1792, 'fp': 73.67, 'fc': 11.14, 'precio_medio': 2.4957},
    {'periodo': 'ABR 25 (2)', 'demanda_kw': 134, 'consumo_kwh': 3024, 'fp': 72.55, 'fc': 3.76, 'precio_medio': 2.6423},
    {'periodo': 'MAY 25', 'demanda_kw': 159, 'consumo_kwh': 4945, 'fp': 71.91, 'fc': 4.18, 'precio_medio': 2.5289},
    {'periodo': 'JUN 25', 'demanda_kw': 166, 'consumo_kwh': 4217, 'fp': 74.29, 'fc': 3.53, 'precio_medio': 3.0060},
    {'periodo': 'JUL 25', 'demanda_kw': 156, 'consumo_kwh': 5819, 'fp': 74.85, 'fc': 5.01, 'precio_medio': 2.6063},
    {'periodo': 'AGO 25', 'demanda_kw': 149, 'consumo_kwh': 7125, 'fp': 76.24, 'fc': 6.43, 'precio_medio': 3.7788},
    {'periodo': 'SEP 25', 'demanda_kw': 154, 'consumo_kwh': 5134, 'fp': 74.09, 'fc': 4.63, 'precio_medio': 2.9910},
    {'periodo': 'OCT 25 (1)', 'demanda_kw': 148, 'consumo_kwh': 8809, 'fp': 75.08, 'fc': 9.92, 'precio_medio': 2.4444},
    {'periodo': 'OCT 25 (2)', 'demanda_kw': 151, 'consumo_kwh': 3400, 'fp': 75.10, 'fc': 15.64, 'precio_medio': 3.5815},
    {'periodo': 'NOV 25', 'demanda_kw': 155, 'consumo_kwh': 13411, 'fp': 76.93, 'fc': 12.02, 'precio_medio': 3.5101},
    {'periodo': 'DIC 25', 'demanda_kw': 162, 'consumo_kwh': 19095, 'fp': 79.48, 'fc': 15.84, 'precio_medio': 3.2260},
]

df_h = pd.DataFrame(hist)
prom_consumo_anual = df_h['consumo_kwh'].mean()
prom_demanda_anual = df_h['demanda_kw'].mean()

print(f"Promedio Histórico Anual de Consumo: {prom_consumo_anual:,.1f} kWh / mes")
print(f"Promedio Histórico Anual de Demanda: {prom_demanda_anual:,.1f} kW")

# Comparación 2026:
# FEBRERO 2026:
feb_26_kwh = 13496
feb_26_imp = 53464.00
feb_25_kwh = 8123

# MARZO 2026:
mar_26_kwh = 13557
mar_26_imp = 51017.00
mar_25_kwh = 8617

print("\n--- FEBRERO 2026 ---")
print(f"Consumo: {feb_26_kwh:,} kWh | Importe: ${feb_26_imp:,.2f}")
print(f"Vs Promedio Histórico ({prom_consumo_anual:,.1f} kWh): +{(feb_26_kwh - prom_consumo_anual):,.1f} kWh (+{((feb_26_kwh - prom_consumo_anual)/prom_consumo_anual)*100:.1f}%) -> SUPERA: SÍ")
print(f"Vs Mismo Mes Año Anterior (FEB 25: {feb_25_kwh:,} kWh): +{(feb_26_kwh - feb_25_kwh):,} kWh (+{((feb_26_kwh - feb_25_kwh)/feb_25_kwh)*100:.1f}%) -> SUPERA: SÍ")

print("\n--- MARZO 2026 ---")
print(f"Consumo: {mar_26_kwh:,} kWh | Importe: ${mar_26_imp:,.2f}")
print(f"Vs Promedio Histórico ({prom_consumo_anual:,.1f} kWh): +{(mar_26_kwh - prom_consumo_anual):,.1f} kWh (+{((mar_26_kwh - prom_consumo_anual)/prom_consumo_anual)*100:.1f}%) -> SUPERA: SÍ")
print(f"Vs Mismo Mes Año Anterior (MAR 25: {mar_25_kwh:,} kWh): +{(mar_26_kwh - mar_25_kwh):,} kWh (+{((mar_26_kwh - mar_25_kwh)/mar_25_kwh)*100:.1f}%) -> SUPERA: SÍ")
