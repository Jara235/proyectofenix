# -*- coding: utf-8 -*-
import sys
sys.path.append(r'c:\Users\JOSE\Desktop\Proyecto fenix')
from app_admin import get_db
db = get_db()

# Debug dia 09/07 semana 28 - Pedido (solicitudes APROBADAS)
print("=== SOLICITUDES 2026-07-09 semana 28 ===")
rows = db.execute("""
    SELECT folio_solicitud, litros, estatus_conciliacion, obra_destino
    FROM diesel.solicitudes 
    WHERE fecha::text = '2026-07-09' AND semana = '28'
    ORDER BY obra_destino
""").fetchall()
total = 0
for r in rows:
    inc = float(r['litros'] or 0)
    marca = "CUENTA" if r['estatus_conciliacion'] == 'APROBADO' else "EXCLUIDA"
    print(f"  [{r['estatus_conciliacion']}] [{marca}] {r['obra_destino']} | {inc} L")
    if r['estatus_conciliacion'] == 'APROBADO':
        total += inc
print(f"TOTAL APROBADAS: {total}")
print()

# Tambien revisar el 07 (martes) para el registro que borro
print("=== SOLICITUDES 2026-07-07 (martes) semana 28 ===")
rows2 = db.execute("""
    SELECT folio_solicitud, litros, estatus_conciliacion, obra_destino
    FROM diesel.solicitudes 
    WHERE fecha::text = '2026-07-07' AND semana = '28'
    ORDER BY obra_destino
""").fetchall()
total2 = 0
for r in rows2:
    inc = float(r['litros'] or 0)
    print(f"  [{r['estatus_conciliacion']}] {r['obra_destino']} | {inc} L | {r['folio_solicitud']}")
    if r['estatus_conciliacion'] == 'APROBADO':
        total2 += inc
print(f"TOTAL APROBADAS martes: {total2}")

db.close()
