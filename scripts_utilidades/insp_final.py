import pandas as pd
file_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_GASOLINA_NUEVO.xlsx'
df = pd.read_excel(file_path, sheet_name='BD_GASOLINA')
print(f'Total rows in BD_GASOLINA: {len(df)}')
for idx, row in df.tail(15).iterrows():
    print(f"[{row['FOLIO_CONCILIACION']}] {row['FECHA']} - {row['ORIGEN'][:10]} | {row['OBRA_DESTINO'][:15]:<15} | {row['VEHICULO'][:15]:<15} | Lts: {row['LITROS']} | Imp: {row['IMPORTE_TOTAL']}")
