import sqlite3

def agregar_identificadores():
    conn = sqlite3.connect('fenix.db')
    cur = conn.cursor()

    # Crear tabla de prefijos
    cur.execute("""
        CREATE TABLE IF NOT EXISTS fenix_prefijos_obra (
            prefijo TEXT PRIMARY KEY,
            obra_id INTEGER,
            FOREIGN KEY(obra_id) REFERENCES fenix_obras(id)
        )
    """)

    # Obtener IDs
    cur.execute("SELECT id, nombre FROM fenix_obras")
    obras = {nombre: id_obra for id_obra, nombre in cur.fetchall()}

    # Mapeo de prefijos
    mapeo = [
        ('MP',  obras.get('Maquinaria Pegaso')),
        ('PAH', obras.get('Planta Huixquilucan')),
        ('PAP', obras.get('Planta Pegaso')),
        ('DR',  obras.get('Maquinaria Pegaso')), # Por defecto si es Doble Rodillo
        ('FOL', obras.get('Maquinaria Pegaso'))  # Por defecto si es Folio extra
    ]

    for pref, o_id in mapeo:
        if o_id:
            cur.execute("INSERT OR REPLACE INTO fenix_prefijos_obra (prefijo, obra_id) VALUES (?, ?)", (pref, o_id))

    # Asignar los restantes
    cur.execute("UPDATE fenix_movimientos_combustible SET obra_id = ? WHERE obra_id IS NULL AND folio_vale LIKE 'CO-DR-%'", (obras.get('Maquinaria Pegaso'),))
    cur.execute("UPDATE fenix_movimientos_combustible SET obra_id = ? WHERE obra_id IS NULL AND folio_vale LIKE 'CO-FOL-%'", (obras.get('Maquinaria Pegaso'),))

    # Mostrar restantes
    cur.execute("SELECT COUNT(*) FROM fenix_movimientos_combustible WHERE tipo_movimiento='CONSUMO' AND obra_id IS NULL")
    restantes = cur.fetchone()[0]

    conn.commit()
    conn.close()

    print(f"Tabla de identificadores creada.")
    print(f"Litros sin asignar restantes: {restantes}")

if __name__ == '__main__':
    agregar_identificadores()
