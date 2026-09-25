from app_admin import get_db
import openpyxl

wb = openpyxl.load_workbook('gasolina/conciliacion_gasolina_google_sheets.xlsx', data_only=True)

from extract_s33_clean import parse_sheet_semana

auths_s33 = parse_sheet_semana(wb['SEMANA 33'], 33)

db = get_db()
consumos_raw = db.execute("""
    SELECT id, fecha, semana, conductor, placa, vehiculo, obra_destino, gasolineria,
           importe_total, litros, costo_por_litro, folio_conciliacion, observaciones,
           foto_evidencia IS NOT NULL as tiene_foto
    FROM gasolina.consumos
    WHERE estatus_revision != 'RECHAZADO' AND semana = '33'
    ORDER BY fecha ASC, id ASC
""").fetchall()

auth_map = {idx: {'auth': a, 'cargas': []} for idx, a in enumerate(auths_s33)}
cargas_asignadas = set()

for c in consumos_raw:
    c_placa = (c['placa'] or '').strip().upper()
    if c_placa in ['S/P', 'NONE']: c_placa = ''
    c_cond = (c['conductor'] or '').strip().upper()
    c_veh = (c['vehiculo'] or '').strip().upper()
    c_obra = (c['obra_destino'] or '').strip().upper()

    best_idx = None
    
    # 1. Si es Motores Lowboy
    if 'MOTORES LOWBOY' in c_veh or 'MOTORES LOWBOY' in c_cond:
        for idx, a in enumerate(auths_s33):
            if 'MOTORES LOWBOY' in a['responsable'].upper() or 'MOTORES LOWBOY' in a['unidad_equipo'].upper():
                best_idx = idx
                break
                
    # 2. Si es Cortadora de Concreto
    elif 'CORTADORA DE CONCRETO' in c_veh or 'CORTADORA' in c_cond:
        for idx, a in enumerate(auths_s33):
            if 'CORTADORA' in a['responsable'].upper() or 'CORTADORA' in a['unidad_equipo'].upper():
                best_idx = idx
                break

    # 3. Coincidencia exacta por placa + obra/responsable si hay duplicadas (como PAT8298)
    elif c_placa:
        matching_indices = [idx for idx, a in enumerate(auths_s33) if a['placas'] == c_placa]
        if len(matching_indices) == 1:
            best_idx = matching_indices[0]
        elif len(matching_indices) > 1:
            # Buscar coincidencia de obra o empresa
            for idx in matching_indices:
                a = auths_s33[idx]
                if c_obra and (c_obra in a['centro_trabajo'].upper() or a['centro_trabajo'].upper() in c_obra):
                    best_idx = idx
                    break
            if best_idx is None:
                best_idx = matching_indices[0]

    # 4. Equipo menor por conductor / obra
    elif 'EQUIPO MENOR' in c_veh:
        for idx, a in enumerate(auths_s33):
            if 'EQUIPO MENOR' in a['unidad_equipo'].upper():
                a_cond = a['responsable'].upper()
                if c_cond and (c_cond == a_cond or c_cond in a_cond or a_cond in c_cond):
                    best_idx = idx
                    break

    # 5. Coincidencia por conductor
    if best_idx is None and c_cond:
        matching = [idx for idx, a in enumerate(auths_s33) if a['responsable'].upper() == c_cond or c_cond in a['responsable'].upper()]
        if len(matching) == 1:
            best_idx = matching[0]

    if best_idx is not None:
        auth_map[best_idx]['cargas'].append(c)
        cargas_asignadas.add(c['id'])

print(f"Cargas asignadas: {len(cargas_asignadas)} de {len(consumos_raw)}")

excedidos = []
for idx, data in auth_map.items():
    a = data['auth']
    cs = data['cargas']
    auth_m = float(a['importe_semanal'] or 0)
    cons_m = sum(float(c['importe_total'] or 0) for c in cs)
    
    # Manejo especial de Samuel Ortega Silva si aplica la fórmula de la hoja
    if 'SAMUEL ORTEGA' in a['responsable'].upper():
        # En la hoja Samuel sólo tiene en cuenta los consumos de la semana regular o límite
        # Si tiene 4 cargas de $1000, $1500, $500, $1000 ($4000 total) pero autorizado $3000
        # Veamos por qué la hoja puso Remanente = 0: Col W (Levet 14-ago) o Col G (Levet 10-ago)
        pass
        
    diff = auth_m - cons_m
    if cons_m > auth_m:
        excedidos.append({
            'responsable': a['responsable'],
            'obra': a['centro_trabajo'],
            'unidad': a['unidad_equipo'],
            'placas': a['placas'],
            'autorizado': auth_m,
            'consumido': cons_m,
            'exceso': cons_m - auth_m
        })

print(f"\nExcedidos encontrados ({len(excedidos)}):")
for ex in excedidos:
    print(f"  {ex['responsable']} | {ex['obra']} | {ex['unidad']} | {ex['placas']} | Auth: ${ex['autorizado']:,.2f} | Cons: ${ex['consumido']:,.2f} | Exceso: +${ex['exceso']:,.2f}")
