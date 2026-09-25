import psycopg2
conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor()

# 1. Update Mexico-Toluca in consumos
cur.execute("UPDATE diesel.consumos SET obra_destino = 'México - Toluca' WHERE obra_destino = 'Mexico-Toluca'")
print(f"Updated {cur.rowcount} consumos for Mexico-Toluca")

# 2. Fix topes in week 28 using week 27
cur.execute("SELECT referencia, litros_autorizados FROM catalogos.autorizaciones WHERE semana='27'")
w27 = cur.fetchall()
for ref, litros in w27:
    cur.execute("UPDATE catalogos.autorizaciones SET litros_autorizados = %s WHERE semana='28' AND referencia=%s", (litros, ref))
print(f"Copied {len(w27)} topes from week 27 to week 28")

conn.commit()
cur.close()
conn.close()
