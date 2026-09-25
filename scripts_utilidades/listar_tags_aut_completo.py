import psycopg2
from psycopg2.extras import DictCursor

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

cur.execute("SELECT * FROM tags.autorizaciones ORDER BY empresa, responsable;")
rows = cur.fetchall()
print(f"Total autorizaciones de tags: {len(rows)}")
for r in rows:
    print(f"ID:{r['id']:2d} | Emp:{r['empresa']:<4} | Tag:{r['tag']:<15} | Resp:{r['responsable']:<30} | Placas:{r['placas']:<10} | Tipo:{r['tipo_unidad']:<15} | Aut:${r['monto_autorizado']:>10.2f}")

print("\n=== VERIFICAR tags.movimientos POR RESPONSABLE (Semana 32 o general) ===")
cur.execute("""
    SELECT DISTINCT responsable, no_economico, tag, placas, obra_asignada
    FROM tags.movimientos
    WHERE responsable ILIKE '%BRYAN%' OR no_economico ILIKE '%BRYAN%' OR tag ILIKE '%BRYAN%';
""")
for r in cur.fetchall():
    print(dict(r))

conn.close()
