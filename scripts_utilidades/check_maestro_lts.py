import pandas as pd

# Revisar el Excel maestro para ver si tiene litros
try:
    xl = pd.ExcelFile(r'c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_GASOLINA_NUEVO.xlsx')
    print("Hojas:", xl.sheet_names)
    
    for sheet in xl.sheet_names:
        df = xl.parse(sheet)
        print(f"\n=== Hoja: {sheet} ===")
        print("Columnas:", list(df.columns))
        print(f"Filas: {len(df)}")
        if 'LITROS' in df.columns or 'litros' in df.columns:
            col = 'LITROS' if 'LITROS' in df.columns else 'litros'
            con_lts = df[df[col].notna() & (df[col] > 0)]
            print(f"Registros CON litros: {len(con_lts)}")
            print(f"Total litros: {con_lts[col].sum():.2f}")
except Exception as e:
    print(f"Error: {e}")

# También revisar el archivo JDJ
try:
    import glob
    archivos = glob.glob(r'c:\Users\JOSE\Desktop\Proyecto fenix\gasolina\*.xlsx') + glob.glob(r'c:\Users\JOSE\Desktop\Proyecto fenix\*JDJ*.xlsx') + glob.glob(r'c:\Users\JOSE\Desktop\Proyecto fenix\*CONTROL*PROVISIONAL*.xlsx')
    print("\nArchivos JDJ encontrados:", archivos)
    for a in archivos[:3]:
        xl2 = pd.ExcelFile(a)
        print(f"\nArchivo: {a.split(chr(92))[-1]}")
        print("Hojas:", xl2.sheet_names)
except Exception as e:
    print(f"Error JDJ: {e}")
