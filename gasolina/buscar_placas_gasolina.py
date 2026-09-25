import pandas as pd
import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

MAESTRO_GAS = r"c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_GASOLINA_NUEVO.xlsx"

xl = pd.ExcelFile(MAESTRO_GAS)
print("Pestanas:", xl.sheet_names)

# Leer todas las hojas y buscar las placas/operadores
BUSCAR = ['NZT266B', 'LKC794D', 'LHB184D', 'PBT-12-29', 'NYZ-790-C',
          'Samuel Ortega', 'Cristobal', 'Diego Fernández', 'Diego Fernandez',
          'Leoncio Martinez', 'Paola Jaramillo']

for sheet in xl.sheet_names:
    try:
        df = pd.read_excel(MAESTRO_GAS, sheet_name=sheet)
        print(f"\n=== {sheet} ({len(df)} filas) ===")
        print("Columnas:", df.columns.tolist())
        
        # Buscar en todas las columnas
        for busq in BUSCAR:
            for col in df.columns:
                try:
                    mask = df[col].astype(str).str.contains(busq, case=False, na=False)
                    if mask.any():
                        print(f"\n  Encontrado '{busq}' en columna '{col}':")
                        print(df[mask].to_string())
                except:
                    pass
    except Exception as e:
        print(f"  ERROR leyendo {sheet}: {e}")
