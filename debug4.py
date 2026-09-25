# -*- coding: utf-8 -*-
import sys
sys.path.append(r'c:\Users\JOSE\Desktop\Proyecto fenix')
from app_admin import get_db
db = get_db()

print("=== SOLICITUDES 2026-07-09 semana 28 - DETALLE COMPLETO ===")
rows = db.execute("""
    SELECT id, folio_solicitud, litros, estatus_conciliacion, obra_destino, 
           responsable, tipo_movimiento, observaciones
    FROM diesel.solicitudes 
    WHERE fecha::text = '2026-07-09' AND semana = '28'
    ORDER BY obra_destino, id
""").fetchall()
for r in rows:
    print(f"  ID:{r['id']} [{r['estatus_conciliacion']}] {r['obra_destino']} | {r['litros']} L | {r['folio_solicitud']} | obs: {r['observaciones']}")

print()
print("=== CONSUMOS 2026-07-09 semana 28 ===")
rows2 = db.execute("""
    SELECT id, folio_conciliacion, litros, estatus_revision, obra_destino, equipo
    FROM diesel.consumos 
    WHERE fecha::text = '2026-07-09' AND semana = '28'
    ORDER BY obra_destino, id
""").fetchall()
total_con = 0
for r in rows2:
    print(f"  ID:{r['id']} [{r['estatus_revision']}] {r['obra_destino']} | {r['litros']} L | {r['folio_conciliacion']} | {r['equipo']}")
    if r['estatus_revision'] == 'APROBADO':
        total_con += float(r['litros'] or 0)
print(f"Total consumos APROBADOS: {total_con}")
db.close()
