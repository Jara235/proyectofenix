import pandas as pd

maestro_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_GASOLINA_NUEVO.xlsx'

df_facturas = pd.read_excel(maestro_path, sheet_name='BD_FACTURAS')

new_row = {
    'FOLIO_CONCILIACION': 'FAC-GAS-27-099',
    'FOLIO_FACTURA': '4LV4025',
    'FECHA_FACTURA': '2026-06-30',
    'SEMANA': 27,
    'PROVEEDOR': 'SERVICIO LEVET',
    'PUNTO_DE_CARGA': 'LEVET',
    'LITROS_FACTURADOS': 4348.27,
    'PRECIO_UNITARIO': 21.71,
    'IMPORTE': 94423.73,
    'I.V.A': 14724.40,
    'IMPORTE_TOTAL': 109148.13,
    'TIPO_COMBUSTIBLE': 'Magna/Premium/Diesel',
    'ESTATUS_CONCILIACION': 'EN ESPERA'
}

df_facturas = pd.concat([df_facturas, pd.DataFrame([new_row])], ignore_index=True)

with pd.ExcelWriter(maestro_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    df_facturas.to_excel(writer, sheet_name='BD_FACTURAS', index=False)

print("Factura J.D.J. JUNIO2026 añadida con éxito a BD_FACTURAS.")
