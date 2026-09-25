import pandas as pd

with open("preview_rendimiento.txt", "w", encoding="utf-8") as f:
    filepath = "GC-COMB-3.1_Excel_Maestro_Control_Combustible_Grupo_Trujano_FINAL_V2.xlsx"
    
    # Horas de trabajo
    f.write("=== Captura_Horas (primeras 25 filas) ===\n")
    df = pd.read_excel(filepath, sheet_name='Captura_Horas', nrows=25, header=None)
    f.write(df.to_string() + "\n\n")
    
    # Inventario con rendimientos
    f.write("=== Maquinaria_Inventario COMPLETA ===\n")
    df2 = pd.read_excel(filepath, sheet_name='Maquinaria_Inventario')
    f.write(df2.to_string() + "\n\n")
    
    # Catalogos - tabla de rendimiento si existe
    f.write("=== Catalogos (col V en adelante, filas 1-50) ===\n")
    df3 = pd.read_excel(filepath, sheet_name='Catalogos', nrows=50, header=None, usecols="A:Z")
    f.write(df3.to_string() + "\n\n")

print("Done")
