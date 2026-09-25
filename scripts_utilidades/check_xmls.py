import os, sqlite3, xml.etree.ElementTree as ET
folder = 'c:/Users/JOSE/Desktop/Proyecto fenix/facturas'
db = sqlite3.connect('c:/Users/JOSE/Desktop/Proyecto fenix/fenix.db')
c = db.cursor()
ns = {'cfdi': 'http://www.sat.gob.mx/cfd/4'}
for f in os.listdir(folder):
    if f.endswith('.xml'):
        path = os.path.join(folder, f)
        try:
            tree = ET.parse(path)
            root = tree.getroot()
            conceptos = root.find('cfdi:Conceptos', ns)
            if conceptos is not None:
                for concepto in conceptos.findall('cfdi:Concepto', ns):
                    desc = concepto.get('Descripcion', '').lower()
                    sat_code = concepto.get('ClaveProdServ', '')
                    folio = root.get('Folio', '')
                    if not folio: continue
                    if 'gasolina' in desc or sat_code in ['15101514', '15101515'] or 'magna' in desc or 'premium' in desc:
                        print(f'GASOLINA FOUND: {f} | Folio: {folio} | Desc: {desc}')
                        c.execute("UPDATE fenix_facturas_documentos SET tipo_combustible='Gasolina' WHERE folio=?", (folio,))
        except Exception as e:
            print(f'Error reading {f}: {e}')
db.commit()
db.close()

