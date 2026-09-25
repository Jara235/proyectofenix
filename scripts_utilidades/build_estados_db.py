import sqlite3
import pandas as pd

db_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\fenix_v2.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Create the states of account table in fenix_v2
cur.execute("DROP TABLE IF EXISTS gasolina_estados_cuenta")
cur.execute("""
CREATE TABLE gasolina_estados_cuenta (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    semana              INTEGER NOT NULL,
    responsable         TEXT,
    vehiculo            TEXT,
    placa               TEXT,
    obra_destino        TEXT,
    gasolinera          TEXT,
    importe_autorizado  NUMERIC NOT NULL DEFAULT 0,
    consumo_real        NUMERIC NOT NULL DEFAULT 0,
    litros_reales       NUMERIC NOT NULL DEFAULT 0,
    diferencia          NUMERIC GENERATED ALWAYS AS (importe_autorizado - consumo_real) STORED,
    estatus             TEXT,
    created_at          TEXT NOT NULL DEFAULT (datetime('now','localtime'))
)
""")
conn.commit()
print("Table gasolina_estados_cuenta created.")

# Reload normalized data
def load_gt(path, semana):
    df = pd.read_excel(path, sheet_name='Consumos Semanales GT', header=2)
    df.columns = ['_idx','RESPONSABLE','VEHICULO','PLACA','OBRA_DESTINO','IMPORTE_AUTORIZADO','GASOLINERA']
    df = df[df['RESPONSABLE'].notna() & (df['RESPONSABLE'] != 'RESPONSABLE') & (df['RESPONSABLE'] != 'Total General')].copy()
    df['SEMANA'] = semana
    return df.drop(columns=['_idx'])

gt26 = load_gt(r'c:\Users\JOSE\Desktop\Proyecto fenix\CONSUMOS_DE_GASOLINA_SEMANALES_GT.xlsx', 26)
gt27 = load_gt(r'c:\Users\JOSE\Desktop\Proyecto fenix\CONSUMOS_DE_GASOLINA_SEMANALES_GT_LEVET_HUIX.xlsx', 27)
df_estado = pd.concat([gt26, gt27], ignore_index=True)

for col in ['RESPONSABLE','VEHICULO','OBRA_DESTINO','GASOLINERA']:
    df_estado[col] = df_estado[col].astype(str).str.strip().str.upper()
df_estado['PLACA'] = df_estado['PLACA'].astype(str).str.strip().str.upper().str.replace(r'[\s\-]','',regex=True)
df_estado.loc[df_estado['PLACA'] == 'NAN', 'PLACA'] = 'S/P'
df_estado.loc[df_estado['VEHICULO'] == 'NAN', 'VEHICULO'] = 'EQUIPO MENOR'
df_estado['IMPORTE_AUTORIZADO'] = pd.to_numeric(df_estado['IMPORTE_AUTORIZADO'], errors='coerce').fillna(0)

maestro_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_GASOLINA_NUEVO.xlsx'
bd_gas = pd.read_excel(maestro_path, sheet_name='BD_GASOLINA')
bd_gas['PLACA'] = bd_gas['PLACA'].astype(str).str.strip().str.upper().str.replace(r'[\s\-]','',regex=True)
bd_gas['SEMANA'] = pd.to_numeric(bd_gas['SEMANA'], errors='coerce').fillna(0).astype(int)
bd_gas['IMPORTE_TOTAL'] = pd.to_numeric(bd_gas['IMPORTE_TOTAL'], errors='coerce').fillna(0)
bd_gas['LITROS'] = pd.to_numeric(bd_gas['LITROS'], errors='coerce').fillna(0)

agg = bd_gas.groupby(['PLACA','SEMANA']).agg(
    consumo_real=('IMPORTE_TOTAL','sum'),
    litros_reales=('LITROS','sum')
).reset_index()

merged = pd.merge(df_estado, agg, left_on=['PLACA','SEMANA'], right_on=['PLACA','SEMANA'], how='left')
merged['consumo_real'] = merged['consumo_real'].fillna(0)
merged['litros_reales'] = merged['litros_reales'].fillna(0)
merged['dif'] = merged['IMPORTE_AUTORIZADO'] - merged['consumo_real']
merged['estatus'] = merged['dif'].apply(lambda x: 'OK - Saldo a favor' if x >= 0 else 'ALERTA - Excedido')

count = 0
for _, row in merged.iterrows():
    def cv(v):
        if pd.isna(v): return None
        if isinstance(v, float) and v != v: return None
        return str(v).strip() if isinstance(v, str) else v
    cur.execute("""
        INSERT INTO gasolina_estados_cuenta (semana, responsable, vehiculo, placa, obra_destino, gasolinera, importe_autorizado, consumo_real, litros_reales, estatus)
        VALUES (?,?,?,?,?,?,?,?,?,?)
    """, (cv(row.SEMANA), cv(row.RESPONSABLE), cv(row.VEHICULO), cv(row.PLACA), cv(row.OBRA_DESTINO),
          cv(row.GASOLINERA), float(row.IMPORTE_AUTORIZADO), float(row.consumo_real), float(row.litros_reales), cv(row.estatus)))
    count += 1

conn.commit()
conn.close()
print(f"Inserted {count} rows into gasolina_estados_cuenta in fenix_v2.db")
print(f"Semana 26: {len(merged[merged.SEMANA==26])} unidades, Total Auth: {merged[merged.SEMANA==26].IMPORTE_AUTORIZADO.sum():,.0f}")
print(f"Semana 27: {len(merged[merged.SEMANA==27])} unidades, Total Auth: {merged[merged.SEMANA==27].IMPORTE_AUTORIZADO.sum():,.0f}")
