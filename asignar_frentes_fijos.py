import sqlite3

def asignar_frentes_fijos():
    conn = sqlite3.connect('fenix.db')
    cur = conn.cursor()

    # 1. Insertar las 3 obras fijas si no existen
    obras_fijas = [
        ('PPE', 'Planta Pegaso'),
        ('PHX', 'Planta Huixquilucan'),
        ('MPE', 'Maquinaria Pegaso')
    ]
    
    for cod, nom in obras_fijas:
        cur.execute("INSERT OR IGNORE INTO fenix_obras (codigo, nombre) VALUES (?, ?)", (cod, nom))
    
    # Obtener sus IDs
    cur.execute("SELECT id FROM fenix_obras WHERE nombre='Planta Pegaso'")
    id_pap = cur.fetchone()[0]
    
    cur.execute("SELECT id FROM fenix_obras WHERE nombre='Planta Huixquilucan'")
    id_pah = cur.fetchone()[0]
    
    cur.execute("SELECT id FROM fenix_obras WHERE nombre='Maquinaria Pegaso'")
    id_mp = cur.fetchone()[0]

    # 2. Asignar los consumos sin obra basados en el prefijo del folio
    # MP -> Maquinaria Pegaso
    cur.execute("UPDATE fenix_movimientos_combustible SET obra_id = ? WHERE obra_id IS NULL AND folio_vale LIKE 'CO-MP-%'", (id_mp,))
    mp_count = cur.rowcount
    
    # PAH -> Planta Huixquilucan
    cur.execute("UPDATE fenix_movimientos_combustible SET obra_id = ? WHERE obra_id IS NULL AND folio_vale LIKE 'CO-PAH-%'", (id_pah,))
    pah_count = cur.rowcount
    
    # PAP -> Planta Pegaso
    cur.execute("UPDATE fenix_movimientos_combustible SET obra_id = ? WHERE obra_id IS NULL AND folio_vale LIKE 'CO-PAP-%'", (id_pap,))
    pap_count = cur.rowcount

    conn.commit()
    conn.close()

    print(f"Obras fijas creadas y asignadas:")
    print(f" - Maquinaria Pegaso (MP): {mp_count} registros asignados")
    print(f" - Planta Huixquilucan (PAH): {pah_count} registros asignados")
    print(f" - Planta Pegaso (PAP): {pap_count} registros asignados")

if __name__ == '__main__':
    asignar_frentes_fijos()
