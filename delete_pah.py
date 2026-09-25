import psycopg2
conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor()
# First update any consumos/facturas that might have 'Planta Asfalto Huixquilucan' to 'Planta Huixquilucan'
cur.execute("UPDATE diesel.consumos SET obra_destino = 'Planta Huixquilucan' WHERE obra_destino = 'Planta Asfalto Huixquilucan'")
cur.execute("UPDATE diesel.facturas SET punto_de_carga = 'Planta Huixquilucan' WHERE punto_de_carga = 'Planta Asfalto Huixquilucan'")
# Now delete the extra work
cur.execute("DELETE FROM catalogos.obras WHERE codigo = 'PAH'")
conn.commit()
print("Duplicado eliminado y unificado.")
