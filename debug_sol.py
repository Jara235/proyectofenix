# -*- coding: utf-8 -*-
import sys
sys.path.append(r'c:\Users\JOSE\Desktop\Proyecto fenix')
from app_admin import get_db
db = get_db()

# Check what estatus values exist for solicitudes on 2026-07-06 semana 28
rows = db.execute("""
    SELECT folio_solicitud, fecha::text, litros, estatus_conciliacion, obra_destino
    FROM diesel.solicitudes 
    WHERE fecha::text = '2026-07-06' AND semana = '28'
    ORDER BY obra_destino
""").fetchall()
print(f'Total registros 2026-07-06 semana 28: {len(rows)}')
total = 0
for r in rows:
    print(f"  [{r['estatus_conciliacion']}] {r['obra_destino']} | {r['litros']} L | {r['folio_solicitud']}")
    total += float(r['litros'] or 0)
print(f'SUMA TOTAL (todos los estatus): {total}')

print()
# Only approved
rows_apro = db.execute("""
    SELECT SUM(litros) as total
    FROM diesel.solicitudes 
    WHERE fecha::text = '2026-07-06' AND semana = '28' AND estatus_conciliacion = 'APROBADO'
""").fetchone()
print(f'SUMA solo APROBADAS: {rows_apro[0]}')

# Check all distinct statuses in solicitudes
statuses = db.execute("SELECT DISTINCT estatus_conciliacion FROM diesel.solicitudes").fetchall()
print(f'Estatus existentes: {[r[0] for r in statuses]}')
db.close()
