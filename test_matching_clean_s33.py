from app_admin import get_db
from datetime import datetime

db = get_db()
semana_num = 33

sql_auths = """
    SELECT s.id, s.num_renglon, s.empresa, s.responsable, s.centro_trabajo, s.unidad_equipo, s.placas, s.importe_semanal
    FROM gasolina.autorizaciones_semanal s
    WHERE s.semana = %s
    ORDER BY s.id ASC
"""
auths_raw = db.execute(sql_auths, (semana_num,)).fetchall()

sql_consumos = """
    SELECT id, fecha, semana, conductor, placa, vehiculo, obra_destino, gasolineria,
           importe_total, litros, costo_por_litro, folio_conciliacion, observaciones,
           foto_evidencia IS NOT NULL as tiene_foto
    FROM gasolina.consumos
    WHERE estatus_revision != 'RECHAZADO' AND semana = %s
    ORDER BY fecha ASC, id ASC
"""
cargas_raw = db.execute(sql_consumos, (str(semana_num),)).fetchall()

# 4. Mapeo preciso de cargas a autorizaciones
auth_map = {a['id']: {'auth': a, 'cargas': []} for a in auths_raw}
cargas_asignadas = set()

for c in cargas_raw:
    c_placa = (c['placa'] or '').strip().upper()
    if c_placa in ['S/P', 'NONE']: c_placa = ''
    c_cond = (c['conductor'] or '').strip().upper()
    c_veh = (c['vehiculo'] or '').strip().upper()
    c_obra = (c['obra_destino'] or '').strip().upper()

    best_auth_id = None
    
    # 1. Equipos especiales específicos (Motores Lowboy, Cortadora)
    if 'MOTORES LOWBOY' in c_veh or 'MOTORES LOWBOY' in c_cond:
        for a in auths_raw:
            a_u = (a['unidad_equipo'] or '').strip().upper()
            a_r = (a['responsable'] or '').strip().upper()
            if 'MOTORES LOWBOY' in a_u or 'MOTORES LOWBOY' in a_r:
                best_auth_id = a['id']
                break
    elif 'CORTADORA' in c_veh or 'CORTADORA' in c_cond:
        for a in auths_raw:
            a_u = (a['unidad_equipo'] or '').strip().upper()
            a_r = (a['responsable'] or '').strip().upper()
            if 'CORTADORA' in a_u or 'CORTADORA' in a_r:
                best_auth_id = a['id']
                break

    # 2. Coincidencia por placa
    if not best_auth_id and c_placa:
        matching_auths = [a for a in auths_raw if a['placas'] and (a['placas'].strip().upper() == c_placa)]
        if len(matching_auths) == 1:
            best_auth_id = matching_auths[0]['id']
        elif len(matching_auths) > 1:
            # Desambiguar por obra o responsable
            for a in matching_auths:
                a_obra = (a['centro_trabajo'] or '').strip().upper()
                a_resp = (a['responsable'] or '').strip().upper()
                if c_obra and (c_obra in a_obra or a_obra in c_obra):
                    best_auth_id = a['id']
                    break
                if c_cond and (c_cond in a_resp or a_resp in c_cond):
                    best_auth_id = a['id']
                    break
            if not best_auth_id:
                best_auth_id = matching_auths[0]['id']

    # 3. Coincidencia por equipo menor
    if not best_auth_id and ('EQUIPO MENOR' in c_veh or not c_placa):
        for a in auths_raw:
            a_u = (a['unidad_equipo'] or '').strip().upper()
            a_r = (a['responsable'] or '').strip().upper()
            a_obra = (a['centro_trabajo'] or '').strip().upper()
            if 'EQUIPO MENOR' in a_u or not a['placas']:
                if c_cond and (c_cond == a_r or c_cond in a_r or a_r in c_cond):
                    best_auth_id = a['id']
                    break
                elif c_obra and (c_obra == a_obra or c_obra in a_obra or a_obra in c_obra):
                    best_auth_id = a['id']
                    break

    # 4. Coincidencia por conductor general
    if not best_auth_id and c_cond:
        matching = [a['id'] for a in auths_raw if (a['responsable'] or '').strip().upper() == c_cond]
        if len(matching) == 1:
            best_auth_id = matching[0]

    if best_auth_id:
        auth_map[best_auth_id]['cargas'].append(c)
        cargas_asignadas.add(c['id'])

personas_list = []
tot_presupuesto = 0.0
tot_consumo = 0.0
tot_litros = 0.0
tot_excedente = 0.0
excedidos_list = []
dias_semana_map = {'LUNES': 0.0, 'MARTES': 0.0, 'MIERCOLES': 0.0, 'JUEVES': 0.0, 'VIERNES': 0.0, 'SABADO': 0.0, 'DOMINGO': 0.0}
dias_semana_litros = {'LUNES': 0.0, 'MARTES': 0.0, 'MIERCOLES': 0.0, 'JUEVES': 0.0, 'VIERNES': 0.0, 'SABADO': 0.0, 'DOMINGO': 0.0}
estaciones_map = {}
estaciones_litros = {}

dias_nombre_es = {0: 'LUNES', 1: 'MARTES', 2: 'MIERCOLES', 3: 'JUEVES', 4: 'VIERNES', 5: 'SABADO', 6: 'DOMINGO'}

for a_id, data in auth_map.items():
    a = data['auth']
    cs = data['cargas']
    auth_m = float(a['importe_semanal'] or 0)
    cons_m = sum(float(c['importe_total'] or 0) for c in cs)
    lts_m = sum(float(c['litros'] or 0) for c in cs)
    
    # Tolerancia de $1.00 para centavos
    is_excedido = (cons_m - auth_m) > 1.0
    monto_exc = (cons_m - auth_m) if is_excedido else 0.0
    pct = (cons_m / auth_m * 100.0) if auth_m > 0 else (100.0 if cons_m > 0 else 0.0)
    pct_exc = round(((cons_m - auth_m) / auth_m * 100.0), 1) if auth_m > 0 and is_excedido else 0.0

    tot_presupuesto += auth_m
    tot_consumo += cons_m
    tot_litros += lts_m
    if is_excedido:
        tot_excedente += monto_exc

    detalles = []
    for c in cs:
        f_str = str(c['fecha'] or '')
        dia_str = 'N/A'
        try:
            dt_obj = datetime.strptime(f_str, '%Y-%m-%d')
            dia_str = dias_nombre_es.get(dt_obj.weekday(), 'N/A')
        except:
            pass

        imp_c = float(c['importe_total'] or 0)
        lts_c = float(c['litros'] or 0)
        est_c = (c['gasolineria'] or 'LEVET').strip().upper()
        if not est_c or est_c == 'NONE':
            est_c = 'LEVET'

        if dia_str in dias_semana_map:
            dias_semana_map[dia_str] += imp_c
            dias_semana_litros[dia_str] += lts_c

        estaciones_map[est_c] = estaciones_map.get(est_c, 0.0) + imp_c
        estaciones_litros[est_c] = estaciones_litros.get(est_c, 0.0) + lts_c

        detalles.append({
            'id': c['id'],
            'fecha': f_str,
            'dia': dia_str,
            'gasolinera': est_c,
            'folio': c['folio_conciliacion'] or f"GAS-{c['id']}",
            'litros': round(lts_c, 2),
            'costo_litro': round(float(c['costo_por_litro'] or 23.90), 2),
            'importe': round(imp_c, 2),
            'tiene_foto': bool(c['tiene_foto']),
            'observaciones': c['observaciones'] or ''
        })

    p_obj = {
        'auth_id': a['id'],
        'empresa': a['empresa'] or 'JDJ',
        'num_renglon': a['num_renglon'] or len(personas_list) + 1,
        'responsable': a['responsable'] or 'Personal Asignado',
        'centro_trabajo': a['centro_trabajo'] or 'General',
        'unidad_equipo': a['unidad_equipo'] or 'Vehículo',
        'placas': a['placas'] or 'S/P',
        'autorizado': round(auth_m, 2),
        'consumido': round(cons_m, 2),
        'litros': round(lts_m, 2),
        'diferencia': round(auth_m - cons_m, 2),
        'excedido': is_excedido,
        'monto_excedido': round(monto_exc, 2),
        'porcentaje_uso': round(pct, 1),
        'porcentaje_exceso': pct_exc,
        'num_cargas': len(cs),
        'detalle_cargas': detalles
    }
    personas_list.append(p_obj)
    if is_excedido:
        excedidos_list.append(p_obj)

excedidos_list.sort(key=lambda x: x['monto_excedido'], reverse=True)

print(f"Total personas: {len(personas_list)}")
print(f"Total excedidos: {len(excedidos_list)}")
print(f"Total monto excedido: ${tot_excedente:,.2f}")
for ex in excedidos_list:
    print(f"  {ex['responsable']} | {ex['centro_trabajo']} | {ex['placas']} | Auth: ${ex['autorizado']:,.2f} | Cons: ${ex['consumido']:,.2f} | Exc: +${ex['monto_excedido']:,.2f} (+{ex['porcentaje_exceso']}%)")
