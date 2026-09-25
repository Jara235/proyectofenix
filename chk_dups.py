import os
import xml.etree.ElementTree as ET

facturas_dir = r'c:\Users\JOSE\Desktop\Proyecto fenix\facturas'

uuids = {}
duplicates = []

for root_dir, dirs, files in os.walk(facturas_dir):
    for f in files:
        if f.lower().endswith('.xml'):
            filepath = os.path.join(root_dir, f)
            try:
                tree = ET.parse(filepath)
                root = tree.getroot()
                
                # Find TimbreFiscalDigital to get UUID
                uuid = None
                for elem in root.iter():
                    if 'TimbreFiscalDigital' in elem.tag:
                        uuid = elem.attrib.get('UUID')
                        break
                        
                if uuid:
                    if uuid in uuids:
                        duplicates.append((uuids[uuid], filepath, uuid))
                    else:
                        uuids[uuid] = filepath
            except Exception as e:
                pass

print(f"Total unique XMLs: {len(uuids)}")
print(f"Total duplicates found: {len(duplicates)}")
for d in duplicates:
    print(f"Duplicate UUID: {d[2]}")
    print(f"  File 1: {d[0]}")
    print(f"  File 2: {d[1]}")
