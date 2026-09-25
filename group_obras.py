import psycopg2

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor()

def group_obras(target, sources):
    print(f"Grouping {sources} into {target}")
    
    # 1. Update consumos (diesel and gasolina)
    for table in ['diesel.consumos', 'gasolina.consumos']:
        for src in sources:
            cur.execute(f"UPDATE {table} SET obra_destino = %s WHERE obra_destino = %s", (target, src))
            print(f"  - Updated {cur.rowcount} consumos in {table} from {src} to {target}")

    # 2. Update autorizaciones (need to sum up if target exists, then delete sources)
    cur.execute("SELECT id, tipo, semana, referencia, litros_autorizados FROM catalogos.autorizaciones")
    all_auths = cur.fetchall()
    
    # Dictionary to accumulate liters: (tipo, semana, target) -> sum
    additions = {}
    ids_to_delete = []
    
    for row in all_auths:
        id_auth, tipo, semana, ref, litros = row
        if ref in sources:
            # this needs to be moved to target
            key = (tipo, semana, target)
            additions[key] = additions.get(key, 0) + litros
            ids_to_delete.append(id_auth)
            
    # Add accumulated liters to target
    for (tipo, semana, target_ref), sum_litros in additions.items():
        if sum_litros > 0:
            # Check if target exists
            cur.execute("SELECT id, litros_autorizados FROM catalogos.autorizaciones WHERE tipo=%s AND semana=%s AND referencia=%s", (tipo, semana, target_ref))
            tgt_row = cur.fetchone()
            if tgt_row:
                cur.execute("UPDATE catalogos.autorizaciones SET litros_autorizados = litros_autorizados + %s WHERE id=%s", (sum_litros, tgt_row[0]))
            else:
                cur.execute("INSERT INTO catalogos.autorizaciones (tipo, semana, referencia, litros_autorizados) VALUES (%s, %s, %s, %s)", (tipo, semana, target_ref, sum_litros))
    
    # Delete sources
    if ids_to_delete:
        cur.execute("DELETE FROM catalogos.autorizaciones WHERE id = ANY(%s)", (ids_to_delete,))
        print(f"  - Merged and deleted {len(ids_to_delete)} source autorizaciones")

    # 3. Delete from catalogos.obras
    for src in sources:
        cur.execute("DELETE FROM catalogos.obras WHERE nombre = %s", (src,))
        print(f"  - Deleted {src} from catalogos.obras (rows: {cur.rowcount})")

group_obras('Planta Pegaso', ['Planta Asfalto Pegaso', 'Maquinaria Pegaso'])
group_obras('Tanque Pegaso', ['TRANSPORTES FLOTILLA'])

conn.commit()
cur.close()
conn.close()
print("Done!")
