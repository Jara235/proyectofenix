import sys
import re

with open(r'c:\Users\JOSE\Desktop\Proyecto fenix\app_admin.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_api = """@app.route('/api/admin/resumen/responsables')
def api_resumen_responsables():
    \"\"\"Returns totals grouped by Responsable (autorizado vs consumido).\"\"\"
    db = get_db()
    modulo  = request.args.get('modulo', 'diesel')
    semana  = request.args.get('semana', 'TODOS')

    if modulo != 'diesel':
        db.close()
        return jsonify([])

    semana_num = None
    cond_con = "WHERE estatus_revision = 'APROBADO' AND obra_destino NOT ILIKE %s"
    params_con = ['%Tanque Pegaso%']

    if semana != 'TODOS':
        semana_limpia = str(semana).replace('Semana ', '').strip()
        cond_con += " AND semana = %s"
        params_con.append(semana_limpia)
        try:
            semana_num = int(semana_limpia)
        except:
            pass

    try:
        auth_map = {}
        if semana_num:
            auth_rows = db.execute(
                "SELECT referencia, litros_autorizados FROM catalogos.autorizaciones WHERE tipo='DIESEL' AND semana=%s",
                (semana_num,)
            ).fetchall()
            for ar in auth_rows:
                auth_map[ar['referencia']] = float(ar['litros_autorizados'] or 0)

        q_obras = f'''
            SELECT 
                COALESCE(NULLIF(NULLIF(responsable, 'nan'), ''), 'S/R') as resp,
                STRING_AGG(DISTINCT obra_destino, ', ') as obras,
                SUM(litros) as consumido
            FROM diesel.consumos
            {cond_con}
            GROUP BY COALESCE(NULLIF(NULLIF(responsable, 'nan'), ''), 'S/R')
            ORDER BY resp
        '''
        rows = db.execute(q_obras, tuple(params_con)).fetchall()
        db.close()
        
        result = []
        for r in rows:
            resp = r['resp']
            auto = 0
            if resp != 'S/R':
                for rep_indiv in resp.split(','):
                    auto += auth_map.get(rep_indiv.strip(), 0)
            
            result.append({
                'responsable': resp,
                'obras': r['obras'],
                'autorizado': auto,
                'consumido': float(r['consumido'] or 0)
            })
            
        return jsonify(result)
    except Exception as e:
        print("ERROR API RESPONSABLES:", e)
        db.close()
        return jsonify([])

@app.route('/api/admin/resumen/maquinaria')
def api_resumen_maquinaria():
    \"\"\"Returns totals grouped by Obra and Maquinaria (equipo).\"\"\"
    db = get_db()
    modulo  = request.args.get('modulo', 'diesel')
    semana  = request.args.get('semana', 'TODOS')

    if modulo != 'diesel':
        db.close()
        return jsonify([])

    cond_con = "WHERE estatus_revision = 'APROBADO' AND obra_destino NOT ILIKE %s"
    params_con = ['%Tanque Pegaso%']

    if semana != 'TODOS':
        semana_limpia = str(semana).replace('Semana ', '').strip()
        cond_con += " AND semana = %s"
        params_con.append(semana_limpia)

    try:
        q = f'''
            SELECT 
                obra_destino as obra,
                COALESCE(NULLIF(NULLIF(equipo, 'nan'), ''), 'S/E') as maquinaria,
                SUM(litros) as consumido
            FROM diesel.consumos
            {cond_con}
            GROUP BY obra_destino, COALESCE(NULLIF(NULLIF(equipo, 'nan'), ''), 'S/E')
            ORDER BY obra_destino, maquinaria
        '''
        rows = db.execute(q, tuple(params_con)).fetchall()
        db.close()
        
        result = []
        for r in rows:
            result.append({
                'obra': r['obra'],
                'maquinaria': r['maquinaria'],
                'autorizado': 0, # Siempre 0 por ahora
                'consumido': float(r['consumido'] or 0)
            })
            
        return jsonify(result)
    except Exception as e:
        print("ERROR API MAQUINARIA:", e)
        db.close()
        return jsonify([])

"""

start_marker = "@app.route('/api/admin/resumen/responsables')"
end_marker = "@app.route('/admin/jalisco')"

parts = content.split(start_marker)
before = parts[0]
after = end_marker + parts[1].split(end_marker, 1)[1]

content = before + new_api + after

with open(r'c:\Users\JOSE\Desktop\Proyecto fenix\app_admin.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Replaced API endpoints.")
