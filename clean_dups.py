import psycopg2

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor()

# 1. Eliminar filas vacías
cur.execute("DELETE FROM diesel.solicitudes WHERE fecha IS NULL AND (litros IS NULL OR litros = 0)")
print("Filas vacías eliminadas:", cur.rowcount)

# 2. Mantener solo el primer ID para los duplicados exactos en diesel.solicitudes
cur.execute("""
    DELETE FROM diesel.solicitudes a USING (
      SELECT MIN(id) as min_id, fecha, importe_total, litros, obra_destino, equipo_economico
      FROM diesel.solicitudes 
      GROUP BY fecha, importe_total, litros, obra_destino, equipo_economico
      HAVING COUNT(*) > 1
    ) b
    WHERE a.fecha = b.fecha AND a.importe_total = b.importe_total AND a.litros = b.litros 
      AND (a.obra_destino = b.obra_destino OR (a.obra_destino IS NULL AND b.obra_destino IS NULL))
      AND (a.equipo_economico = b.equipo_economico OR (a.equipo_economico IS NULL AND b.equipo_economico IS NULL))
      AND a.id > b.min_id;
""")
print("Duplicados eliminados:", cur.rowcount)

conn.commit()
conn.close()
print("Depuración completada.")
