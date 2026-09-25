import zipfile
import os

facturas_dir = r'c:\Users\JOSE\Desktop\Proyecto fenix\facturas'
zips = [f for f in os.listdir(facturas_dir) if f.endswith('.zip')]

for z in zips:
    print(f"\n--- {z} ---")
    with zipfile.ZipFile(os.path.join(facturas_dir, z), 'r') as zip_ref:
        names = zip_ref.namelist()
        print(f"Total files: {len(names)}")
        print("Sample files:")
        for n in names[:10]:
            print("  ", n)
