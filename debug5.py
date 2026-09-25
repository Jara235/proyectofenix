# -*- coding: utf-8 -*-
import sys
sys.path.append(r'c:\Users\JOSE\Desktop\Proyecto fenix')
from app_admin import get_db
db = get_db()

# All SOL-D-20260717... that are APROBADO (these are the duplicate captures from Jul 17)
rows = db.execute("""
    SELECT id, folio_solicitud, fecha::text, semana, litros, estatus_conciliacion, obra_destino
    FROM diesel.solicitudes 
    WHERE folio_solicitud LIKE 'SOL-D-2026%%'
    AND estatus_conciliacion = 'APROBADO'
    ORDER BY fecha, obra_destino
""").fetchall()

print(f"Duplicados SOL-D-2026... con estatus APROBADO: {len(rows)}")
total = 0
for r in rows:
    print(f"  ID:{r['id']} Sem:{r['semana']} {r['fecha']} | {r['obra_destino']} | {r['litros']} L | {r['folio_solicitud']}")
    total += float(r['litros'] or 0)
print(f"TOTAL Litros que inflan incorrectamente: {total}")

print()
# Also show PENDIENTE ones (these are harmless since they don't count in the query)
rows2 = db.execute("""
    SELECT COUNT(*) as n, SUM(litros) as total
    FROM diesel.solicitudes 
    WHERE folio_solicitud LIKE 'SOL-D-2026%%'
    AND estatus_conciliacion = 'PENDIENTE'
""").fetchone()
print(f"Duplicados SOL-D-2026... con estatus PENDIENTE (no afectan calculo): {rows2[0]} registros, {rows2[1]} L")

db.close()
