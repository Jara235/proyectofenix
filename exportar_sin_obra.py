import sqlite3, pandas as pd, os

DB_PATH = 'c:\\Users\\JOSE\\Desktop\\Proyecto fenix\\fenix.db'
OUT_PATH = 'c:\\Users\\JOSE\\Desktop\\Proyecto fenix\\Consumos_Sin_Obra_A_Corregir.xlsx'

conn = sqlite3.connect(DB_PATH)
query = """
    SELECT folio_vale as Folio_Transaccion,
           fecha as Fecha,
           semana as Semana,
           origen_nombre as Origen,
           destino_nombre as Equipo_o_Destino,
           litros as Litros
    FROM fenix_movimientos_combustible
    WHERE tipo_movimiento='CONSUMO' AND obra_id IS NULL
    ORDER BY semana, fecha
"""
df = pd.read_sql_query(query, conn)
conn.close()

df.to_excel(OUT_PATH, index=False)
print(f"Excel guardado en {OUT_PATH}")
