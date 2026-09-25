from sync_s33_consumos import sheet_cargas
from app_admin import get_db

db = get_db()
db_cargas = [dict(r) for r in db.execute("SELECT id, folio_conciliacion, fecha, conductor, gasolineria, importe_total, placa, foto_evidencia IS NOT NULL as has_foto FROM gasolina.consumos WHERE semana = '33' ORDER BY id").fetchall()]

print("--- SHEET CARGAS NOT EXACTLY IN DB ---")
for sc in sheet_cargas:
    matched = False
    for dc in db_cargas:
        if dc['conductor'].strip().upper() == sc['conductor'].strip().upper() and abs(float(dc['importe_total']) - sc['importe']) < 0.05 and dc['gasolineria'].upper() == sc['gasolineria'].upper():
            matched = True
            break
    if not matched:
        print(f"SHEET ONLY: {sc['fecha']} | {sc['conductor']} | {sc['gasolineria']} | ${sc['importe']:.2f} | Folio: {sc['folio_sheet']}")

print("\n--- DB CARGAS NOT IN SHEET ---")
for dc in db_cargas:
    matched = False
    for sc in sheet_cargas:
        if dc['conductor'].strip().upper() == sc['conductor'].strip().upper() and abs(float(dc['importe_total']) - sc['importe']) < 0.05 and dc['gasolineria'].upper() == sc['gasolineria'].upper():
            matched = True
            break
    if not matched:
        print(f"DB ONLY: {dc['id']} | {dc['fecha']} | {dc['conductor']} | {dc['gasolineria']} | ${float(dc['importe_total']):.2f} | Folio: {dc['folio_conciliacion']}")

db.close()
