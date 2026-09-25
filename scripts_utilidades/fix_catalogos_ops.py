import sqlite3
db = sqlite3.connect('c:/Users/JOSE/Desktop/Proyecto fenix/fenix_v2.db')
c = db.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS catalogos_operaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_operacion TEXT UNIQUE,
    codigo_operacion TEXT
)''')
c.execute('DELETE FROM catalogos_operaciones')
operaciones = [
    ('CARGA TANQUE', 'CT'),
    ('CARGA MARIMBA', 'CM'),
    ('CARGA MAQUINARIA', 'CMQ'),
    ('SOLICITUD', 'SO'),
    ('FACTURA', 'FA')
]
c.executemany('INSERT INTO catalogos_operaciones (tipo_operacion, codigo_operacion) VALUES (?, ?)', operaciones)
db.commit()
db.close()
print('Tabla catalogos_operaciones creada e insertada.')

