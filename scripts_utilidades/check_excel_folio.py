import pandas as pd
df = pd.read_excel('c:/Users/JOSE/Desktop/Proyecto fenix/MAESTRO_CONTROL_DIESEL_NUEVO.xlsx', sheet_name='DIESEL_CONSUMOS')
print(df[df['ORIGEN'] == 'FACTURA']['FOLIO_CONCILIACION'].head(5))

