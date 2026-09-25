import os
import zipfile
import glob
from pathlib import Path

base_dir = r"c:\Users\JOSE\Desktop\Proyecto fenix\facturas"

# 1. Get all files in ZIPs
zip_files = glob.glob(os.path.join(base_dir, "*.zip"))
files_in_zips = set()

print(f"Buscando en {len(zip_files)} archivos ZIP...")
for z_path in zip_files:
    try:
        with zipfile.ZipFile(z_path, 'r') as z:
            for info in z.infolist():
                if not info.is_dir():
                    # Get base filename, ignore folder paths inside ZIP
                    fname = os.path.basename(info.filename).strip()
                    if fname and not fname.startswith('.'): # ignore hidden/mac files
                        files_in_zips.add(fname.lower())
    except Exception as e:
        print(f"Error reading {z_path}: {e}")

print(f"Total archivos únicos dentro de los ZIPs: {len(files_in_zips)}")

# 2. Get all files in DB_Diesel and DB_Gasolina (the ones we exported)
exported_dirs = [
    os.path.join(base_dir, "DB_Diesel"),
    os.path.join(base_dir, "DB_Gasolina"),
    os.path.join(base_dir, "Diesel"),
    os.path.join(base_dir, "Gasolina")
]

files_in_folders = set()
for d in exported_dirs:
    if os.path.exists(d):
        for root, dirs, files in os.walk(d):
            for f in files:
                files_in_folders.add(f.strip().lower())

print(f"Total archivos únicos en carpetas extraídas: {len(files_in_folders)}")

# 3. Compare
missing = []
for f in files_in_zips:
    # Some ZIP files might have UUIDs or original names, whereas our DB exports are "Factura_XXXX.pdf"
    # So a direct name comparison might be tricky. Let's try it first.
    if f not in files_in_folders:
        missing.append(f)

print(f"\nArchivos en ZIPs que no coinciden por nombre exacto en las carpetas: {len(missing)}")
if missing:
    print("Muestra de 10 archivos no encontrados (por nombre exacto):")
    for f in missing[:10]:
        print(f"  - {f}")
        
    print("\nNOTA: Recuerda que las facturas de la Base de Datos fueron renombradas a 'Factura_10405.pdf' etc. "
          "Si los ZIPs tenían nombres como '1243_factura.pdf', no coincidirán por nombre.")
