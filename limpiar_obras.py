import psycopg2

def limpiar_obras():
    conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
    cur = conn.cursor()
    
    mapping = [
        {
            'old_names': ['BACHEO TOLUCA Y CALLE VICENTE LOMBARDO TOLEDANO', 'Bacheo Toluca'],
            'new_name': 'Bacheo Toluca',
            'codigo': 'BTL'
        },
        {
            'old_names': ['Lerma-Tenango', 'LERMA TENANGO'],
            'new_name': 'Lerma - Tenango',
            'codigo': 'LT'
        },
        {
            'old_names': ['MEXICO-TOLUCA', 'México-Toluca', 'OBRA MEXICO TOLUCA'],
            'new_name': 'México - Toluca',
            'codigo': 'MT'
        },
        {
            'old_names': ['Planta Huixquilucan', 'P.ASFALTO HUIX'],
            'new_name': 'Planta Huixquilucan',
            'codigo': 'PHX'
        },
        {
            'old_names': ['MAǪUINARIA', 'Maquinaria Pegaso'],
            'new_name': 'Maquinaria Pegaso',
            'codigo': 'MPE'
        }
    ]
    
    for m in mapping:
        # Update Diesel
        cur.execute("UPDATE diesel.consumos SET obra_destino = %s WHERE obra_destino = ANY(%s)", (m['new_name'], m['old_names']))
        
        # Update Gasolina
        cur.execute("UPDATE gasolina.consumos SET obra_destino = %s WHERE obra_destino = ANY(%s)", (m['new_name'], m['old_names']))
        
        # Remove old from catalogos
        cur.execute("DELETE FROM catalogos.obras WHERE nombre = ANY(%s)", (m['old_names'],))
        
        # Insert clean version
        cur.execute("INSERT INTO catalogos.obras (codigo, nombre, ingeniero_responsable, responsable_default) VALUES (%s, %s, '', '')", (m['codigo'], m['new_name']))
        
    conn.commit()
    print("Limpieza completada!")
    conn.close()

if __name__ == '__main__':
    limpiar_obras()
