import sqlite3
db = sqlite3.connect('c:/Users/JOSE/Desktop/Proyecto fenix/fenix_v2.db')
c = db.cursor()
codigos = {
    'Mxico-Toluca': 'MT',
    'Lerma - Tres Maras': 'L3M',
    'No aplica': 'NA',
    'Chamapa-Lechera': 'CL',
    'Bacheo Toluca': 'BT',
    'Planta Asfalto Pegaso': 'PAP',
    'Planta Asfalto Huixquilucan': 'PAH',
    'Dragones': 'DRA',
    'Jalisco': 'JAL',
    'Maquinaria Pegaso': 'MP',
    'Providencia': 'PRO',
    'Vicente Lomabrdo': 'VL',
    'Transportes flotilla': 'TF'
}
for nombre, codigo in codigos.items():
    c.execute('UPDATE catalogos_obras SET codigo = ? WHERE nombre LIKE ?', (codigo, nombre[:8] + '%'))

c.execute('UPDATE diesel_consumos SET folio_conciliacion = ? WHERE folio_conciliacion = ?', ('CMQ-L3M-28-303', 'CMQ-LERMA-28-303'))
db.commit()
db.close()
print('Cdigos actualizados.')

