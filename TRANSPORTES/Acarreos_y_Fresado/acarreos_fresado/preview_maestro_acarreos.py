import pandas as pd

with open("preview_maestro_acarreos.txt", "w", encoding="utf-8") as f:
    filepath = "acarreos y Fresado/GC-MAT-1.0_Maestro_Consolidado_V12.xlsx"
    xls = pd.ExcelFile(filepath)
    f.write(f"HOJAS: {xls.sheet_names}\n\n")
    
    for sheet in xls.sheet_names:
        try:
            df = pd.read_excel(filepath, sheet_name=sheet, nrows=20, header=None)
            f.write(f"=== {sheet} (primeras 20 filas) ===\n")
            f.write(df.to_string() + "\n\n")
        except Exception as e:
            f.write(f"=== {sheet} ERROR: {e} ===\n\n")

print("Done")
