import pandas as pd

maestro_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_GASOLINA_NUEVO.xlsx'
df_gas = pd.read_excel(maestro_path, sheet_name='BD_GASOLINA')

# Filter for Week 26
df_w26 = df_gas[df_gas['SEMANA'] == 26]

res = df_w26.groupby('ORIGEN').agg({
    'LITROS': 'sum',
    'IMPORTE_TOTAL': 'sum'
}).reset_index()

print("Resumen BD_GASOLINA Semana 26 por Origen:")
for _, row in res.iterrows():
    print(f"{row['ORIGEN']:<20} | Litros: {row['LITROS']:,.2f} | Importe: ${row['IMPORTE_TOTAL']:,.2f}")

print(f"\nTotal Importe General Semana 26: ${df_w26['IMPORTE_TOTAL'].sum():,.2f}")
