import xml.etree.ElementTree as ET
tree = ET.parse('c:/Users/JOSE/Desktop/Proyecto fenix/facturas/Diesel/Semana_25/2c6f01d9-fdba-4376-8cef-ed0d989e49df.xml')
root = tree.getroot()
ns = {'cfdi': 'http://www.sat.gob.mx/cfd/4', 'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'}

fecha = root.get('Fecha')

uuid = ''
timbre = root.find('.//tfd:TimbreFiscalDigital', ns)
if timbre is not None: uuid = timbre.get('UUID')

print(f'UUID: {uuid}, Fecha: {fecha}')
for c in root.findall('.//cfdi:Concepto', ns):
    print('Concepto:', c.get('Descripcion'), 'Cant:', c.get('Cantidad'), 'PU:', c.get('ValorUnitario'), 'Imp:', c.get('Importe'))
    for imp in c.findall('.//cfdi:Traslado', ns):
        print('  Impuesto:', imp.get('Impuesto'), 'Importe:', imp.get('Importe'))

