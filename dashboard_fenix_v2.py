# -*- coding: utf-8 -*-
"""
Dashboard Fenix 2.0 - Servidor independiente puerto 5000
Conectado a fenix_db PostgreSQL
"""
import sys, io, os, datetime
import psycopg2
from psycopg2.extras import DictCursor

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from flask import Flask, render_template, jsonify, request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TMPL_DIR = os.path.join(BASE_DIR, "servidor", "templates", "dashboard")
STAT_DIR = os.path.join(BASE_DIR, "servidor", "static")

app = Flask(__name__, template_folder=TMPL_DIR, static_folder=STAT_DIR)
app.config['TEMPLATES_AUTO_RELOAD'] = True

class DbProxy:
    def __init__(self, conn):
        self.conn = conn
    def execute(self, sql, params=()):
        cur = self.conn.cursor(cursor_factory=DictCursor)
        cur.execute(sql, params)
        return cur
    def close(self):
        self.conn.close()

def get_db():
    conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
    return DbProxy(conn)

# ─────────────────────────────────────────
#  API: GASOLINA - autorizaciones vs consumidos
# ─────────────────────────────────────────
@app.route('/api/gasolina/autorizaciones')
def api_gasolina_auth():
    db = get_db()
    sem = request.args.get('semana', '')
    if not sem: sem = datetime.date.today().isocalendar()[1]
    
    rows = db.execute("""
        SELECT a.referencia as vehiculo, a.litros_autorizados, 
               COALESCE((SELECT SUM(litros) FROM gasolina.consumos c WHERE (c.vehiculo = a.referencia OR c.placa = a.referencia) AND c.semana = ('Semana ' || a.semana::text) AND c.estatus_revision = 'APROBADO'), 0) as litros_consumidos
        FROM catalogos.autorizaciones a
        WHERE a.tipo = 'GASOLINA' AND a.semana = %s
        ORDER BY a.referencia
    """, (sem,)).fetchall()
    
    db.close()
    data = []
    for r in rows:
        auth = float(r['litros_autorizados'])
        cons = float(r['litros_consumidos'])
        data.append({
            'vehiculo': r['vehiculo'], 
            'autorizado': auth, 
            'consumido': cons, 
            'excedido': cons > auth and auth > 0
        })
    return jsonify({'success': True, 'data': data})

# ─────────────────────────────────────────
#  RUNNER
# ─────────────────────────────────────────
@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/dashboard/diesel')
def dashboard_diesel():
    return render_template('dashboard_diesel.html')

@app.route('/dashboard/gasolina')
def dashboard_gasolina():
    return render_template('dashboard_gasolina.html')

@app.route('/dashboard/acarreos')
def dashboard_acarreos():
    return render_template('dashboard_acarreos.html')

@app.route('/dashboard/mezcla')
def dashboard_mezcla():
    return render_template('dashboard_mezcla.html')

# ─────────────────────────────────────────
#  API: KPIs GENERALES (tarjetas superiores)
# ─────────────────────────────────────────
@app.route('/api/kpis')
def api_kpis():
    db = get_db()
    sem = request.args.get('semana', '')
    cond = "AND semana = %s" if sem else ""
    params = [sem] if sem else []

    def q(sql):
        res = db.execute(sql, params).fetchone()
        return res[0] if res and res[0] is not None else 0

    diesel_lts  = q(f"SELECT COALESCE(SUM(litros),0) FROM diesel.consumos WHERE estatus_revision = 'APROBADO' {cond}")
    diesel_imp  = q(f"SELECT COALESCE(SUM(importe_total),0) FROM diesel.consumos WHERE estatus_revision = 'APROBADO' {cond}")
    diesel_regs = q(f"SELECT COUNT(*) FROM diesel.consumos WHERE estatus_revision = 'APROBADO' {cond}")

    diesel_fac_lts = q(f"SELECT COALESCE(SUM(litros_facturados),0) FROM diesel.facturas WHERE estatus_revision = 'APROBADO' {cond}")
    diesel_fac_imp = q(f"SELECT COALESCE(SUM(importe_total),0) FROM diesel.facturas WHERE estatus_revision = 'APROBADO' {cond}")
    diesel_fac_cnt = q(f"SELECT COUNT(*) FROM diesel.facturas WHERE estatus_revision = 'APROBADO' {cond}")

    gas_lts  = q(f"SELECT COALESCE(SUM(litros),0) FROM gasolina.consumos WHERE estatus_revision = 'APROBADO' {cond}")
    gas_imp  = q(f"SELECT COALESCE(SUM(importe_total),0) FROM gasolina.consumos WHERE estatus_revision = 'APROBADO' {cond}")
    gas_regs = q(f"SELECT COUNT(*) FROM gasolina.consumos WHERE estatus_revision = 'APROBADO' {cond}")

    db.close()
    return jsonify({
        'success': True,
        'diesel':  {'litros': diesel_lts, 'importe': diesel_imp, 'registros': diesel_regs},
        'diesel_facturas': {'litros': diesel_fac_lts, 'importe': diesel_fac_imp, 'count': diesel_fac_cnt},
        'gasolina': {'litros': gas_lts, 'importe': gas_imp, 'registros': gas_regs},
        'acarreos': {'viajes': 0, 'importe': 0},
        'mezcla':   {'toneladas': 0, 'importe': 0},
    })

# ─────────────────────────────────────────
#  API: SEMANAS DISPONIBLES
# ─────────────────────────────────────────
@app.route('/api/semanas')
def api_semanas():
    db = get_db()
    sems = set()
    for table in ['diesel.consumos','diesel.facturas','gasolina.consumos','gasolina.facturas']:
        for row in db.execute(f"SELECT DISTINCT semana FROM {table} WHERE estatus_revision = 'APROBADO' AND semana IS NOT NULL"):
            val = str(row[0]).strip()
            if val.isdigit():
                val = f'Semana {val}'
            sems.add(val)
    db.close()
    # Sort: "Semana 24" -> 24 numerically
    sorted_sems = sorted(sems, key=lambda x: int(x.replace('Semana','').strip()) if x.replace('Semana','').strip().isdigit() else 0, reverse=True)
    return jsonify(sorted_sems)

# ─────────────────────────────────────────
#  API: DIESEL - tabla comparativa consumos vs facturas
# ─────────────────────────────────────────
@app.route('/api/diesel/comparativo')
def api_diesel_comparativo():
    db = get_db()
    obra  = request.args.get('obra', '')
    sem   = request.args.get('semana', '')

    cons_cond = ""
    fac_cond  = ""
    cons_params = []
    fac_params  = []

    if obra:
        cons_cond += " AND obra_destino = %s"
        fac_cond  += " AND punto_de_carga = %s"
        cons_params.append(obra)
        fac_params.append(obra)
    if sem:
        cons_cond += " AND semana = %s"
        fac_cond  += " AND semana = %s"
        cons_params.append(sem)
        fac_params.append(sem)

    cons_rows = db.execute(f"""
        SELECT semana, COUNT(*) regs, COALESCE(SUM(litros),0) lts, COALESCE(SUM(importe_total),0) imp
        FROM diesel.consumos WHERE estatus_revision = 'APROBADO' {cons_cond}
        GROUP BY semana ORDER BY semana
    """, cons_params).fetchall()

    fac_rows = db.execute(f"""
        SELECT semana, COALESCE(SUM(litros_facturados),0) lts, COALESCE(SUM(importe_total),0) imp
        FROM diesel.facturas WHERE estatus_revision = 'APROBADO' {fac_cond}
        GROUP BY semana ORDER BY semana
    """, fac_params).fetchall()

    obras_list = [r['nombre'] for r in db.execute('SELECT nombre FROM catalogos.obras ORDER BY nombre')]

    # Build per-semana map
    fac_map = {r['semana']: {'lts': r['lts'], 'imp': r['imp']} for r in fac_rows}

    table = []
    for r in cons_rows:
        s = str(r['semana'])
        f = fac_map.get(r['semana'], {'lts': 0, 'imp': 0})
        table.append({
            'semana': s,
            'cons_lts': round(float(r['lts']), 2),
            'cons_imp': round(float(r['imp']), 2),
            'fac_lts':  round(float(f['lts']), 2),
            'fac_imp':  round(float(f['imp']), 2),
            'registros': r['regs']
        })

    kpis = {
        'cons_lts': sum(x['cons_lts'] for x in table),
        'cons_imp': sum(x['cons_imp'] for x in table),
        'fac_lts':  sum(x['fac_lts']  for x in table),
        'fac_imp':  sum(x['fac_imp']  for x in table),
    }

    db.close()
    return jsonify({'success': True, 'table': table, 'kpis': kpis, 'obras': obras_list})

# ─────────────────────────────────────────
#  API: DIESEL - consumos por obra (para grafica)
# ─────────────────────────────────────────
@app.route('/api/diesel/por_obra')
def api_diesel_por_obra():
    db = get_db()
    sem = request.args.get('semana', '')
    cond = "AND semana = %s" if sem else ""
    params = [sem] if sem else []

    rows = db.execute(f"""
        SELECT obra_destino as obra, COALESCE(SUM(litros),0) lts
        FROM diesel.consumos WHERE estatus_revision = 'APROBADO' {cond}
        GROUP BY obra_destino ORDER BY lts DESC LIMIT 10
    """, params).fetchall()

    db.close()
    return jsonify({'success': True, 'data': [{'obra': r['obra'] or 'Sin Obra', 'litros': float(r['lts'])} for r in rows]})

# ─────────────────────────────────────────
#  API: DIESEL - autorizaciones vs consumidos
# ─────────────────────────────────────────
@app.route('/api/diesel/autorizaciones')
def api_diesel_auth():
    db = get_db()
    sem = request.args.get('semana', '')
    if not sem: sem = datetime.date.today().isocalendar()[1]
    
    rows = db.execute("""
        SELECT a.referencia as obra, a.litros_autorizados, 
               COALESCE((SELECT SUM(litros) FROM diesel.consumos c WHERE c.obra_destino = a.referencia AND c.semana = ('Semana ' || a.semana::text) AND c.estatus_revision = 'APROBADO'), 0) as litros_consumidos
        FROM catalogos.autorizaciones a
        WHERE a.tipo = 'DIESEL' AND a.semana = %s
        ORDER BY a.referencia
    """, (sem,)).fetchall()
    
    db.close()
    data = []
    for r in rows:
        auth = float(r['litros_autorizados'])
        cons = float(r['litros_consumidos'])
        data.append({
            'obra': r['obra'], 
            'autorizado': auth, 
            'consumido': cons, 
            'excedido': cons > auth and auth > 0
        })
    return jsonify({'success': True, 'data': data})

# ─────────────────────────────────────────
#  API: GASOLINA - tabla comparativa consumos vs facturas
# ─────────────────────────────────────────
@app.route('/api/gasolina/comparativo_gasolinera')
def api_gasolina_comparativo():
    db = get_db()
    sem = request.args.get('semana', '')
    cond = "AND semana = %s" if sem else ""
    params = [sem] if sem else []

    def normalize(s):
        if not s: return 'OTRO'
        s = s.upper()
        if 'LEVET' in s: return 'LEVET'
        if 'SI VALE' in s or 'SIVALE' in s: return 'SI VALE'
        if 'CASTILLA' in s or 'DERIVADOS' in s or 'MOBILE' in s or 'MOBIL' in s: return 'MOBILE'
        return s

    # Get consumos grouped by gasolinera (origen)
    cons_rows = db.execute(f"""
        SELECT UPPER(origen) as gasolinera, COUNT(*) regs, COALESCE(SUM(litros),0) lts, COALESCE(SUM(importe_total),0) imp
        FROM gasolina.consumos WHERE estatus_revision = 'APROBADO' AND origen IS NOT NULL AND origen != '' {cond}
        GROUP BY UPPER(origen) ORDER BY lts DESC
    """, params).fetchall()

    # Get facturas grouped by proveedor
    fac_rows = db.execute(f"""
        SELECT UPPER(proveedor) as gasolinera, COALESCE(SUM(litros_facturados),0) lts, COALESCE(SUM(importe_total),0) imp
        FROM gasolina.facturas WHERE estatus_revision = 'APROBADO' AND proveedor IS NOT NULL AND proveedor != '' {cond}
        GROUP BY UPPER(proveedor)
    """, params).fetchall()

    cons_map = {}
    for r in cons_rows:
        k = normalize(r['gasolinera'])
        if k not in cons_map: cons_map[k] = {'lts': 0, 'imp': 0, 'regs': 0}
        cons_map[k]['lts'] += r['lts']
        cons_map[k]['imp'] += r['imp']
        cons_map[k]['regs'] += r['regs']

    fac_map = {}
    for r in fac_rows:
        k = normalize(r['gasolinera'])
        if k not in fac_map: fac_map[k] = {'lts': 0, 'imp': 0}
        fac_map[k]['lts'] += r['lts']
        fac_map[k]['imp'] += r['imp']

    all_gas = set(list(cons_map.keys()) + list(fac_map.keys()))
    
    table = []
    for g in sorted(list(all_gas)):
        c = cons_map.get(g, {'lts': 0, 'imp': 0, 'regs': 0})
        f = fac_map.get(g, {'lts': 0, 'imp': 0})
        table.append({
            'gasolinera': g,
            'cons_lts': round(float(c['lts']), 2),
            'cons_imp': round(float(c['imp']), 2),
            'fac_lts':  round(float(f['lts']), 2),
            'fac_imp':  round(float(f['imp']), 2),
            'registros': c['regs']
        })

    kpis = {
        'cons_lts': sum(x['cons_lts'] for x in table),
        'cons_imp': sum(x['cons_imp'] for x in table),
        'fac_lts':  sum(x['fac_lts']  for x in table),
        'fac_imp':  sum(x['fac_imp']  for x in table),
    }

    db.close()
    return jsonify({'success': True, 'table': table, 'kpis': kpis})

# ─────────────────────────────────────────
#  API: GASOLINA - consumos vs autorizaciones por obra
# ─────────────────────────────────────────
@app.route('/api/gasolina/por_obra')
def api_gasolina_por_obra():
    db = get_db()
    sem = request.args.get('semana', '')
    cond = "AND semana = %s" if sem else ""
    params = [sem] if sem else []

    auth_rows = db.execute(f"""
        SELECT obra_destino as obra, COALESCE(SUM(importe_autorizado),0) auth_imp
        FROM gasolina.autorizaciones WHERE estatus_revision = 'APROBADO' AND obra_destino IS NOT NULL AND obra_destino != '' {cond}
        GROUP BY obra_destino
    """, params).fetchall()

    cons_rows = db.execute(f"""
        SELECT obra_destino as obra, COALESCE(SUM(importe_total),0) cons_imp
        FROM gasolina.consumos WHERE estatus_revision = 'APROBADO' AND obra_destino IS NOT NULL AND obra_destino != '' {cond}
        GROUP BY obra_destino
    """, params).fetchall()

    auth_map = {r['obra']: r['auth_imp'] for r in auth_rows}
    cons_map = {r['obra']: r['cons_imp'] for r in cons_rows}
    
    all_obras = set(list(auth_map.keys()) + list(cons_map.keys()))
    
    data = []
    for o in sorted(list(all_obras)):
        data.append({
            'obra': o,
            'auth_imp': round(float(auth_map.get(o, 0)), 2),
            'cons_imp': round(float(cons_map.get(o, 0)), 2)
        })
        
    data.sort(key=lambda x: x['auth_imp'], reverse=True)

    db.close()
    return jsonify({'success': True, 'data': data})

# ─────────────────────────────────────────
#  API: GASOLINA - estado de cuenta vs consumos (por placa)
# ─────────────────────────────────────────
@app.route('/api/gasolina/estado_cuenta_conciliacion')
def api_gasolina_estado_cuenta_conciliacion():
    db = get_db()
    sem = request.args.get('semana', '')
    cond = "AND semana = %s" if sem else ""
    params = [sem] if sem else []

    def clean_placa(p):
        if not p or str(p).strip().upper() in ['S/P', 'N/A', 'NONE']: return 'SIN PLACA'
        return str(p).strip().upper()

    ec_rows = db.execute(f"""
        SELECT placa, vehiculo, 
               COALESCE(importe_autorizado,0) as auth_imp, 
               COALESCE(consumo_real,0) as ec_imp
        FROM gasolina.estados_cuenta WHERE estatus_revision = 'APROBADO' {cond}
    """, params).fetchall()

    cons_rows = db.execute(f"""
        SELECT placa, vehiculo, 
               COALESCE(importe_total,0) as cons_imp, 
               COALESCE(litros,0) as cons_lts
        FROM gasolina.consumos WHERE estatus_revision = 'APROBADO' {cond}
    """, params).fetchall()

    ec_map = {}
    for r in ec_rows:
        p = clean_placa(r['placa'])
        if p not in ec_map: ec_map[p] = {'v': r['vehiculo'], 'auth': 0, 'ec_imp': 0}
        ec_map[p]['auth'] += r['auth_imp']
        ec_map[p]['ec_imp'] += r['ec_imp']
        if r['vehiculo'] and not ec_map[p]['v']: ec_map[p]['v'] = r['vehiculo']

    cons_map = {}
    for r in cons_rows:
        p = clean_placa(r['placa'])
        if p not in cons_map: cons_map[p] = {'v': r['vehiculo'], 'cons_imp': 0, 'cons_lts': 0}
        cons_map[p]['cons_imp'] += r['cons_imp']
        cons_map[p]['cons_lts'] += r['cons_lts']
        if r['vehiculo'] and not cons_map[p]['v']: cons_map[p]['v'] = r['vehiculo']

    all_placas = set(list(ec_map.keys()) + list(cons_map.keys()))
    
    table = []
    for p in sorted(list(all_placas)):
        if p == 'SIN PLACA': continue
        e = ec_map.get(p, {'v': '', 'auth': 0, 'ec_imp': 0})
        c = cons_map.get(p, {'v': '', 'cons_imp': 0, 'cons_lts': 0})
        veh = e['v'] if e['v'] else c['v']
        
        dif = round(float(e['ec_imp']) - float(c['cons_imp']), 2)
        if abs(dif) <= 1.0:
            estatus = 'CUADRADO'
        elif e['ec_imp'] > 0 and c['cons_imp'] == 0:
            estatus = 'FALTA REPORTE (SOLO EN EDO. CTA)'
        elif c['cons_imp'] > 0 and e['ec_imp'] == 0:
            estatus = 'FALTA EDO. CTA (SOLO EN REPORTE)'
        elif dif > 0:
            estatus = 'EDO. CTA EXCEDE REPORTE'
        else:
            estatus = 'REPORTE EXCEDE EDO. CTA'
            
        table.append({
            'placa': p,
            'vehiculo': veh or 'S/V',
            'auth_imp': round(float(e['auth']), 2),
            'ec_imp': round(float(e['ec_imp']), 2),
            'cons_imp': round(float(c['cons_imp']), 2),
            'cons_lts': round(float(c['cons_lts']), 2),
            'diferencia': dif,
            'estatus': estatus
        })
        
    kpis = {
        'total_ec_imp': sum(x['ec_imp'] for x in table),
        'total_cons_imp': sum(x['cons_imp'] for x in table),
        'total_dif': sum(x['diferencia'] for x in table),
        'cuadrados': sum(1 for x in table if x['estatus'] == 'CUADRADO'),
        'problemas': sum(1 for x in table if x['estatus'] != 'CUADRADO'),
    }

    db.close()
    return jsonify({'success': True, 'table': table, 'kpis': kpis})

# ─────────────────────────────────────────
#  API: GASOLINA - conciliacion por gasolinera
# ─────────────────────────────────────────
@app.route('/api/gasolina/conciliacion')
def api_gasolina_conciliacion():
    db = get_db()
    sem = request.args.get('semana', '')
    cond = "AND semana = %s" if sem else ""
    params = [sem] if sem else []

    def normalize(s):
        if not s: return 'OTRO'
        s = s.upper()
        if 'LEVET' in s: return 'LEVET'
        if 'SI VALE' in s or 'SIVALE' in s: return 'SI VALE'
        if 'CASTILLA' in s or 'DERIVADOS' in s or 'MOBILE' in s or 'MOBIL' in s: return 'MOBILE'
        return s

    cons_rows = db.execute(f"""
        SELECT origen, COUNT(*) regs, COALESCE(SUM(litros),0) lts, COALESCE(SUM(importe_total),0) imp
        FROM gasolina.consumos WHERE estatus_revision = 'APROBADO' AND origen IS NOT NULL {cond}
        GROUP BY origen
    """, params).fetchall()

    fac_rows = db.execute(f"""
        SELECT proveedor, COUNT(*) regs, COALESCE(SUM(litros_facturados),0) lts, COALESCE(SUM(importe_total),0) imp
        FROM gasolina.facturas WHERE estatus_revision = 'APROBADO' AND proveedor IS NOT NULL {cond}
        GROUP BY proveedor
    """, params).fetchall()

    # Aggregate by normalized key
    cons_map = {}
    for r in cons_rows:
        k = normalize(r['origen'])
        if k not in cons_map: cons_map[k] = {'regs':0,'lts':0.0,'imp':0.0}
        cons_map[k]['regs'] += r['regs']
        cons_map[k]['lts']  += float(r['lts'] or 0)
        cons_map[k]['imp']  += float(r['imp'] or 0)

    fac_map = {}
    for r in fac_rows:
        k = normalize(r['proveedor'])
        if k not in fac_map: fac_map[k] = {'regs':0,'lts':0.0,'imp':0.0}
        fac_map[k]['regs'] += r['regs']
        fac_map[k]['lts']  += float(r['lts'] or 0)
        fac_map[k]['imp']  += float(r['imp'] or 0)

    all_keys = sorted(set(list(cons_map.keys()) + list(fac_map.keys())))
    table = []
    for k in all_keys:
        c = cons_map.get(k, {'regs':0,'lts':0.0,'imp':0.0})
        f = fac_map.get(k, {'regs':0,'lts':0.0,'imp':0.0})
        dif_imp = round(c['imp'] - f['imp'], 2)
        dif_lts = round(c['lts'] - f['lts'], 3)
        if abs(dif_imp) <= 1.0: estatus = 'CUADRADO'
        elif dif_imp > 0: estatus = 'FALTA FACTURA'
        else: estatus = 'FACTURA EXCEDE'
        table.append({
            'gasolinera': k,
            'rep_regs': c['regs'], 'rep_lts': round(c['lts'],3), 'rep_imp': round(c['imp'],2),
            'fac_regs': f['regs'], 'fac_lts': round(f['lts'],3), 'fac_imp': round(f['imp'],2),
            'dif_lts': dif_lts, 'dif_imp': dif_imp, 'estatus': estatus
        })

    kpis = {
        'total_rep': sum(x['rep_imp'] for x in table),
        'total_fac': sum(x['fac_imp'] for x in table),
        'total_dif': round(sum(x['rep_imp'] for x in table) - sum(x['fac_imp'] for x in table), 2),
        'cuadrados': sum(1 for x in table if x['estatus']=='CUADRADO'),
        'con_problema': sum(1 for x in table if x['estatus']!='CUADRADO'),
    }
    db.close()
    return jsonify({'success': True, 'table': table, 'kpis': kpis})

# ─────────────────────────────────────────
#  API: DIESEL - conciliacion por proveedor
# ─────────────────────────────────────────
@app.route('/api/diesel/conciliacion')
def api_diesel_conciliacion():
    db = get_db()
    sem = request.args.get('semana', '')
    cond = "AND semana = %s" if sem else ""
    params = [sem] if sem else []

    def norm_diesel(s):
        if not s: return 'OTRO'
        s = s.upper()
        if 'CASTILLA' in s or 'DERIVADOS' in s: return 'CASTILLA'
        if 'PEGASO' in s or 'TANQUE' in s: return 'TANQUE PEGASO'
        if 'MARIMBA' in s: return 'MARIMBA'
        if 'BIDON' in s or 'BIDÓN' in s: return 'BIDONES'
        return s

    cons_rows = db.execute(f"""
        SELECT origen, COUNT(*) regs, COALESCE(SUM(litros),0) lts, COALESCE(SUM(importe_total),0) imp
        FROM diesel.consumos WHERE estatus_revision = 'APROBADO' AND origen IS NOT NULL {cond}
        GROUP BY origen
    """, params).fetchall()

    fac_rows = db.execute(f"""
        SELECT proveedor, COUNT(*) regs, COALESCE(SUM(litros_facturados),0) lts, COALESCE(SUM(importe_total),0) imp
        FROM diesel.facturas WHERE estatus_revision = 'APROBADO' AND proveedor IS NOT NULL {cond}
        GROUP BY proveedor
    """, params).fetchall()

    cons_map = {}
    for r in cons_rows:
        k = norm_diesel(r['origen'])
        if k not in cons_map: cons_map[k] = {'regs':0,'lts':0.0,'imp':0.0}
        cons_map[k]['regs'] += r['regs']
        cons_map[k]['lts']  += float(r['lts'] or 0)
        cons_map[k]['imp']  += float(r['imp'] or 0)

    fac_map = {}
    for r in fac_rows:
        k = norm_diesel(r['proveedor'])
        if k not in fac_map: fac_map[k] = {'regs':0,'lts':0.0,'imp':0.0}
        fac_map[k]['regs'] += r['regs']
        fac_map[k]['lts']  += float(r['lts'] or 0)
        fac_map[k]['imp']  += float(r['imp'] or 0)

    all_keys = sorted(set(list(cons_map.keys()) + list(fac_map.keys())))
    table = []
    for k in all_keys:
        c = cons_map.get(k, {'regs':0,'lts':0.0,'imp':0.0})
        f = fac_map.get(k, {'regs':0,'lts':0.0,'imp':0.0})
        dif_imp = round(c['imp'] - f['imp'], 2)
        dif_lts = round(c['lts'] - f['lts'], 3)
        if abs(dif_imp) <= 1.0: estatus = 'CUADRADO'
        elif dif_imp > 0: estatus = 'FALTA FACTURA'
        else: estatus = 'FACTURA EXCEDE'
        table.append({
            'proveedor': k,
            'rep_regs': c['regs'], 'rep_lts': round(c['lts'],3), 'rep_imp': round(c['imp'],2),
            'fac_regs': f['regs'], 'fac_lts': round(f['lts'],3), 'fac_imp': round(f['imp'],2),
            'dif_lts': dif_lts, 'dif_imp': dif_imp, 'estatus': estatus
        })

    kpis = {
        'total_rep': sum(x['rep_imp'] for x in table),
        'total_fac': sum(x['fac_imp'] for x in table),
        'total_dif': round(sum(x['rep_imp'] for x in table) - sum(x['fac_imp'] for x in table), 2),
        'cuadrados': sum(1 for x in table if x['estatus']=='CUADRADO'),
        'con_problema': sum(1 for x in table if x['estatus']!='CUADRADO'),
    }
    db.close()
    return jsonify({'success': True, 'table': table, 'kpis': kpis})

# ─────────────────────────────────────────
#  API: DIESEL - conciliacion por obra
# ─────────────────────────────────────────
@app.route('/api/diesel/conciliacion_obra')
def api_diesel_conciliacion_obra():
    db = get_db()
    sem = request.args.get('semana', '')
    cond = "AND semana = %s" if sem else ""
    params = [sem] if sem else []

    OBRAS_MAP = [
        (['HUIXQUILUCAN', 'P.A.H'], 'Planta Huixquilucan'),
        (['PLANTA DE ASFALTO', 'PLANTA ASFALTO', 'PAP'], 'Planta Asfalto Pegaso'),
        (['MAQUINARIA PEGASO', 'MAQUINARIA PEG', 'MP'], 'Maquinaria Pegaso'),
        (['TANQUE PEGASO', 'TANQUE', 'TP', 'PLANTA PEGASO', 'PEGASO', 'OBRA: PLANTA'], 'Tanque Pegaso'),
        (['DESASOLVE', 'DEZAZOLVE', 'VICENTE LOMBARDO', 'LOMBARDO'], 'Vicente Lombardo'),
        (['ALFREDO DEL MAZO', 'ALFREDO MAZO'], 'Alfredo del Mazo'),
        (['BACHEO TOLUCA', 'BACHEO'], 'Bacheo Toluca'),
        (['MEXICO TOLUCA', 'MEX-TOL', 'MEXICO-TOLUCA', 'MEXICO - TOLUCA', 'MÉXICO-TOLUCA', 'MÉXICO- TOLUCA', 'MÉXICO - TOLUCA', 'LA PROVIDENCIA', 'PROVIDENCIA', 'PETROLIZADORA'], 'Mexico-Toluca'),
        (['LERMA TENANGO', 'LERMA-TENANGO', 'LERMA - TENANGO', 'LERMA', 'OBRA: LERMA'], 'Lerma - Tenango'),
        (['COLEGIO MILITAR', 'COLMIL'], 'Colegio Militar'),
        (['DRAGONES', 'DRAG'], 'Dragones'),
        (['FLOTILLA', 'TRANSPORTES FLOTILLA', 'OBRA: TRANSPORTES', 'TRANSPORTES'], 'Transportes Flotilla'),
    ]

    def mapear(txt):
        if not txt: return 'Sin clasificar'
        t = txt.upper()
        for kws, obra in OBRAS_MAP:
            for kw in kws:
                if kw in t: return obra
        return 'Sin clasificar'

    cons_rows = db.execute(f"SELECT obra_destino, COUNT(*) regs, COALESCE(SUM(litros),0) lts, COALESCE(SUM(importe_total),0) imp FROM diesel.consumos WHERE estatus_revision = 'APROBADO' {cond} GROUP BY obra_destino", params).fetchall()
    fac_rows = db.execute(f"SELECT punto_de_carga, COUNT(*) regs, COALESCE(SUM(litros_facturados),0) lts, COALESCE(SUM(importe_total),0) imp FROM diesel.facturas WHERE estatus_revision = 'APROBADO' {cond} GROUP BY punto_de_carga", params).fetchall()

    cons_map = {}
    for r in cons_rows:
        k = mapear(r['obra_destino'])
        if k not in cons_map: cons_map[k] = {'regs':0,'lts':0.0,'imp':0.0}
        cons_map[k]['regs'] += r['regs']; cons_map[k]['lts'] += float(r['lts']); cons_map[k]['imp'] += float(r['imp'])

    fac_map = {}
    for r in fac_rows:
        k = mapear(r['punto_de_carga'])
        if k not in fac_map: fac_map[k] = {'regs':0,'lts':0.0,'imp':0.0}
        fac_map[k]['regs'] += r['regs']; fac_map[k]['lts'] += float(r['lts']); fac_map[k]['imp'] += float(r['imp'])

    all_keys = sorted(set(list(cons_map.keys()) + list(fac_map.keys())))
    table = []
    for k in all_keys:
        c = cons_map.get(k, {'regs':0,'lts':0.0,'imp':0.0})
        f = fac_map.get(k, {'regs':0,'lts':0.0,'imp':0.0})
        dif_lts = round(f['lts'] - c['lts'], 2)
        if f['lts'] == 0: estatus = 'SIN FACTURA'
        elif c['lts'] == 0: estatus = 'SIN CONSUMO'
        elif abs(dif_lts) < 50: estatus = 'OK'
        elif dif_lts > 0: estatus = 'FAC > CONS'
        else: estatus = 'CONS > FAC'
        
        table.append({
            'obra': k, 'cons_lts': round(c['lts'],1), 'fac_lts': round(f['lts'],1), 'dif_lts': dif_lts, 'estatus': estatus
        })

    kpis = {
        'total_cons': sum(x['cons_lts'] for x in table),
        'total_fac': sum(x['fac_lts'] for x in table),
        'total_dif': sum(x['dif_lts'] for x in table)
    }
    db.close()
    return jsonify({'success': True, 'table': table, 'kpis': kpis})


if __name__ == '__main__':
    print("=" * 50)
    print("  DASHBOARD FENIX 2.0")
    print("  http://127.0.0.1:5000")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=False)

