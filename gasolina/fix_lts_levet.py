import pandas as pd, sqlite3, re

# Leer el JDJ PROVISIONAL con los litros reales
df_raw = pd.read_excel(r'c:\Users\JOSE\Desktop\Proyecto fenix\gasolina\CONTROL JDJ PROVISIONAL.xlsx', sheet_name='JUNIO 2026', header=None)
df_raw.columns = ['_x0','ticket','fecha','placa','km','conductor','obra','litros','precio','importe','subtotal']

# Limpiar: quitar filas de header o vacías
df = df_raw[df_raw['ticket'].notna() & df_raw['ticket'].astype(str).str.match(r'^\d{5,}')].copy()
df['placa'] = df['placa'].astype(str).str.strip().str.upper()
df['litros'] = pd.to_numeric(df['litros'], errors='coerce').fillna(0)
df['importe'] = pd.to_numeric(df['importe'], errors='coerce').fillna(0)
df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')

print(f"Tickets JDJ encontrados: {len(df)}")
print(f"Total litros en JDJ: {df['litros'].sum():.2f}")
print(f"Total importe en JDJ: ")
print()
print("Por placa:")
print(df.groupby('placa')[['litros','importe']].sum().sort_values('importe', ascending=False).to_string())

# Actualizar la BD - asignar litros a los registros de LEVET que los tienen en 0
c = sqlite3.connect(r'c:\Users\JOSE\Desktop\Proyecto fenix\fenix_v2.db')
cur = c.cursor()

actualizados = 0
sin_match = []
for _, row in df.iterrows():
    placa = str(row['placa']).strip().upper()
    fecha = row['fecha'].strftime('%Y-%m-%d') if pd.notna(row['fecha']) else None
    litros = float(row['litros'])
    importe = float(row['importe'])
    if not fecha or litros == 0: continue
    
    # Buscar el registro en gasolina_consumos que coincida por placa, fecha e importe
    cur.execute("""
        SELECT id, litros, importe_total FROM gasolina_consumos
        WHERE placa=? AND DATE(fecha)=? AND (ABS(importe_total - ?) < 1.0) AND semana='Semana 26'
    """, (placa, fecha, importe))
    rows = cur.fetchall()
    
    if rows and len(rows) == 1:
        rid = rows[0][0]
        cur.execute("UPDATE gasolina_consumos SET litros=?, costo_por_litro=? WHERE id=?",
                    (litros, round(importe/litros, 4) if litros > 0 else 0, rid))
        actualizados += 1
    elif not rows:
        sin_match.append(f"  NO MATCH: {placa} | {fecha} |  | {litros:.2f}lts")

c.commit()
c.close()

print(f"\n=== RESULTADO: {actualizados} registros actualizados con litros ===")
if sin_match:
    print(f"\nSIN MATCH ({len(sin_match)}):")
    for s in sin_match:
        print(s)
