import os
import shutil
import pandas as pd
from datetime import datetime

base_dir = r"c:\Users\JOSE\Desktop\Proyecto fenix\facturas"
excel_path = r"c:\Users\JOSE\Desktop\Proyecto fenix\FACTURAS_EXTRAIDAS_REVISION.xlsx"

try:
    df = pd.read_excel(excel_path)
    
    # Create base directories
    diesel_dir = os.path.join(base_dir, "Diesel")
    gasolina_dir = os.path.join(base_dir, "Gasolina")
    os.makedirs(diesel_dir, exist_ok=True)
    os.makedirs(gasolina_dir, exist_ok=True)
    
    moved_count = 0
    
    # Keep track of moved basenames so we can find orphans if needed
    moved_basenames = set()
    
    for index, row in df.iterrows():
        archivo = str(row.get('ARCHIVO_ORIGEN', ''))
        if not archivo or pd.isna(archivo) or archivo == 'nan':
            continue
            
        basename = os.path.splitext(archivo)[0].lower()
        
        # Determine Fuel Type
        tipo = str(row.get('TIPO_COMBUSTIBLE', '')).upper()
        if "GASOLINA" in tipo or "MAGNA" in tipo or "PREMIUM" in tipo:
            fuel_folder = gasolina_dir
        else:
            # Default to Diesel if not explicitly Gasolina (since most are Diesel)
            fuel_folder = diesel_dir
            
        # Determine Week
        fecha_val = row.get('FECHA_FACTURA')
        semana = "Semana_Desconocida"
        if pd.notna(fecha_val):
            # Try to parse date
            try:
                if isinstance(fecha_val, datetime):
                    dt = fecha_val
                else:
                    # Clean string
                    fecha_str = str(fecha_val).strip().split(' ')[0]
                    dt = pd.to_datetime(fecha_str)
                week_num = dt.isocalendar()[1]
                semana = f"Semana_{week_num:02d}"
            except Exception as e:
                pass
                
        # Create Week Folder
        target_dir = os.path.join(fuel_folder, semana)
        os.makedirs(target_dir, exist_ok=True)
        
        # Find files matching this basename
        # Check files directly instead of iterating all
        # since files might have different casing, we listdir once
        
    # We need to map all existing files in base_dir to their lowercased basename
    all_files = [f for f in os.listdir(base_dir) if os.path.isfile(os.path.join(base_dir, f))]
    file_map = {}
    for f in all_files:
        if f.lower().endswith('.xml') or f.lower().endswith('.pdf'):
            bname = os.path.splitext(f)[0].lower()
            if bname not in file_map:
                file_map[bname] = []
            file_map[bname].append(f)
            
    # Now iterate again to move
    for index, row in df.iterrows():
        archivo = str(row.get('ARCHIVO_ORIGEN', ''))
        if not archivo or pd.isna(archivo) or archivo == 'nan':
            continue
        basename = os.path.splitext(archivo)[0].lower()
        
        tipo = str(row.get('TIPO_COMBUSTIBLE', '')).upper()
        if "GASOLINA" in tipo or "MAGNA" in tipo:
            fuel_folder = gasolina_dir
        else:
            fuel_folder = diesel_dir
            
        fecha_val = row.get('FECHA_FACTURA')
        semana = "Semana_Desconocida"
        if pd.notna(fecha_val):
            try:
                if isinstance(fecha_val, datetime):
                    dt = fecha_val
                else:
                    fecha_str = str(fecha_val).strip().split(' ')[0]
                    dt = pd.to_datetime(fecha_str)
                week_num = dt.isocalendar()[1]
                semana = f"Semana_{week_num:02d}"
            except:
                pass
                
        target_dir = os.path.join(fuel_folder, semana)
        
        # Move files
        if basename in file_map:
            for actual_filename in file_map[basename]:
                src = os.path.join(base_dir, actual_filename)
                dst = os.path.join(target_dir, actual_filename)
                if os.path.exists(src):
                    shutil.move(src, dst)
                    moved_count += 1
            # Remove from map so we don't process again
            del file_map[basename]
            
    print(f"Exito: Se clasificaron y movieron {moved_count} archivos (XML y PDF).")
    
    # Any files left?
    leftovers = []
    for flist in file_map.values():
        leftovers.extend(flist)
        
    if leftovers:
        unclassified_dir = os.path.join(base_dir, "Sin_Clasificar")
        os.makedirs(unclassified_dir, exist_ok=True)
        for f in leftovers:
            src = os.path.join(base_dir, f)
            dst = os.path.join(unclassified_dir, f)
            shutil.move(src, dst)
        print(f"Nota: {len(leftovers)} archivos no estaban en el Excel y se movieron a 'Sin_Clasificar'.")

except Exception as e:
    print(f"Error fatal: {e}")
