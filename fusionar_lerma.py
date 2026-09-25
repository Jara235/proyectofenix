import psycopg2

def fusionar_lerma():
    conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
    cur = conn.cursor()
    
    old_names = ['Lerma - Tres Marías']
    new_name = 'Lerma - Tenango'
    
    # Update Diesel
    cur.execute("UPDATE diesel.consumos SET obra_destino = %s WHERE obra_destino = ANY(%s)", (new_name, old_names))
    
    # Update Gasolina
    cur.execute("UPDATE gasolina.consumos SET obra_destino = %s WHERE obra_destino = ANY(%s)", (new_name, old_names))
    
    # Remove old from catalogos
    cur.execute("DELETE FROM catalogos.obras WHERE nombre = ANY(%s)", (old_names,))
    
    conn.commit()
    print("Fusión completada!")
    conn.close()

if __name__ == '__main__':
    fusionar_lerma()
