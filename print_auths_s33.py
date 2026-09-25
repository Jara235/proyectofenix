from app_admin import get_db

db = get_db()
rows = db.execute("""
    SELECT id, num_renglon, empresa, responsable, centro_trabajo, unidad_equipo, placas, importe_semanal
    FROM gasolina.autorizaciones_semanal
    WHERE semana = 33
    ORDER BY id ASC
""").fetchall()

print(f"Total rows in semana 33: {len(rows)}")
for r in rows:
    print(f"{r['num_renglon']:2d} | {r['empresa']:4s} | {str(r['responsable'])[:25]:25s} | {str(r['centro_trabajo'])[:20]:20s} | {str(r['unidad_equipo'])[:15]:15s} | {str(r['placas'])[:8]:8s} | {r['importe_semanal']}")
