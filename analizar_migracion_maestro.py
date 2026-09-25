import psycopg2
import pandas as pd
import json
import sys, io
from datetime import datetime, date

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

MAESTRO_PATH = r"c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_DIESEL_NUEVO.xlsx"

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor()

print("Conectado a PostgreSQL")

# Leer todos los datos del maestro Excel
print("\nLeyendo BD_DIESEL del Maestro Excel...")
df_consumos = pd.read_excel(MAESTRO_PATH, sheet_name='BD_DIESEL')
df_consumos = df_consumos.dropna(how='all')
print(f"  Registros de consumos en Excel: {len(df_consumos)}")

print("\nLeyendo BD_SOLICITUD del Maestro Excel...")
df_solicitudes = pd.read_excel(MAESTRO_PATH, sheet_name='BD_SOLICITUD')
df_solicitudes = df_solicitudes.dropna(how='all')
print(f"  Registros de solicitudes en Excel: {len(df_solicitudes)}")

print("\nLeyendo BD_FACTURAS del Maestro Excel...")
df_facturas = pd.read_excel(MAESTRO_PATH, sheet_name='BD_FACTURAS')
df_facturas = df_facturas.dropna(how='all')
print(f"  Registros de facturas en Excel: {len(df_facturas)}")

# Ver cuanto tenemos ya en Postgres
cur.execute("SELECT COUNT(*) FROM diesel.consumos")
print(f"\nPostgres - diesel.consumos actual: {cur.fetchone()[0]} registros")

cur.execute("SELECT COUNT(*) FROM diesel.facturas")
print(f"Postgres - diesel.facturas actual: {cur.fetchone()[0]} registros")

# Ver las semanas en Excel que no estan en Postgres
cur.execute("SELECT DISTINCT semana FROM diesel.consumos ORDER BY semana")
semanas_pg = set([r[0] for r in cur.fetchall()])
semanas_excel = set(df_consumos['SEMANA'].dropna().unique())
semanas_nuevas = semanas_excel - semanas_pg
semanas_pg_no_excel = semanas_pg - semanas_excel

print(f"\nSemanas en Excel: {sorted(semanas_excel)}")
print(f"Semanas en Postgres: {sorted(semanas_pg)}")
print(f"Semanas NUEVAS a migrar: {sorted(semanas_nuevas)}")
if semanas_pg_no_excel:
    print(f"Semanas en PG que no estan en Excel: {sorted(semanas_pg_no_excel)}")

cur.close()
conn.close()
