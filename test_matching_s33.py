from app_admin import get_db
import datetime

db = get_db()

# Let's inspect all weekly authorizations and consumos for semana 33
auths_raw = db.execute("""
    SELECT s.id, s.num_renglon, s.empresa, s.responsable, s.centro_trabajo, s.unidad_equipo, s.placas, s.importe_semanal
    FROM gasolina.autorizaciones_semanal s
    WHERE s.semana = 33
    ORDER BY s.id ASC
""").fetchall()

print(f"Auths raw count: {len(auths_raw)}")

consumos_raw = db.execute("""
    SELECT id, fecha, semana, conductor, placa, vehiculo, obra_destino, gasolineria,
           importe_total, litros, costo_por_litro, folio_conciliacion, observaciones,
           foto_evidencia IS NOT NULL as tiene_foto
    FROM gasolina.consumos
    WHERE estatus_revision != 'RECHAZADO' AND semana = '33'
    ORDER BY fecha ASC, id ASC
""").fetchall()

print(f"Consumos raw count: {len(consumos_raw)}")
