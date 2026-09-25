import pandas as pd
import re

excel_path = r"c:\Users\JOSE\Desktop\Proyecto fenix\FACTURAS_EXTRAIDAS_REVISION.xlsx"

try:
    df = pd.read_excel(excel_path)
except Exception as e:
    print(f"Error reading excel: {e}")
    exit(1)

def normalize_destination(raw_text):
    if pd.isna(raw_text):
        return "Sin asignar"
        
    text = str(raw_text).upper()
    
    if "PEGASO" in text:
        return "Maquinaria Pegaso"
    
    # Check Lerma first as it's distinct
    if "LERMA" in text or "TRES MARIAS" in text or "TRES MARÍAS" in text or "L3M" in text:
        return "Lerma-Tres Marias"
        
    # Check Bacheo Toluca
    if "BACHEO" in text:
        return "Bacheo Toluca"
        
    # Check Mexico-Toluca (if it has MEX and TOLUCA, or just MEX-TOL)
    if ("MEX" in text or "MÉX" in text) and "TOLUCA" in text:
        return "México-Toluca"
    # Sometime it's just 'OBRA MEXICO'
    if "MEXICO" in text or "MÉXICO" in text:
        return "México-Toluca"
        
    # Check Huixquilucan
    if "HUIXQUILUCAN" in text or "HUIX" in text:
        return "Planta de Asfalto Huixquilucan"
        
    # Fallback for just "TOLUCA" (if not bacheo or mexico)
    if "TOLUCA" in text:
        # We can assume Mexico-Toluca or leave for review
        return "México-Toluca"
        
    return "Sin asignar"

df['PUNTO_DE_CARGA_NORMALIZADO'] = df['DESTINO_REPORTADO_PDF'].apply(normalize_destination)

# Put the normalized column right next to the original destination for easy review
cols = list(df.columns)
cols.remove('PUNTO_DE_CARGA_NORMALIZADO')
# Find index of DESTINO_REPORTADO_PDF
try:
    idx = cols.index('DESTINO_REPORTADO_PDF')
    cols.insert(idx + 1, 'PUNTO_DE_CARGA_NORMALIZADO')
    df = df[cols]
except:
    pass

try:
    df.to_excel(excel_path, index=False)
    
    # Let's count how many we assigned
    counts = df['PUNTO_DE_CARGA_NORMALIZADO'].value_counts()
    print("Normalizacion completada con exito.\nResumen de Asignaciones:")
    for name, count in counts.items():
        print(f" - {name}: {count}")
except Exception as e:
    print(f"Error saving to Excel: {e}")
