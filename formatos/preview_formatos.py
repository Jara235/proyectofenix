import pandas as pd

try:
    with open("preview_formatos.txt", "w", encoding="utf-8") as f:
        f.write("=== Captura_Obra (Master) ===\n")
        df_obra = pd.read_excel('GC-COMB-3.1_Excel_Maestro_Control_Combustible_Grupo_Trujano_FINAL_V2.xlsx', sheet_name='Captura_Obra', nrows=15, header=None)
        f.write(df_obra.to_string() + "\n\n")

        f.write("=== Formato GC-COMB-003_V2 ===\n")
        df_fmt3 = pd.read_excel('formatos/GC-COMB-003_V2.xlsx', nrows=15, header=None)
        f.write(df_fmt3.to_string() + "\n\n")
        
        f.write("=== Formato GC-COMB-006_V2 ===\n")
        df_fmt6 = pd.read_excel('formatos/GC-COMB-006_Formato_Captura_Operador_Semanal_V2.xlsx', nrows=15, header=None)
        f.write(df_fmt6.to_string() + "\n\n")
except Exception as e:
    with open("preview_formatos.txt", "w", encoding="utf-8") as f:
        f.write(str(e))
