import psycopg2
from psycopg2.extras import DictCursor
import pandas as pd
import unicodedata

def normalize(text):
    if not text:
        return ""
    text = unicodedata.normalize('NFKD', str(text)).encode('ASCII', 'ignore').decode('utf-8')
    return text.strip().upper()

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

cur.execute("SELECT * FROM catalogos.obras ORDER BY codigo;")
rows = cur.fetchall()

print(f"{'CÓDIGO':<8} | {'NOMBRE':<35} | {'INGENIERO RESPONSABLE':<30} | {'RESPONSABLE DEFAULT':<30}")
print("-" * 110)
for r in rows:
    print(f"{r['codigo'] or 'None':<8} | {r['nombre'] or 'None':<35} | {r['ingeniero_responsable'] or 'None':<30} | {r['responsable_default'] or 'None':<30}")

print("\n=== ANÁLISIS DE DUPLICADOS Y SIMILITUDES ===")
# Agrupar por nombre normalizado
groups = {}
for r in rows:
    norm = normalize(r['nombre'])
    # simplificaciones adicionales para detectar variantes
    key = norm.replace("OBRA ", "").replace(" - ", " ").replace("-", " ")
    groups.setdefault(key, []).append(r)

for k, v in sorted(groups.items()):
    if len(v) > 1:
        print(f"\nGRUPO DUPLICADO: '{k}'")
        for item in v:
            print(f"  -> Código: {item['codigo']:<6} | Nombre: '{item['nombre']}' | Ing: {item['ingeniero_responsable']}")

print("\n=== VALORES EN GASOLINA.CONSUMOS ===")
cur.execute("SELECT obra_destino, COUNT(*) FROM gasolina.consumos GROUP BY obra_destino ORDER BY obra_destino;")
for r in cur.fetchall():
    print(dict(r))

conn.close()
