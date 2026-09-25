import json, sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app_admin import get_db

db = get_db()
semana_num = 30

cargas = db.execute("""
    SELECT id, fecha, conductor, placa, vehiculo, obra_destino, gasolineria, importe_total, litros, folio_conciliacion, foto_evidencia IS NOT NULL as tiene_foto
    FROM gasolina.consumos
    WHERE semana = %s AND estatus_revision != 'RECHAZADO'
    ORDER BY fecha ASC, id ASC
""", (str(semana_num),)).fetchall()

auths = db.execute("""
    SELECT id, num_renglon, empresa, responsable, centro_trabajo, unidad_equipo, placas, importe_semanal
    FROM gasolina.autorizaciones_semanal
    WHERE semana = %s
    ORDER BY id ASC
""", (semana_num,)).fetchall()

auth_map = {a['id']: {'auth': a, 'cargas': []} for a in auths}
unmatched = []

for c in cargas:
    c_placa = (c['placa'] or '').strip().upper()
    c_cond = (c['conductor'] or '').strip().upper()
    c_veh = (c['vehiculo'] or '').strip().upper()
    c_obra = (c['obra_destino'] or '').strip().upper()
    
    best_auth_id = None
    if c_placa and c_placa != 'S/P':
        for a in auths:
            a_placa = (a['placas'] or '').strip().upper()
            if a_placa and (a_placa == c_placa or a_placa in c_placa or c_placa in a_placa):
                best_auth_id = a['id']
                break
                
    if not best_auth_id and c_cond:
        for a in auths:
            a_cond = (a['responsable'] or '').strip().upper()
            a_veh = (a['unidad_equipo'] or '').strip().upper()
            if a_cond and a_cond == c_cond:
                if 'EQUIPO MENOR' in c_veh and 'EQUIPO MENOR' in a_veh:
                    best_auth_id = a['id']
                    break
                elif not a['placas']:
                    best_auth_id = a['id']
                    break
                    
    if not best_auth_id and c_cond:
        matching_auths = [a['id'] for a in auths if (a['responsable'] or '').strip().upper() == c_cond]
        if len(matching_auths) == 1:
            best_auth_id = matching_auths[0]
            
    if best_auth_id:
        auth_map[best_auth_id]['cargas'].append(c)
    else:
        unmatched.append(c)

print(f"Total cargas: {len(cargas)}, matched: {len(cargas) - len(unmatched)}, unmatched: {len(unmatched)}")
for a_id, data in list(auth_map.items())[:8]:
    a = data['auth']
    cs = data['cargas']
    tot_m = sum(float(c['importe_total']) for c in cs)
    resp = a['responsable']
    unid = a['unidad_equipo']
    plc = a['placas'] or 'S/P'
    aut = float(a['importe_semanal'])
    print(f"  Auth {a['num_renglon']:2d} | {resp:25s} | {unid:15s} | {plc:8s} | Auth: ${aut:,.2f} | Cons: ${tot_m:,.2f} ({len(cs)} cargas)")

db.close()
