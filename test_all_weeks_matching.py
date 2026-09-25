from app_admin import get_db
from datetime import datetime

db = get_db()

for sem in [26, 27, 28, 29, 30, 31, 32, 33]:
    sql_auths = "SELECT * FROM gasolina.autorizaciones_semanal WHERE semana = %s ORDER BY id ASC"
    auths_raw = db.execute(sql_auths, (sem,)).fetchall()
    
    sql_consumos = "SELECT * FROM gasolina.consumos WHERE estatus_revision != 'RECHAZADO' AND semana = %s ORDER BY fecha ASC, id ASC"
    cargas_raw = db.execute(sql_consumos, (str(sem),)).fetchall()
    
    auth_map = {a['id']: {'auth': a, 'cargas': []} for a in auths_raw}
    cargas_asignadas = set()
    
    for c in cargas_raw:
        c_placa = (c['placa'] or '').strip().upper()
        if c_placa in ['S/P', 'NONE']: c_placa = ''
        c_cond = (c['conductor'] or '').strip().upper()
        c_veh = (c['vehiculo'] or '').strip().upper()
        c_obra = (c['obra_destino'] or '').strip().upper()
        best_auth_id = None
        
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

        if not best_auth_id and c_placa:
            matching_auths = [a for a in auths_raw if a['placas'] and (a['placas'].strip().upper() == c_placa)]
            if len(matching_auths) == 1:
                best_auth_id = matching_auths[0]['id']
            elif len(matching_auths) > 1:
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

        if not best_auth_id and c_cond:
            matching = [a['id'] for a in auths_raw if (a['responsable'] or '').strip().upper() == c_cond]
            if len(matching) == 1:
                best_auth_id = matching[0]

        if best_auth_id:
            auth_map[best_auth_id]['cargas'].append(c)
            cargas_asignadas.add(c['id'])
            
    excedidos = []
    tot_exc = 0.0
    for a_id, d in auth_map.items():
        auth_m = float(d['auth']['importe_semanal'] or 0)
        cons_m = sum(float(c['importe_total'] or 0) for c in d['cargas'])
        if (cons_m - auth_m) > 1.0:
            excedidos.append((d['auth']['responsable'], auth_m, cons_m, cons_m - auth_m))
            tot_exc += (cons_m - auth_m)
            
    print(f"Semana {sem:2d}: {len(cargas_asignadas)}/{len(cargas_raw)} cargas asignadas | {len(excedidos)} excedidos | Total Exceso: ${tot_exc:,.2f}")
