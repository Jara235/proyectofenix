import sqlite3
db = sqlite3.connect('c:/Users/JOSE/Desktop/Proyecto fenix/fenix_v2.db')
c = db.cursor()
c.execute('SELECT equipo_economico FROM diesel_consumos WHERE folio_conciliacion = ?', ('CMQ-L3M-28-302',))
row = c.fetchone()
equipo_eco = row[0] if row else None
if equipo_eco:
    c.execute('SELECT descripcion FROM catalogos_equipos WHERE numero_economico = ?', (equipo_eco,))
    desc_row = c.fetchone()
    desc = desc_row[0] if desc_row else ''
    c.execute('UPDATE diesel_consumos SET origen = ?, tipo_movimiento = ?, equipo = ? WHERE folio_conciliacion = ?', ('Marimba M-01', 'CARGA MAQUINARIA', desc, 'CMQ-L3M-28-302'))
    db.commit()
    print(f'Registro 302 actualizado. Equipo: {desc}')
else:
    print('No se encontro el registro 302.')

