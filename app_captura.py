import os, datetime, re, json
import psycopg2
from psycopg2.extras import DictCursor
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
try:
    import pdfplumber
except ImportError:
    pdfplumber = None

from bitacora_pdf_service import parse_bitacora_pdf, validar_duplicados_semana
from flask import Flask, render_template, request, jsonify, redirect, url_for

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TMPL_DIR = os.path.join(BASE_DIR, 'servidor', 'templates', 'captura_v2')
STAT_DIR = os.path.join(BASE_DIR, 'servidor', 'static', 'captura_v2')

app = Flask(__name__, template_folder=TMPL_DIR, static_folder=STAT_DIR, static_url_path='/static')

def get_db():
    conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
    return conn

def get_current_week():
    return datetime.datetime.now().isocalendar()[1]

def normalizar_obra_nombre(nombre):
    if not nombre:
        return ''
    n = str(nombre).strip().upper()
    if 'COSUM' in n:
        return 'SINDICATO COSUM'
    if 'MEXICO' in n and 'TOLUCA' in n:
        return 'OBRA MÉXICO TOLUCA'
    if 'ALFREDO' in n and 'MAZO' in n:
        return 'ALFREDO DEL MAZO'
    if 'LERMA' in n or 'MARIAS' in n or 'MARÍAS' in n:
        return 'LERMA - TRES MARÍAS'
    if 'HUIXQUILUCAN' in n:
        return 'P. ASFALTO HUIXQUILUCAN'
    if 'PEGASO' in n and 'PLANTA' in n:
        return 'PLANTA PEGASO'
    if 'PEGASO' in n and 'TANQUE' in n:
        return 'TANQUE PEGASO'
    if 'BACHEO' in n:
        return 'BACHEO TOLUCA'
    if 'PROVIDENCIA' in n:
        return 'PROVIDENCIA'
    if 'DESASOLVE' in n or 'DESAZOLVE' in n:
        return 'DESASOLVE'
    return str(nombre).strip().upper()

def generate_folio(module_prefix):
    return f"{module_prefix}-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

@app.route('/')
def index():
    return redirect(url_for('view_dashboard'))

@app.route('/dashboard')
def view_dashboard():
    db = get_db()
    cur = db.cursor(cursor_factory=DictCursor)
    cur.execute('SELECT nombre FROM catalogos.obras ORDER BY nombre')
    obras = cur.fetchall()
    cur.execute('SELECT tipo_operacion FROM catalogos.operaciones ORDER BY id')
    operaciones = cur.fetchall()
    db.close()
    return render_template('dashboard.html', obras=obras, operaciones=operaciones)

@app.route('/diesel')
def view_diesel():
    db = get_db()
    cur = db.cursor(cursor_factory=DictCursor)
    cur.execute('SELECT nombre FROM catalogos.obras ORDER BY nombre')
    obras = cur.fetchall()
    cur.execute("SELECT numero_economico, descripcion FROM catalogos.equipos WHERE tipo_equipo = 'DIESEL' OR tipo_equipo IS NULL ORDER BY numero_economico")
    equipos = cur.fetchall()
    cur.execute("""
        SELECT DISTINCT nombre FROM (
            SELECT nombre FROM catalogos.operadores WHERE nombre IS NOT NULL AND nombre != ''
            UNION
            SELECT DISTINCT operador AS nombre FROM diesel.consumos WHERE operador IS NOT NULL AND operador NOT IN ('Sin Registro', 'S/R', 'nan', '')
            UNION
            SELECT DISTINCT responsable_maquinaria AS nombre FROM diesel.consumos WHERE responsable_maquinaria IS NOT NULL AND responsable_maquinaria NOT IN ('Sin Registro', 'S/R', 'nan', '')
        ) t ORDER BY nombre
    """)
    operadores = cur.fetchall()
    cur.execute('SELECT tipo_operacion, codigo_operacion FROM catalogos.operaciones ORDER BY id')
    operaciones = cur.fetchall()
    
    origenes = ['Marimba M-01', 'Tanque Pegaso', 'Bidones', 'Gasolineria Mobil', 'Gasolineria Levet', 'No aplica']
    
    # Get history
    cur.execute("""
        SELECT folio_conciliacion, fecha, semana, obra_destino, equipo_economico, equipo, litros, 
               responsable, operador, responsable_maquinaria, horometro_inicial, tipo_captura 
        FROM diesel.consumos 
        WHERE origen != 'FACTURA' 
        ORDER BY id DESC LIMIT 10
    """)
    historial_consumos = cur.fetchall()
    cur.execute("SELECT observaciones, fecha as fecha_factura, litros as litros_facturados, importe_total FROM diesel.consumos WHERE origen='FACTURA' ORDER BY id DESC LIMIT 5")
    historial_facturas_raw = cur.fetchall()
    historial_facturas = []
    for h in historial_facturas_raw:
        obs = h['observaciones'] or ''
        uuid = obs.split('|')[0].replace('UUID:', '').strip() if 'UUID:' in obs else obs
        historial_facturas.append({
            'folio_fiscal': uuid,
            'fecha_factura': h['fecha_factura'],
            'litros_facturados': h['litros_facturados'],
            'importe_total': h['importe_total']
        })
    
    cur.execute("""
        SELECT DISTINCT nombre FROM (
            SELECT referencia AS nombre FROM catalogos.autorizaciones
                WHERE tipo = 'DIESEL' AND referencia IS NOT NULL AND referencia NOT IN ('S/R','nan','')
            UNION
            SELECT DISTINCT responsable AS nombre FROM diesel.consumos
                WHERE responsable IS NOT NULL AND responsable NOT IN ('S/R','nan','')
            UNION
            SELECT nombre FROM catalogos.operadores WHERE nombre IS NOT NULL AND nombre != ''
        ) t
        ORDER BY nombre
    """)
    responsables = cur.fetchall()

    # Mapeo Equipo -> Obra
    cur.execute("SELECT equipo_eco, obra_nombre FROM catalogos.equipo_obra_mapping")
    mapping_rows = cur.fetchall()
    obra_equipos_map = {}
    for r in mapping_rows:
        ob = r['obra_nombre']
        eq = r['equipo_eco']
        if ob and eq:
            obra_equipos_map.setdefault(ob, []).append(eq)

    # Catálogos de Transportes (Tanque Pegaso)
    cur.execute("SELECT numero_economico, descripcion, tipo_equipo, responsable_default FROM transportes.equipos WHERE activo = TRUE ORDER BY numero_economico")
    transportes_equipos = [dict(r) for r in cur.fetchall()]
    
    cur.execute("SELECT nombre, puesto FROM transportes.operadores WHERE activo = TRUE ORDER BY nombre")
    transportes_operadores = [dict(r) for r in cur.fetchall()]
    
    # Mapeo Responsable -> Equipo Default en Transportes
    transportes_resp_to_equipo = {}
    for eq in transportes_equipos:
        if eq.get('responsable_default'):
            resp_clean = str(eq['responsable_default']).strip().upper()
            transportes_resp_to_equipo[resp_clean] = eq['numero_economico']

    # Historial reciente de transportes
    cur.execute("""
        SELECT folio_conciliacion, fecha, semana, obra_destino, equipo_economico, equipo, litros, 
               responsable_unidad as responsable, responsable_unidad as operador, horometro as horometro_inicial, 'TRANSPORTES' as tipo_captura
        FROM transportes.consumos_diesel
        ORDER BY id DESC LIMIT 10
    """)
    historial_transportes = [dict(r) for r in cur.fetchall()]

    db.close()
    context = {
        'obras': obras,
        'equipos': equipos,
        'operadores': operadores,
        'responsables': responsables,
        'transportes_equipos': transportes_equipos,
        'transportes_operadores': transportes_operadores,
        'transportes_resp_to_equipo': transportes_resp_to_equipo,
        'historial_transportes': historial_transportes,
        'operaciones': operaciones,
        'origenes': origenes,
        'obra_equipos_map': obra_equipos_map,
        'historial_consumos': historial_consumos,
        'historial_facturas': historial_facturas,
        'current_date': datetime.datetime.now().strftime('%Y-%m-%d'),
        'current_week': get_current_week()
    }
    return render_template('captura_diesel.html', **context)

def sync_gasolina_autorizaciones_arrastre(db, semana_num):
    """Garantiza la continuidad/arrastre semanal de las autorizaciones de gasolina."""
    cur = db.cursor()
    cur.execute("SELECT COUNT(*) FROM gasolina.autorizaciones_semanal WHERE semana = %s", (semana_num,))
    cnt = cur.fetchone()[0]
    if cnt == 0:
        cur.execute("SELECT MAX(semana) FROM gasolina.autorizaciones_semanal WHERE semana < %s", (semana_num,))
        max_sem_prev_row = cur.fetchone()
        max_sem_prev = max_sem_prev_row[0] if max_sem_prev_row else None
        
        if max_sem_prev:
            cur.execute("""
                INSERT INTO gasolina.autorizaciones_semanal 
                    (semana, maestro_id, empresa, num_renglon, responsable, centro_trabajo, unidad_equipo, placas, importe_semanal)
                SELECT %s, maestro_id, empresa, num_renglon, responsable, centro_trabajo, unidad_equipo, placas, importe_semanal
                FROM gasolina.autorizaciones_semanal WHERE semana = %s
                ON CONFLICT (semana, maestro_id) DO NOTHING;
            """, (semana_num, max_sem_prev))
        else:
            cur.execute("""
                INSERT INTO gasolina.autorizaciones_semanal 
                    (semana, maestro_id, empresa, num_renglon, responsable, centro_trabajo, unidad_equipo, placas, importe_semanal)
                SELECT %s, id, empresa, num_renglon, responsable, centro_trabajo, unidad_equipo, placas, importe_semanal
                FROM gasolina.autorizaciones_maestro WHERE activo = TRUE
                ON CONFLICT (semana, maestro_id) DO NOTHING;
            """, (semana_num,))
        db.commit()

@app.route('/gasolina')
def view_gasolina():
    db = get_db()
    cur = db.cursor(cursor_factory=DictCursor)
    cur.execute("""
        SELECT nombre FROM catalogos.obras WHERE nombre IS NOT NULL AND nombre != '' ORDER BY nombre
    """)
    obras = cur.fetchall()
    
    cur.execute("""
        SELECT id, empresa, num_renglon, responsable, centro_trabajo, unidad_equipo, placas, importe_semanal
        FROM gasolina.autorizaciones_maestro
        WHERE activo = TRUE
        ORDER BY CASE WHEN empresa='J.D.J.' THEN 1 ELSE 2 END, num_renglon ASC
    """)
    rows = cur.fetchall()

    placas_list = []
    placas_map = {}
    equipos_sin_placa = []
    seen_placas = set()

    for r in rows:
        p = str(r['placas'] or 'S/P').strip().upper()
        veh = str(r['unidad_equipo'] or '').strip()
        obra = str(r['centro_trabajo'] or '').strip()
        resp = str(r['responsable'] or '').strip()
        monto = float(r['importe_semanal'] or 0)

        item = {
            'id': r['id'],
            'empresa': r['empresa'],
            'placa': p,
            'vehiculo': veh,
            'obra': obra,
            'responsable': resp,
            'importe_semanal': monto
        }

        if p == 'S/P' or 'SIN PLACA' in p:
            equipos_sin_placa.append(item)
        else:
            if p not in seen_placas:
                seen_placas.add(p)
                placas_list.append({'id': r['id'], 'placa': p, 'vehiculo': veh, 'obra': obra, 'responsable': resp})
            placas_map[p] = item

    cur.execute("SELECT numero_economico, descripcion FROM catalogos.equipos WHERE tipo_equipo = 'GASOLINA' ORDER BY numero_economico")
    vehiculos = cur.fetchall()
    cur.execute('SELECT folio_conciliacion, fecha, obra_destino, vehiculo, litros FROM gasolina.consumos ORDER BY id DESC LIMIT 5')
    historial_consumos = cur.fetchall()
    try:
        cur.execute('SELECT uuid_cfdi, fecha_factura, litros_facturados, importe_total FROM gasolina.facturas ORDER BY id DESC LIMIT 5')
        historial_facturas_raw = cur.fetchall()
        historial_facturas = [dict(r) for r in historial_facturas_raw]
    except Exception:
        historial_facturas = []

    # Catálogos Transportes Gasolina
    cur.execute("SELECT numero_economico, descripcion, tipo_equipo, placas, responsable_default FROM transportes.equipos WHERE activo = TRUE ORDER BY numero_economico")
    transportes_gasolina_equipos = [dict(r) for r in cur.fetchall()]
    cur.execute("SELECT nombre, puesto FROM transportes.operadores WHERE activo = TRUE ORDER BY nombre")
    transportes_gasolina_operadores = [dict(r) for r in cur.fetchall()]

    cur.execute("""
        SELECT folio_conciliacion, fecha, semana, gasolineria as origen, obra_destino, vehiculo, placa, litros, responsable_unidad as conductor
        FROM transportes.consumos_gasolina
        ORDER BY id DESC LIMIT 5
    """)
    historial_transportes_gasolina = [dict(r) for r in cur.fetchall()]

    db.close()
    
    import json
    context = {
        'obras': obras,
        'placas': placas_list,
        'placas_map_json': json.dumps(placas_map),
        'equipos_sin_placa_json': json.dumps(equipos_sin_placa),
        'vehiculos': vehiculos,
        'transportes_equipos': transportes_gasolina_equipos,
        'transportes_operadores': transportes_gasolina_operadores,
        'historial_consumos': historial_consumos,
        'historial_transportes_gasolina': historial_transportes_gasolina,
        'historial_facturas': historial_facturas,
        'current_date': datetime.datetime.now().strftime('%Y-%m-%d'),
        'current_week': get_current_week()
    }
    return render_template('captura_gasolina.html', **context)

@app.route('/api/gasolina/unidad_info')
def api_gasolina_unidad_info():
    placa = request.args.get('placa', '').strip()
    if not placa:
        return jsonify({'success': False, 'error': 'Placa no especificada'})
    try:
        db = get_db()
        cur = db.cursor(cursor_factory=DictCursor)
        
        # 1. Search in master authorizations (gasolina.autorizaciones_maestro)
        cur.execute("""
            SELECT id, empresa, responsable, centro_trabajo as obra_destino, unidad_equipo as vehiculo
            FROM gasolina.autorizaciones_maestro 
            WHERE UPPER(TRIM(placas)) = UPPER(%s) AND activo = TRUE
            ORDER BY id DESC LIMIT 1
        """, (placa,))
        m_row = cur.fetchone()
        
        vehiculo = m_row['vehiculo'] if m_row and m_row['vehiculo'] else ''
        obra = m_row['obra_destino'] if m_row and m_row['obra_destino'] else ''
        responsable = m_row['responsable'] if m_row and m_row['responsable'] else ''
        maestro_id = m_row['id'] if m_row else None
        empresa = m_row['empresa'] if m_row else ''

        # 2. Fallback to consumos
        if not obra or not responsable or not vehiculo:
            cur.execute("""
                SELECT vehiculo, obra_destino, conductor FROM gasolina.consumos 
                WHERE UPPER(TRIM(placa)) = UPPER(%s) AND (obra_destino IS NOT NULL OR conductor IS NOT NULL)
                ORDER BY id DESC LIMIT 1
            """, (placa,))
            c_row = cur.fetchone()
            if c_row:
                if not vehiculo and c_row['vehiculo']: vehiculo = c_row['vehiculo']
                if not obra and c_row['obra_destino']: obra = c_row['obra_destino']
                if not responsable and c_row['conductor']: responsable = c_row['conductor']

        # 3. Fallback to catalogos.equipos
        if not vehiculo or not responsable:
            cur.execute("""
                SELECT descripcion, operador_default FROM catalogos.equipos 
                WHERE UPPER(TRIM(numero_economico)) = UPPER(%s)
            """, (placa,))
            eq_row = cur.fetchone()
            if eq_row:
                if not vehiculo and eq_row['descripcion']: vehiculo = eq_row['descripcion']
                if not responsable and eq_row['operador_default']: responsable = eq_row['operador_default']

        db.close()
        return jsonify({
            'success': True,
            'placa': placa,
            'maestro_id': maestro_id,
            'empresa': empresa,
            'vehiculo': vehiculo,
            'obra': obra,
            'responsable': responsable
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/jalisco')
def view_jalisco():
    db = get_db()
    cur = db.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT numero_economico, descripcion FROM catalogos.equipos WHERE tipo_equipo = 'DIESEL' OR tipo_equipo IS NULL ORDER BY numero_economico")
    equipos = cur.fetchall()
    db.close()
    return render_template('captura_jalisco.html', equipos=equipos)

@app.route('/api/jalisco/guardar_movimiento', methods=['POST'])
def api_jalisco_guardar_movimiento():
    try:
        tipo = request.form.get('tipo_movimiento')
        litros = float(request.form.get('litros', 0))
        obs = request.form.get('observaciones', '')
        
        import datetime
        fecha_req = request.form.get('fecha')
        if fecha_req and fecha_req.strip():
            fecha = fecha_req.strip()
            try:
                dt_obj = datetime.datetime.strptime(fecha, '%Y-%m-%d')
                semana = dt_obj.isocalendar()[1]
            except:
                semana = get_current_week()
        else:
            fecha = datetime.date.today().strftime('%Y-%m-%d')
            semana = get_current_week()
        
        db = get_db()
        cur = db.cursor(cursor_factory=DictCursor)

        cur.execute("SELECT saldo_teorico FROM diesel.jalisco_movimientos ORDER BY id DESC LIMIT 1")
        last = cur.fetchone()
        saldo_actual = float(last['saldo_teorico']) if last else 0.0

        if tipo == 'ENTRADA':
            costo = float(request.form.get('costo_por_litro', 0))
            importe = float(request.form.get('importe_total', 0))
            saldo_nuevo = saldo_actual + litros
            pdf = request.files.get('archivo_pdf')
            pdf_blob = pdf.read() if pdf and pdf.filename else None

            cur.execute("""
                INSERT INTO diesel.jalisco_movimientos
                (fecha, semana, tipo_movimiento, litros, costo_por_litro, importe_total, saldo_teorico, observaciones, archivo_pdf)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (fecha, semana, tipo, litros, costo, importe, saldo_nuevo, obs, pdf_blob))

        elif tipo == 'SALIDA':
            eq_eco = request.form.get('equipo_economico', '')
            eq_desc = request.form.get('equipo', '')
            saldo_nuevo = saldo_actual - litros
            foto = request.files.get('foto_evidencia')
            foto_blob = foto.read() if foto and foto.filename else None
            
            is_gasolina = 'GASOLINA' in (str(eq_eco) + ' ' + str(eq_desc) + ' ' + str(obs)).upper()
            costo = 23.97 if is_gasolina else 27.00
            importe = litros * costo

            cur.execute("""
                INSERT INTO diesel.jalisco_movimientos
                (fecha, semana, tipo_movimiento, equipo_economico, equipo, litros, costo_por_litro, importe_total, saldo_teorico, observaciones, foto_evidencia)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (fecha, semana, tipo, eq_eco, eq_desc, litros, costo, importe, saldo_nuevo, obs, foto_blob))

        db.commit()
        cur.close()
        db.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/jalisco/procesar_documento_masivo', methods=['POST'])
def api_jalisco_procesar_documento_masivo():
    try:
        if 'archivo' not in request.files:
            return jsonify({'success': False, 'error': 'No se recibió ningún archivo.'})
        
        file = request.files['archivo']
        if not file or file.filename == '':
            return jsonify({'success': False, 'error': 'Archivo no válido.'})
        
        temp_dir = os.path.join(os.path.dirname(__file__), 'servidor', 'static', 'jalisco_temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        filename = os.path.basename(file.filename)
        filepath = os.path.join(temp_dir, filename)
        file.save(filepath)
        
        from servidor.parser_jalisco import extraer_jalisco_documento
        res = extraer_jalisco_documento(filepath)
        
        try: os.remove(filepath)
        except Exception: pass
        
        # Vincular con catalogos.equipos
        db = get_db()
        cur = db.cursor(cursor_factory=DictCursor)
        cur.execute("SELECT numero_economico, descripcion, tipo_equipo FROM catalogos.equipos")
        cat_equipos = cur.fetchall()
        cur.close()
        db.close()
        
        # Mapear cada consumo extraído
        import difflib
        for item in res.get('consumos', []):
            eq_name = str(item.get('equipo', '')).strip()
            best_match = None
            best_score = 0.0
            
            for eq in cat_equipos:
                desc = eq['descripcion'] or ''
                num = eq['numero_economico'] or ''
                
                if eq_name.lower() == desc.lower() or eq_name.lower() == num.lower():
                    best_match = eq
                    best_score = 1.0
                    break
                    
                score1 = difflib.SequenceMatcher(None, eq_name.lower(), desc.lower()).ratio()
                score2 = difflib.SequenceMatcher(None, eq_name.lower(), num.lower()).ratio()
                score = max(score1, score2)
                
                if eq_name.lower() in desc.lower() or (len(eq_name) > 4 and desc.lower() in eq_name.lower()):
                    score = max(score, 0.85)
                    
                if score > best_score:
                    best_score = score
                    best_match = eq
            
            if best_match and best_score >= 0.7:
                item['equipo_economico'] = best_match['numero_economico']
                item['equipo'] = best_match['descripcion']
                item['en_catalogo'] = True
            else:
                item['equipo_economico'] = eq_name[:20]
                item['en_catalogo'] = False
        
        return jsonify({'success': True, 'data': res})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/jalisco/guardar_masivo', methods=['POST'])
def api_jalisco_guardar_masivo():
    try:
        payload = request.get_json()
        consumos = payload.get('consumos', [])
        if not consumos:
            return jsonify({'success': False, 'error': 'No hay consumos para guardar.'})
            
        db = get_db()
        cur = db.cursor(cursor_factory=DictCursor)
        
        insertados = 0
        equipos_creados = 0
        
        for item in consumos:
            fecha = item.get('fecha')
            semana = item.get('semana')
            equipo = str(item.get('equipo', '')).strip()
            equipo_eco = str(item.get('equipo_economico', '')).strip() or equipo[:20]
            litros = float(item.get('litros') or 0)
            costo = float(item.get('costo_por_litro') or 27.0)
            importe = float(item.get('importe_total') or round(litros * costo, 2))
            tipo_comb = str(item.get('tipo_combustible', 'DIESEL')).upper()
            obs = str(item.get('observaciones', 'Captura Masiva Jalisco'))
            
            if litros <= 0 or not equipo:
                continue

            # Verificar si el equipo existe en catalogos.equipos
            cur.execute("SELECT numero_economico FROM catalogos.equipos WHERE LOWER(descripcion) = LOWER(%s) OR LOWER(numero_economico) = LOWER(%s)", (equipo, equipo_eco))
            if not cur.fetchone():
                try:
                    tipo_eq = 'GASOLINA' if tipo_comb == 'GASOLINA' else 'DIESEL'
                    cur.execute("""
                        INSERT INTO catalogos.equipos (numero_economico, descripcion, tipo_equipo)
                        VALUES (%s, %s, %s)
                    """, (equipo_eco, equipo, tipo_eq))
                    equipos_creados += 1
                except Exception: pass

            # Calcular saldo teorico acumulado
            cur.execute("SELECT saldo_teorico FROM diesel.jalisco_movimientos ORDER BY id DESC LIMIT 1")
            last = cur.fetchone()
            saldo_actual = float(last['saldo_teorico']) if last else 0.0
            saldo_nuevo = saldo_actual - litros

            cur.execute("""
                INSERT INTO diesel.jalisco_movimientos
                (fecha, semana, tipo_movimiento, equipo_economico, equipo, litros, costo_por_litro, importe_total, saldo_teorico, observaciones, tipo_combustible)
                VALUES (%s, %s, 'SALIDA', %s, %s, %s, %s, %s, %s, %s, %s)
            """, (fecha, semana, equipo_eco, equipo, litros, costo, importe, saldo_nuevo, obs, tipo_comb))
            insertados += 1

        db.commit()
        cur.close()
        db.close()
        
        return jsonify({
            'success': True,
            'insertados': insertados,
            'equipos_creados': equipos_creados
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/acarreos')
def view_acarreos():
    return render_template('en_construccion.html', modulo='Acarreos')

@app.route('/mezcla')
def view_mezcla():
    return render_template('en_construccion.html', modulo='Mezcla Asfáltica')

@app.route('/solicitudes')
def view_solicitudes():
    db = get_db()
    cur = db.cursor(cursor_factory=DictCursor)
    cur.execute('SELECT nombre FROM catalogos.obras ORDER BY nombre')
    obras = cur.fetchall()
    cur.execute("SELECT numero_economico, descripcion FROM catalogos.equipos WHERE tipo_equipo = 'DIESEL' OR tipo_equipo IS NULL ORDER BY numero_economico")
    equipos = cur.fetchall()
    db.close()
    return render_template('captura_solicitudes.html',
        obras=obras,
        equipos=equipos,
        current_date=datetime.datetime.now().strftime('%Y-%m-%d'),
        current_week=get_current_week()
    )

@app.route('/api/solicitudes/guardar', methods=['POST'])
def api_solicitudes_guardar():
    data = request.get_json()
    tipo = data.get('tipo', 'diesel')  # 'diesel' o 'gasolina'
    try:
        db = get_db()
        cur = db.cursor(cursor_factory=DictCursor)
        now = datetime.datetime.now()
        folio = f"SOL-{'D' if tipo=='diesel' else 'G'}-{now.strftime('%Y%m%d%H%M%S')}"
        semana = str(data.get('semana', '')).replace('Semana ', '').replace('Semana', '').strip().replace('Semana ', '').replace('Semana', '').strip()
        fecha = data.get('fecha') or now.strftime('%Y-%m-%d')
        litros = float(data.get('litros') or 0)
        precio = float(data.get('precio_unitario') or 0)
        importe = float(data.get('importe_total') or 0) or round(litros * precio, 2)

        obra_clean = normalizar_obra_nombre(data.get('obra_destino', ''))

        if tipo == 'diesel':
            cur.execute("""
                INSERT INTO diesel.solicitudes
                    (folio_solicitud, fecha, semana, solicitante, tipo_movimiento, obra_destino,
                     equipo_economico, litros, costo_por_litro, importe_total, responsable,
                     estatus_conciliacion, observaciones)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'PENDIENTE', %s)
            """, (
                folio, fecha, semana,
                data.get('solicitante', ''),
                'SOLICITUD DIESEL',
                obra_clean,
                data.get('equipo_economico', ''),
                litros, precio, importe,
                data.get('solicitante', ''),
                data.get('observaciones', '')
            ))
        else:
            cur.execute("""
                INSERT INTO gasolina.solicitudes
                    (folio_solicitud, fecha, semana, solicitante, gasolinera, obra_destino,
                     vehiculo, litros, precio_unitario, importe_total, responsable,
                     estatus_conciliacion, observaciones)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'PENDIENTE', %s)
            """, (
                folio, fecha, semana,
                data.get('solicitante', ''),
                data.get('gasolinera', 'LEVET'),
                obra_clean,
                data.get('vehiculo', ''),
                litros, precio, importe,
                data.get('solicitante', ''),
                data.get('observaciones', '')
            ))
        db.commit()
        db.close()
        return jsonify({'success': True, 'folio': folio})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/solicitudes/historial')
def api_solicitudes_historial():
    tipo = request.args.get('tipo', 'diesel')
    try:
        db = get_db()
        cur = db.cursor(cursor_factory=DictCursor)
        if tipo == 'diesel':
            cur.execute("""
                SELECT folio_solicitud as folio, fecha::text, semana, obra_destino as obra,
                       litros, importe_total as importe, estatus_conciliacion as estatus
                FROM diesel.solicitudes
                ORDER BY id DESC LIMIT 50
            """)
        else:
            cur.execute("""
                SELECT folio_solicitud as folio, fecha::text, semana, obra_destino as obra,
                       litros, importe_total as importe, estatus_conciliacion as estatus
                FROM gasolina.solicitudes
                ORDER BY id DESC LIMIT 50
            """)
        rows = [dict(r) for r in cur.fetchall()]
        db.close()
        return jsonify(rows)
    except Exception as e:
        return jsonify([])

@app.route('/catalogos')
def view_catalogos():
    db = get_db()
    cur = db.cursor(cursor_factory=DictCursor)
    cur.execute('SELECT * FROM catalogos.obras')
    obras = cur.fetchall()
    cur.execute('SELECT * FROM catalogos.equipos')
    equipos = cur.fetchall()
    cur.execute('SELECT * FROM catalogos.operadores')
    operadores = cur.fetchall()
    db.close()
    return render_template('catalogos.html', obras=obras, equipos=equipos, operadores=operadores)

@app.route('/api/get_responsable/<obra_nombre>')
def api_get_responsable(obra_nombre):
    db = get_db()
    cur = db.cursor(cursor_factory=DictCursor)
    cur.execute('SELECT responsable_default FROM catalogos.obras WHERE nombre=%s', (obra_nombre,))
    res = cur.fetchone()
    db.close()
    return jsonify({'responsable': res['responsable_default'] if res else ''})

@app.route('/api/get_operador/<equipo_eco>')
def api_get_operador(equipo_eco):
    db = get_db()
    cur = db.cursor(cursor_factory=DictCursor)
    cur.execute('SELECT operador_default FROM catalogos.equipos WHERE numero_economico=%s', (equipo_eco,))
    res = cur.fetchone()
    db.close()
    op = res['operador_default'] if res and res['operador_default'] else 'Sin Registro'
    return jsonify({'operador': op})

@app.route('/api/parse_factura', methods=['POST'])
def api_parse_factura():
    res = {'cargas': [], 'obra_texto': '', 'obra_sugerida': '', 'uuid': '', 'fecha': '', 'facturas_pagadas': [], 'monto_pago': 0}
    
    tipo_doc = request.form.get('tipo_doc', 'factura')
    archivo_pdf = request.files.get('archivo_pdf')
    archivo_xml = request.files.get('archivo_xml')
    
    if archivo_pdf and pdfplumber:
        try:
            with pdfplumber.open(archivo_pdf) as pdf:
                text = pdf.pages[0].extract_text()
                match = re.search(r'Fecha de Vencimiento:\s*\S+\s+(.*)', text, re.IGNORECASE)
                if match:
                    res['obra_texto'] = match.group(1).strip()
        except: pass

    if archivo_xml:
        try:
            tree = ET.parse(archivo_xml)
            root = tree.getroot()
            ns = {'cfdi': 'http://www.sat.gob.mx/cfd/4', 'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'}
            
            res['fecha'] = root.get('Fecha', '').split('T')[0]
            if res['fecha']:
                try:
                    res['semana'] = datetime.datetime.strptime(res['fecha'], '%Y-%m-%d').isocalendar()[1]
                except:
                    res['semana'] = ''

            # Folio y serie del comprobante
            serie = root.get('Serie', '')
            folio_num = root.get('Folio', '')
            res['folio_factura'] = f"{serie}{folio_num}".strip() if (serie or folio_num) else ''

            # Emisor (proveedor)
            emisor = root.find('cfdi:Emisor', ns)
            if emisor is not None:
                res['proveedor'] = emisor.get('Nombre', '')
            else:
                res['proveedor'] = ''

            timbre = root.find('.//tfd:TimbreFiscalDigital', ns)
            if timbre is not None:
                res['uuid'] = timbre.get('UUID', '')
            
            for c in root.findall('.//cfdi:Concepto', ns):
                desc = c.get('Descripcion', '').lower()
                clave = c.get('ClaveProdServ', '')
                
                # If it's a complemento, the concept is 'Pago' 84111506
                if tipo_doc == 'complemento':
                    break # we extract from Pagos node instead

                # Filter for Diesel, ignore Gasolina/Magna/Premium
                if ('diesel' in desc or 'diésel' in desc or clave == '15101505') and not any(x in desc for x in ['magna', 'premium', 'gasolina']):
                    litros = float(c.get('Cantidad', 0))
                    precio = float(c.get('ValorUnitario', 0))
                    subtotal = float(c.get('Importe', 0))
                    iva = 0
                    for imp in c.findall('.//cfdi:Traslado', ns):
                        if imp.get('Impuesto') == '002':
                            iva += float(imp.get('Importe', 0))
                    res['cargas'].append({
                        'descripcion': c.get('Descripcion'),
                        'litros': round(litros, 2),
                        'precio': round(precio, 2),
                        'subtotal': round(subtotal, 2),
                        'iva': round(iva, 2),
                        'total': round(subtotal + iva, 2)
                    })
                    
            if tipo_doc == 'complemento':
                pagos = root.findall('.//*[local-name()="Pago"]')
                monto_total_pago = 0
                for p in pagos:
                    monto_total_pago += float(p.get('Monto', 0))
                    doctos = p.findall('.//*[local-name()="DoctoRelacionado"]')
                    for d in doctos:
                        res['facturas_pagadas'].append({
                            'uuid_relacionado': d.get('IdDocumento', ''),
                            'folio_relacionado': d.get('Folio', ''),
                            'monto_pagado': float(d.get('ImpPagado', 0) or 0)
                        })
                res['monto_pago'] = round(monto_total_pago, 2)

        except Exception as e:
            print("XML Error:", e)

    # Map Punto de Carga to Obras
    if res['obra_texto']:
        db = get_db()
        cur = db.cursor(cursor_factory=DictCursor)
        cur.execute("SELECT nombre, codigo FROM catalogos.obras")
        obras = cur.fetchall()
        db.close()
        texto = res['obra_texto'].upper()
        # Some manual mappings based on typical names
        if 'PEGASO' in texto and 'ASFALTO' not in texto: res['obra_sugerida'] = 'PLANTA PEGASO'
        elif 'TRES MARIAS' in texto or 'LERMA' in texto: res['obra_sugerida'] = 'LERMA - TRES MARÍAS'
        elif 'ALFREDO' in texto or 'DEL MAZO' in texto: res['obra_sugerida'] = 'ALFREDO DEL MAZO'
        elif 'HUIXQUILUCAN' in texto: res['obra_sugerida'] = 'P. ASFALTO HUIXQUILUCAN'
        elif 'MEXICO' in texto and 'TOLUCA' in texto: res['obra_sugerida'] = 'OBRA MÉXICO TOLUCA'
        else:
            for o in obras:
                if o['nombre'].upper() in texto or (o['codigo'] and o['codigo'].upper() in texto):
                    res['obra_sugerida'] = o['nombre']
                    break

    return jsonify(res)

@app.route('/api/gasolina/tope_status')
def api_gasolina_tope_status():
    vehiculo = request.args.get('vehiculo', '').strip()
    placa = request.args.get('placa', '').strip()
    maestro_id = request.args.get('maestro_id')
    semana_str = str(request.args.get('semana', '')).replace('Semana ', '').replace('Semana', '').strip()
    precio_unitario = float(request.args.get('precio_unitario', 23.90) or 23.90)

    try:
        semana_num = int(semana_str) if semana_str else get_current_week()
    except:
        semana_num = get_current_week()

    try:
        db = get_db()
        cur = db.cursor(cursor_factory=DictCursor)
        
        # 1. Asegurar arrastre
        sync_gasolina_autorizaciones_arrastre(db, semana_num)
        
        monto_autorizado = 0.0
        if maestro_id and str(maestro_id).isdigit():
            cur.execute("""
                SELECT importe_semanal, unidad_equipo, placas 
                FROM gasolina.autorizaciones_semanal 
                WHERE semana = %s AND maestro_id = %s
            """, (semana_num, int(maestro_id)))
            auth_row = cur.fetchone()
            if auth_row:
                monto_autorizado = float(auth_row['importe_semanal'] or 0)
                if not vehiculo: vehiculo = auth_row['unidad_equipo']
                if not placa: placa = auth_row['placas']
        else:
            ref_search = placa if (placa and placa != 'S/P') else vehiculo
            cur.execute("""
                SELECT importe_semanal, unidad_equipo, placas 
                FROM gasolina.autorizaciones_semanal 
                WHERE semana = %s AND (
                    (placas IS NOT NULL AND placas != 'S/P' AND placas ILIKE %s) OR
                    (unidad_equipo IS NOT NULL AND unidad_equipo ILIKE %s)
                )
                LIMIT 1
            """, (semana_num, f"%{ref_search}%", f"%{ref_search}%"))
            auth_row = cur.fetchone()
            if auth_row:
                monto_autorizado = float(auth_row['importe_semanal'] or 0)

        litros_autorizados = round(monto_autorizado / precio_unitario, 2) if precio_unitario > 0 else 0.0
        
        ref_p = placa if (placa and placa != 'S/P') else ''
        ref_v = vehiculo if vehiculo else ''
        
        cur.execute("""
            SELECT SUM(litros) as total_litros, SUM(importe_total) as total_importe
            FROM gasolina.consumos
            WHERE semana = %s AND (
                (placa IS NOT NULL AND placa != 'S/P' AND placa ILIKE %s) OR
                (vehiculo IS NOT NULL AND vehiculo ILIKE %s)
            ) AND estatus_revision != 'RECHAZADO'
        """, (str(semana_num), f"%{ref_p or ref_v}%", f"%{ref_v or ref_p}%"))
        cons_row = cur.fetchone()
        
        consumido_litros = float(cons_row['total_litros'] or 0) if (cons_row and cons_row['total_litros']) else 0.0
        consumido_importe = float(cons_row['total_importe'] or 0) if (cons_row and cons_row['total_importe']) else 0.0
        
        disponible_importe = max(0.0, round(monto_autorizado - consumido_importe, 2))
        disponible_litros = max(0.0, round(litros_autorizados - consumido_litros, 2))
        
        db.close()
        return jsonify({
            'success': True,
            'placa': placa,
            'vehiculo': vehiculo,
            'semana': semana_num,
            'monto_autorizado': round(monto_autorizado, 2),
            'litros_autorizados': round(litros_autorizados, 2),
            'consumido_importe': round(consumido_importe, 2),
            'consumido_litros': round(consumido_litros, 2),
            'disponible_importe': disponible_importe,
            'disponible_litros': disponible_litros,
            'excedido': consumido_importe > monto_autorizado and monto_autorizado > 0
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/gasolina/consumo', methods=['POST'])
def api_post_gasolina():
    try:
        db = get_db()
        data = request.form
        fotos = request.files.getlist('foto_evidencia')

        foto_blob = None
        if fotos and len(fotos) > 0 and fotos[0].filename != '':
            if len(fotos) == 1:
                foto_blob = fotos[0].read()
            else:
                import io, zipfile
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for f in fotos:
                        if f.filename:
                            zip_file.writestr(f.filename, f.read())
                foto_blob = zip_buffer.getvalue()

        cur = db.cursor(cursor_factory=DictCursor)
        obra_raw = (data.get('obra_destino') or '').strip()
        obra_dest = obra_raw if obra_raw != '' else None

        obra_codigo = 'XX'
        if obra_dest:
            cur.execute('SELECT codigo FROM catalogos.obras WHERE nombre=%s', (obra_dest,))
            obra_row = cur.fetchone()
            if obra_row:
                obra_codigo = obra_row['codigo']

        semana = str(data.get('semana', '')).replace('Semana ', '').replace('Semana', '').strip()

        cur.execute("SELECT folio_conciliacion FROM gasolina.consumos WHERE folio_conciliacion LIKE %s", (f"GAS-%-{semana}-%%",))
        folios = cur.fetchall()
        max_cons = 0
        for f in folios:
            parts = f['folio_conciliacion'].split('-')
            if len(parts) >= 4:
                try:
                    num = int(parts[-1])
                    if num > max_cons: max_cons = num
                except: pass
        consecutivo = max_cons + 1
        folio = f"GAS-{obra_codigo}-{semana}-{consecutivo:03d}"

        litros = float(data.get('litros', 0))
        costo = float(data.get('costo_por_litro', 0))
        importe = round(litros * costo, 2)
        
        fecha_val = data.get('fecha')
        if not fecha_val:
            import datetime
            fecha_val = datetime.date.today().strftime('%Y-%m-%d')

        es_extraordinario = data.get('es_extraordinario') in ['1', 'true', True]
        motivo_extra = (data.get('motivo_extraordinario') or '').strip()
        obs = (data.get('observaciones') or '').strip()
        if es_extraordinario:
            prefix = f"[CARGA EXTRAORDINARIA{': ' + motivo_extra if motivo_extra else ''}]"
            obs = f"{prefix} {obs}".strip()

        vehiculo_val = (data.get('vehiculo') or '').strip() or None
        placa_val = (data.get('placa') or '').strip() or None
        conductor_val = (data.get('conductor') or '').strip() or None

        if placa_val:
            cur.execute('SELECT 1 FROM catalogos.equipos WHERE numero_economico = %s', (placa_val,))
            if not cur.fetchone():
                desc_veh = vehiculo_val or f"Vehículo {placa_val}"
                cur.execute('''
                    INSERT INTO catalogos.equipos (numero_economico, descripcion, tipo_equipo)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (numero_economico) DO NOTHING
                ''', (placa_val, desc_veh, 'GASOLINA'))

        gasolineria_val = (data.get('gasolineria') or 'LEVET').strip()

        cur.execute('''INSERT INTO gasolina.consumos
            (folio_conciliacion, fecha, semana, origen, obra_destino, vehiculo, placa, kilometraje, litros, costo_por_litro, importe_total, conductor, observaciones, foto_evidencia, gasolineria)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
            (folio, fecha_val, semana, data.get('origen', 'Gasolineria'), obra_dest,
             vehiculo_val, placa_val, data.get('kilometraje') or None,
             litros, costo, importe, conductor_val, obs, foto_blob, gasolineria_val))
        db.commit()
        db.close()
        return jsonify({'success': True, 'folio': folio})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/gasolina/facturas_batch', methods=['POST'])
def api_post_gasolina_facturas():
    try:
        data = request.json
        db = get_db()
        semana = str(data.get('semana', '')).replace('Semana ', '').replace('Semana', '').strip().replace('Semana ', '').replace('Semana', '').strip()
        obra_nombre = data.get('obra', '')
        cur = db.cursor(cursor_factory=DictCursor)
        cur.execute('SELECT codigo FROM catalogos.obras WHERE nombre=%s', (obra_nombre,))
        obra_row = cur.fetchone()
        obra_codigo = obra_row['codigo'] if obra_row else 'XX'

        cur.execute("SELECT folio_conciliacion FROM gasolina.facturas WHERE folio_conciliacion LIKE %s", (f"FA-%-{semana}-%%",))
        folios = cur.fetchall()
        max_cons = 0
        for f in folios:
            parts = f['folio_conciliacion'].split('-')
            if len(parts) >= 4:
                try:
                    num = int(parts[-1])
                    if num > max_cons: max_cons = num
                except: pass
        consecutivo = max_cons + 1

        total_lts = sum(c['litros'] for c in data['cargas'])
        total_imp = sum(c['total'] for c in data['cargas'])
        folio_final = f"FA-{obra_codigo}-{semana}-{consecutivo:03d}"

        cur.execute('''INSERT INTO gasolina.facturas
            (folio_conciliacion, folio_factura, fecha_factura, semana, proveedor, litros_facturados, importe_total, uuid_cfdi)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
            (folio_final, data.get('folio_factura', ''), data['fecha'], semana,
             data.get('proveedor', 'PROVEEDOR'), total_lts, total_imp, data['uuid']))
        db.commit()
        db.close()
        return jsonify({'success': True, 'folio': folio_final})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


def normalizar_equipos_filas_con_catalogo(filas, db_conn):
    try:
        cur = db_conn.cursor(cursor_factory=DictCursor)
        cur.execute("SELECT numero_economico, descripcion FROM catalogos.equipos WHERE numero_economico IS NOT NULL AND numero_economico != ''")
        catalog = cur.fetchall()
        
        for f in filas:
            eq_text = (f.get('equipo') or '').strip()
            eco_text = (f.get('economico') or '').strip()
            
            if ' - ' in eq_text:
                continue
                
            best_match = None
            eq_upper = eq_text.upper()
            eco_upper = eco_text.upper()
            
            if eco_upper:
                for item in catalog:
                    if item['numero_economico'].strip().upper() == eco_upper:
                        best_match = item
                        break
                        
            if not best_match and eq_text:
                for item in catalog:
                    desc_upper = item['descripcion'].strip().upper() if item['descripcion'] else ''
                    if desc_upper and desc_upper == eq_upper:
                        best_match = item
                        break
                        
                if not best_match:
                    longest_match_len = 0
                    for item in catalog:
                        desc_upper = item['descripcion'].strip().upper() if item['descripcion'] else ''
                        if desc_upper and len(desc_upper) >= 3 and desc_upper in eq_upper:
                            if len(desc_upper) > longest_match_len:
                                longest_match_len = len(desc_upper)
                                best_match = item

                if not best_match:
                    for item in catalog:
                        code_upper = item['numero_economico'].strip().upper()
                        if code_upper and len(code_upper) >= 3 and code_upper in eq_upper:
                            best_match = item
                            break

            if best_match:
                f['equipo'] = f"{best_match['numero_economico']} - {best_match['descripcion']}"
                f['economico'] = best_match['numero_economico']
    except Exception as e:
        print("Error normalizando equipos con catálogo:", e)


@app.route('/api/diesel/extraer_bitacora_pdf', methods=['POST'])
def api_diesel_extraer_bitacora_pdf():
    try:
        pdf_file = request.files.get('archivo_pdf')
        if not pdf_file or pdf_file.filename == '':
            return jsonify({'success': False, 'error': 'No se proporcionó ningún archivo PDF.'})
            
        temp_dir = os.path.join(STAT_DIR, 'temp_pdf')
        os.makedirs(temp_dir, exist_ok=True)
        
        filename = f"bitacora_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{pdf_file.filename}"
        save_path = os.path.join(temp_dir, filename)
        pdf_file.save(save_path)
        
        # Parse PDF con bitacora_pdf_service
        resultado = parse_bitacora_pdf(save_path)
        semana_detectada = resultado.get('semana', get_current_week())
        
        db = get_db()
        # Normalizar nombres de equipos extraídos del PDF contra catálogo (NUMERO_ECONOMICO - DESCRIPCION)
        normalizar_equipos_filas_con_catalogo(resultado.get('filas', []), db)

        # Validar duplicados contra la base de datos para esta semana y obra
        filas_val, dup_count = validar_duplicados_semana(db, semana_detectada, resultado.get('filas', []), resultado.get('obra_detectada', ''))
        db.close()
        
        # URL relativa para visor PDF iframe
        pdf_url = f"/static/temp_pdf/{filename}"
        
        return jsonify({
            'success': True,
            'pdf_url': pdf_url,
            'semana': semana_detectada,
            'operador': resultado.get('operador', ''),
            'marimba': resultado.get('marimba', 'Marimba M-01'),
            'obra_detectada': resultado.get('obra_detectada', ''),
            'filas': filas_val,
            'duplicados_count': dup_count
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/diesel/validar_duplicados', methods=['POST'])
def api_diesel_validar_duplicados():
    try:
        data = request.get_json() or {}
        semana = data.get('semana', get_current_week())
        filas = data.get('filas', [])
        obra_gen = data.get('obra_general', '')
        
        db = get_db()
        filas_val, dup_count = validar_duplicados_semana(db, semana, filas, obra_gen)
        db.close()
        
        return jsonify({
            'success': True,
            'filas': filas_val,
            'duplicados_count': dup_count
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/diesel/guardar_bitacora_masiva', methods=['POST'])
def api_diesel_guardar_bitacora_masiva():
    try:
        data = request.get_json()
        if not data or 'filas' not in data or not data['filas']:
            return jsonify({'success': False, 'error': 'No hay filas de consumos para guardar.'})
            
        semana_gral = str(data.get('semana', get_current_week())).replace('Semana ', '').replace('Semana', '').strip()
        obra_general = data.get('obra_general', 'OBRA MÉXICO TOLUCA')
        responsable_general = data.get('responsable_general', 'Francisco Javier')
        origen = data.get('origen', 'Marimba M-01')
        
        db = get_db()
        cur = db.cursor(cursor_factory=DictCursor)
        
        # Obtener código de la obra
        cur.execute('SELECT codigo FROM catalogos.obras WHERE nombre=%s', (obra_general,))
        obra_row = cur.fetchone()
        obra_codigo = obra_row['codigo'] if obra_row else 'XX'
        
        # Cargar catálogos para resolver FKs
        cur.execute("SELECT numero_economico, descripcion FROM catalogos.equipos")
        eq_rows = cur.fetchall()
        num_ecos = {r['numero_economico'].strip().upper(): r['numero_economico'] for r in eq_rows if r['numero_economico']}
        num_descs = {r['descripcion'].strip().upper(): r['numero_economico'] for r in eq_rows if r['descripcion']}

        cur.execute("SELECT nombre FROM catalogos.obras")
        obras_set = {r['nombre'].strip().upper(): r['nombre'] for r in cur.fetchall()}

        def resolver_equipo(txt_raw):
            if not txt_raw: return None, ''
            txt_clean = str(txt_raw).strip()
            txt_upper = txt_clean.upper()
            if txt_upper in num_ecos:
                return num_ecos[txt_upper], txt_clean
            if ' - ' in txt_clean:
                code_p = txt_clean.split(' - ')[0].strip().upper()
                if code_p in num_ecos:
                    return num_ecos[code_p], txt_clean
            if txt_upper in num_descs:
                return num_descs[txt_upper], txt_clean
            for code, real_code in num_ecos.items():
                if code and len(code) >= 2 and code in txt_upper:
                    return real_code, txt_clean
            return None, txt_clean

        def resolver_obra(obra_raw, obra_gen):
            if obra_raw and str(obra_raw).strip().upper() in obras_set:
                return obras_set[str(obra_raw).strip().upper()]
            for o_upper, o_real in obras_set.items():
                if obra_raw and o_upper in str(obra_raw).strip().upper():
                    return o_real
            return obra_gen

        # Buscar consecutivos existentes
        cur.execute("SELECT folio_conciliacion FROM diesel.consumos WHERE folio_conciliacion LIKE %s", (f"CMQ-{obra_codigo}-%",))
        folios = cur.fetchall()
        max_cons = 0
        for f in folios:
            parts = f['folio_conciliacion'].split('-')
            if len(parts) >= 4:
                try:
                    num = int(parts[-1])
                    if num > max_cons: max_cons = num
                except: pass
                
        consecutivo = max_cons
        guardados = 0
        
        for fila in data['filas']:
            litros = float(fila.get('litros') or fila.get('salida') or 0)
            if litros <= 0:
                continue
                
            fecha_val = fila.get('fecha') or datetime.date.today().strftime('%Y-%m-%d')
            if fila.get('semana'):
                semana_row = str(fila['semana']).replace('Semana ', '').replace('Semana', '').strip()
            else:
                try:
                    f_dt = datetime.datetime.strptime(fecha_val, '%Y-%m-%d').date()
                    semana_row = str(f_dt.isocalendar()[1])
                except:
                    semana_row = semana_gral

            consecutivo += 1
            folio = f"CMQ-{obra_codigo}-{semana_row}-{consecutivo:03d}"
            
            equipo_raw = fila.get('equipo', 'MAQUINARIA')
            eq_eco, eq_desc = resolver_equipo(equipo_raw)
            obra_row_val = resolver_obra(fila.get('origen_obra') or fila.get('obra'), obra_general)
            responsable_row_val = fila.get('responsable') or responsable_general
            ticket_val = fila.get('ticket') or fila.get('ticket_ref') or ''
            obs_val = fila.get('observaciones') or ''
            
            if ticket_val and ticket_val not in obs_val:
                obs_val = f"[Ticket: {ticket_val}] {obs_val}".strip()
                
            costo = 27.00
            importe = round(litros * costo, 2)
            
            # Insertar en PostgreSQL fenix_db con estatus APROBADO
            cur.execute("""
                INSERT INTO diesel.consumos
                (folio_conciliacion, fecha, semana, origen, tipo_movimiento,
                 obra_destino, responsable, equipo_economico, equipo, litros, costo_por_litro, importe_total, estatus_revision, observaciones)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'APROBADO', %s)
            """, (
                folio, fecha_val, semana_row, origen, 'CARGA MAQUINARIA',
                obra_row_val, responsable_row_val, eq_eco, eq_desc, litros, costo, importe, obs_val
            ))
            guardados += 1
            
        db.commit()
        db.close()
        
        return jsonify({
            'success': True,
            'registros_guardados': guardados,
            'message': f'¡Se guardaron exitosamente {guardados} partidas desde la bitácora PDF!'
        })
    except Exception as e:
        if 'db' in locals() and db:
            try: db.rollback(); db.close()
            except: pass
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/sync_excel', methods=['POST'])
def api_sync_excel():
    try:
        excel_path = os.path.join(BASE_DIR, 'MAESTRO_CONTROL_DIESEL_NUEVO.xlsx')
        if not os.path.exists(excel_path):
            return jsonify({'success': False, 'error': 'No se encontró el archivo Excel Maestro.'})

        db = get_db()
        
        # 1. FASE DE IMPORTACIÓN (Excel -> SQLite)
        df_excel = pd.read_excel(excel_path, sheet_name='BD_DIESEL')
        df_excel = df_excel.dropna(subset=['FOLIO_CONCILIACION'])
        
        cur = db.cursor(cursor_factory=DictCursor)
        cur.execute('SELECT folio_conciliacion FROM diesel.consumos')
        db_folios = [row['folio_conciliacion'] for row in cur.fetchall()]
        
        nuevos_en_excel = df_excel[~df_excel['FOLIO_CONCILIACION'].isin(db_folios)]
        
        def to_py(val):
            if pd.isna(val): return None
            if hasattr(val, 'strftime'): return val.strftime('%Y-%m-%d')
            if isinstance(val, (np.int64, np.int32)): return int(val)
            if isinstance(val, (np.float64, np.float32)): return float(val)
            return str(val) if not isinstance(val, (str, int, float)) else val

        for _, row in nuevos_en_excel.iterrows():
            r = {k: to_py(v) for k, v in row.items()}
            semana_val = str(r['SEMANA']).replace('Semana', '').strip() if r['SEMANA'] else None
            cur.execute('''INSERT INTO diesel.consumos 
                (folio_conciliacion, fecha, semana, origen, tipo_movimiento, obra_destino, equipo, equipo_economico, litros, costo_por_litro, importe_total, responsable, operador, observaciones)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''', 
                (r['FOLIO_CONCILIACION'], r['FECHA'], semana_val, r['ORIGEN'], r['TIPO_MOVIMIENTO'], r['OBRA_DESTINO'], r['EQUIPO'], r['EQUIPO_ECONOMICO'], r['LITROS'], r['COSTO_POR_LITRO'], r['IMPORTE_TOTAL'], r['RESPONSABLE'], r['OPERADOR'], r['OBSERVACIONES']))
        
        db.commit()
        
        # 2. FASE DE EXPORTACIÓN (SQLite -> Excel)
        df_db = pd.read_sql_query('SELECT folio_conciliacion, fecha, semana, origen, tipo_movimiento, obra_destino, equipo, equipo_economico, litros, costo_por_litro, importe_total, responsable, operador, observaciones FROM diesel.consumos', db)
        
        df_db = df_db.rename(columns={
            'folio_conciliacion': 'FOLIO_CONCILIACION',
            'fecha': 'FECHA',
            'semana': 'SEMANA',
            'origen': 'ORIGEN',
            'tipo_movimiento': 'TIPO_MOVIMIENTO',
            'obra_destino': 'OBRA_DESTINO',
            'equipo': 'EQUIPO',
            'equipo_economico': 'EQUIPO_ECONOMICO',
            'litros': 'LITROS',
            'costo_por_litro': 'COSTO_POR_LITRO',
            'importe_total': 'IMPORTE_TOTAL',
            'responsable': 'RESPONSABLE',
            'operador': 'OPERADOR',
            'observaciones': 'OBSERVACIONES'
        })
        
        df_db['ESTATUS_CONCILIACION'] = ''
        columnas_orden = ['FOLIO_CONCILIACION', 'FECHA', 'SEMANA', 'ORIGEN', 'TIPO_MOVIMIENTO', 'OBRA_DESTINO', 'EQUIPO', 'EQUIPO_ECONOMICO', 'LITROS', 'COSTO_POR_LITRO', 'IMPORTE_TOTAL', 'RESPONSABLE', 'OPERADOR', 'ESTATUS_CONCILIACION', 'OBSERVACIONES']
        df_db = df_db[columnas_orden]
        
        with pd.ExcelWriter(excel_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df_db.to_excel(writer, sheet_name='BD_DIESEL', index=False)
            
        db.close()
        
        return jsonify({'success': True, 'importados': len(nuevos_en_excel), 'exportados': len(df_db)})
        
    except PermissionError:
        return jsonify({'success': False, 'error': 'El archivo Excel está abierto por otro programa (probablemente Excel). Ciérralo e intenta de nuevo.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/diesel/facturas_batch', methods=['POST'])
def api_post_facturas_batch():
    try:
        data = request.json
        db = get_db()
        
        semana = str(data.get('semana', '')).replace('Semana ', '').replace('Semana', '').strip().replace('Semana ', '').replace('Semana', '').strip()
        obra_nombre = data.get('obra', '')
        
        # 1. Obtener codigo de obra
        cur = db.cursor(cursor_factory=DictCursor)
        cur.execute('SELECT codigo FROM catalogos.obras WHERE nombre=%s', (obra_nombre,))
        obra_row = cur.fetchone()
        obra_codigo = obra_row['codigo'] if obra_row else 'XX'
        
        # 2. Consecutivo - buscar en diesel.facturas
        cur.execute("SELECT folio_conciliacion FROM diesel.facturas WHERE folio_conciliacion LIKE %s", (f"FAC-%-{semana}-%%",))
        folios = cur.fetchall()
        max_cons = 0
        for f in folios:
            parts = f['folio_conciliacion'].split('-')
            if len(parts) >= 4:
                try:
                    num = int(parts[-1])
                    if num > max_cons: max_cons = num
                except: pass
        
        consecutivo = max_cons + 1
        
        for c in data['cargas']:
            folio_final = f"FA-{obra_codigo}-{semana}-{consecutivo:03d}"
            
            cur.execute("""INSERT INTO diesel.facturas
                (folio_conciliacion, folio_factura, fecha_factura, semana, proveedor,
                 punto_de_carga, litros_facturados, precio_unitario, importe, iva, importe_total, uuid_cfdi)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (
                folio_final,
                data.get('folio_factura', ''),
                data['fecha'],
                semana,
                data.get('proveedor', c.get('descripcion', 'DIESEL')),
                obra_nombre,
                c['litros'],
                c['precio'],
                round(c['litros'] * c['precio'], 2),
                c['iva'],
                c['total'],
                data['uuid']
            ))
            consecutivo += 1
            
        db.commit()
        db.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/diesel/guardar_complemento', methods=['POST'])
def api_guardar_complemento():
    try:
        data = request.json
        db = get_db()
        cur = db.cursor()
        
        # Insert into complementos_pago
        cur.execute("""
            INSERT INTO diesel.complementos_pago 
            (folio_complemento, fecha_pago, proveedor, monto_total)
            VALUES (%s, %s, %s, %s) RETURNING id
        """, (data.get('folio', ''), data.get('fecha'), data.get('proveedor', ''), data.get('monto_total', 0)))
        
        comp_id = cur.fetchone()[0]
        
        # Link facturas
        facturas_pagadas = data.get('facturas_pagadas', [])
        for p in facturas_pagadas:
            uuid_rel = p.get('uuid_relacionado')
            monto_pagado = p.get('monto_pagado')
            
            # Find the internal factura_id based on uuid_cfdi
            cur.execute("SELECT id FROM diesel.facturas WHERE uuid_cfdi = %s", (uuid_rel,))
            fac_row = cur.fetchone()
            
            if fac_row:
                fac_id = fac_row[0]
                cur.execute("""
                    INSERT INTO diesel.pagos_facturas (complemento_id, factura_id, monto_aplicado)
                    VALUES (%s, %s, %s)
                """, (comp_id, fac_id, monto_pagado))
                
                # Update status of factura
                cur.execute("UPDATE diesel.facturas SET estatus_pago = 'PAGADO' WHERE id = %s", (fac_id,))
                
        db.commit()
        db.close()
        return jsonify({'success': True})
    except Exception as e:
        print("ERROR Guardando Complemento:", e)
        return jsonify({'success': False, 'error': str(e)})
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/diesel/consumo', methods=['POST'])
def api_post_diesel():
    try:
        db = get_db()
        data = request.form
        fotos = request.files.getlist('foto_evidencia')
        
        foto_blob = None
        if fotos and len(fotos) > 0 and fotos[0].filename != '':
            if len(fotos) == 1:
                foto_blob = fotos[0].read()
            else:
                import io, zipfile
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for i, f in enumerate(fotos):
                        if f.filename:
                            zip_file.writestr(f.filename, f.read())
                foto_blob = zip_buffer.getvalue()
        # Encontrar descripcion de equipo
        cur = db.cursor(cursor_factory=DictCursor)
        cur.execute('SELECT descripcion FROM catalogos.equipos WHERE numero_economico=%s', (data.get('equipo_economico'),))
        eq_row = cur.fetchone()
        equipo_desc = eq_row['descripcion'] if eq_row else ''
        
        # Generar Folio: CODIGO_OP - CODIGO_OBRA - SEMANA - CONSECUTIVO
        cur = db.cursor(cursor_factory=DictCursor)
        cur.execute('SELECT codigo FROM catalogos.obras WHERE nombre=%s', (data.get('obra_destino'),))
        obra_row = cur.fetchone()
        obra_codigo = obra_row['codigo'] if obra_row else 'XX'
        semana = str(data.get('semana', '')).replace('Semana ', '').replace('Semana', '').strip().replace('Semana ', '').replace('Semana', '').strip()
        tipo_op = data.get('tipo_movimiento_codigo', 'CMQ')
        tipo_movimiento_nombre = data.get('tipo_movimiento_nombre', 'CARGA MAQUINARIA')
        
        # Consecutivo: obtener el número más alto de esa semana sin importar la obra
        # Ejemplo de folio: CMQ-MP-28-301
        cur.execute("SELECT folio_conciliacion FROM diesel.consumos WHERE folio_conciliacion LIKE %s", (f"{tipo_op}-%-{semana}-%%",))
        folios = cur.fetchall()
        max_cons = 0
        for f in folios:
            parts = f['folio_conciliacion'].split('-')
            if len(parts) >= 4:
                try:
                    num = int(parts[-1])
                    if num > max_cons: max_cons = num
                except: pass
        
        consecutivo = max_cons + 1
        folio = f"{tipo_op}-{obra_codigo}-{semana}-{consecutivo:03d}"

        litros = float(data.get('litros', 0))
        costo = float(data.get('costo_por_litro', 0))
        importe = litros * costo
        operador_val = data.get('operador')
        if not operador_val: operador_val = 'Sin Registro'
        
        fecha_val = data.get('fecha')
        if not fecha_val:
            import datetime
            fecha_val = datetime.date.today().strftime('%Y-%m-%d')
        
        origen_raw = data.get('origen') or 'Marimba M-01'
        medio_sum = data.get('medio_suministro') or ('CAMION_3_5' if ('3.5' in origen_raw or 'camion' in origen_raw.lower() or '3 1/2' in origen_raw) else 'MARIMBA')
        conductor_dist = data.get('conductor_distribuidor') or data.get('responsable')
        unidad_rep = data.get('unidad_reparto') or origen_raw

        cur.execute('''INSERT INTO diesel.consumos 
            (folio_conciliacion, fecha, semana, origen, tipo_movimiento, obra_destino, equipo_economico, equipo, litros, costo_por_litro, importe_total, responsable, operador, foto_evidencia, usuario_captura, tipo_captura, medio_suministro, conductor_distribuidor, unidad_reparto)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'MARIMBA', %s, %s, %s)''', (
            folio, fecha_val, str(data.get('semana', '')).replace('Semana ', '').replace('Semana', '').strip(), data.get('origen'), tipo_movimiento_nombre, data.get('obra_destino'), data.get('equipo_economico'), equipo_desc, litros, costo, importe, data.get('responsable'), operador_val, foto_blob, data.get('responsable'),
            medio_sum, conductor_dist, unidad_rep
        ))
        db.commit()
        db.close()
        return jsonify({'success': True, 'folio': folio, 'message': f'Consumo de {litros} Lts guardado exitosamente.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/diesel/operador_consumo', methods=['POST'])
def api_post_diesel_operador():
    try:
        db = get_db()
        data = request.form
        fotos = request.files.getlist('foto_evidencia')
        
        foto_blob = None
        if fotos and len(fotos) > 0 and fotos[0].filename != '':
            if len(fotos) == 1:
                foto_blob = fotos[0].read()
            else:
                import io, zipfile
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for i, f in enumerate(fotos):
                        if f.filename:
                            zip_file.writestr(f.filename, f.read())
                foto_blob = zip_buffer.getvalue()

        cur = db.cursor(cursor_factory=DictCursor)
        
        # Resolver equipo
        eq_eco_raw = (data.get('equipo_economico') or '').strip()
        if ' - ' in eq_eco_raw:
            eq_eco = eq_eco_raw.split(' - ')[0].strip()
        else:
            eq_eco = eq_eco_raw
            
        cur.execute('SELECT descripcion FROM catalogos.equipos WHERE numero_economico=%s', (eq_eco,))
        eq_row = cur.fetchone()
        equipo_desc = eq_row['descripcion'] if eq_row else (data.get('equipo_nombre') or eq_eco)
        
        # Resolver obra y código
        obra_dest = (data.get('obra_destino') or '').strip()
        cur.execute('SELECT codigo FROM catalogos.obras WHERE nombre=%s', (obra_dest,))
        obra_row = cur.fetchone()
        obra_codigo = obra_row['codigo'] if obra_row else 'XX'
        
        semana = str(data.get('semana', '')).replace('Semana ', '').replace('Semana', '').strip()
        if not semana:
            semana = str(get_current_week())
            
        # Folio: OPR-CODIGO_OBRA-SEMANA-CONSECUTIVO
        tipo_op = 'OPR'
        cur.execute("SELECT folio_conciliacion FROM diesel.consumos WHERE folio_conciliacion LIKE %s", (f"{tipo_op}-%-{semana}-%%",))
        folios = cur.fetchall()
        max_cons = 0
        for f in folios:
            parts = f['folio_conciliacion'].split('-')
            if len(parts) >= 4:
                try:
                    num = int(parts[-1])
                    if num > max_cons: max_cons = num
                except: pass
        
        consecutivo = max_cons + 1
        folio = f"{tipo_op}-{obra_codigo}-{semana}-{consecutivo:03d}"
        
        litros = float(data.get('litros', 0))
        costo = float(data.get('costo_por_litro', 27.0) or 27.0)
        importe = round(litros * costo, 2)
        
        resp_maquinaria = (data.get('responsable_maquinaria') or data.get('operador') or '').strip() or 'Sin Registro'
        ing_responsable = (data.get('responsable') or '').strip()
        
        horometro_val = data.get('horometro_inicial')
        horometro_inicial = None
        if horometro_val and str(horometro_val).strip() != '':
            try:
                horometro_inicial = float(str(horometro_val).replace(',', '').strip())
            except:
                horometro_inicial = None
                
        fecha_val = data.get('fecha')
        if not fecha_val or not fecha_val.strip():
            import datetime
            fecha_val = datetime.date.today().strftime('%Y-%m-%d')
            
        obs_val = (data.get('observaciones') or '').strip()
        if horometro_inicial is not None and f"Horómetro: {horometro_inicial}" not in obs_val:
            obs_val = f"[Horómetro Inicial: {horometro_inicial} hrs] {obs_val}".strip()
            
        origen_val = data.get('origen', 'Marimba M-01')
        medio_sum = data.get('medio_suministro') or ('CAMION_3_5' if ('3.5' in origen_val or 'camion' in origen_val.lower() or '3 1/2' in origen_val) else 'MARIMBA')
        conductor_dist = data.get('conductor_distribuidor') or ing_responsable
        unidad_rep = data.get('unidad_reparto') or origen_val
        
        # Registrar operador en catálogo si es nuevo
        if resp_maquinaria and resp_maquinaria != 'Sin Registro':
            try:
                cur.execute("SELECT 1 FROM catalogos.operadores WHERE UPPER(TRIM(nombre)) = UPPER(TRIM(%s))", (resp_maquinaria,))
                if not cur.fetchone():
                    cur.execute("INSERT INTO catalogos.operadores (nombre) VALUES (%s)", (resp_maquinaria.strip(),))
            except Exception: pass
            
        cur.execute('''
            INSERT INTO diesel.consumos 
            (folio_conciliacion, fecha, semana, origen, tipo_movimiento, obra_destino, 
             equipo_economico, equipo, litros, costo_por_litro, importe_total, 
             responsable, operador, responsable_maquinaria, horometro_inicial, 
             tipo_captura, foto_evidencia, usuario_captura, observaciones, estatus_revision,
             medio_suministro, conductor_distribuidor, unidad_reparto)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'OPERADOR', %s, %s, %s, 'PENDIENTE', %s, %s, %s)
        ''', (
            folio, fecha_val, semana, origen_val, 'CARGA OPERADOR', obra_dest,
            eq_eco, equipo_desc, litros, costo, importe,
            ing_responsable, resp_maquinaria, resp_maquinaria, horometro_inicial,
            foto_blob, resp_maquinaria, obs_val,
            medio_sum, conductor_dist, unidad_rep
        ))
        
        db.commit()
        db.close()
        return jsonify({
            'success': True,
            'folio': folio,
            'message': f'¡Carga de operador guardada exitosamente! Folio: {folio} ({litros} Lts)'
        })
    except Exception as e:
        if 'db' in locals() and db:
            try: db.rollback(); db.close()
            except: pass
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/dashboard/resumen', methods=['GET'])
def api_dashboard_resumen():
    try:
        db = get_db()
        cur = db.cursor(cursor_factory=DictCursor)
        cur.execute("SELECT COALESCE(SUM(litros),0) FROM diesel.consumos WHERE origen != 'FACTURA'")
        diesel_lts = cur.fetchone()[0]
        cur.execute("SELECT COALESCE(SUM(importe_total),0) FROM diesel.consumos WHERE origen != 'FACTURA'")
        diesel_imp = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM diesel.consumos WHERE origen != 'FACTURA'")
        diesel_reg = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM diesel.consumos WHERE origen = 'FACTURA'")
        fac_total = cur.fetchone()[0]
        cur.execute("SELECT COALESCE(SUM(importe_total),0) FROM diesel.consumos WHERE origen = 'FACTURA'")
        fac_imp = cur.fetchone()[0]
        db.close()
        return jsonify({
            'success': True,
            'diesel': {'litros_consumidos': diesel_lts, 'importe_consumido': diesel_imp, 'registros': diesel_reg},
            'facturas': {'total': fac_total, 'importe_total': fac_imp}
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/diesel/dashboard', methods=['GET'])
def api_diesel_dashboard():
    try:
        obra = request.args.get('obra', '')
        movimiento = request.args.get('movimiento', '')
        
        query = '''
        SELECT 
            REPLACE(semana, 'Semana ', '') as sem_num,
            SUM(CASE WHEN origen != 'FACTURA' THEN litros ELSE 0 END) as litros_consumidos,
            SUM(CASE WHEN origen != 'FACTURA' THEN importe_total ELSE 0 END) as importe_consumido,
            SUM(CASE WHEN origen = 'FACTURA' THEN litros ELSE 0 END) as litros_facturados,
            SUM(CASE WHEN origen = 'FACTURA' THEN importe_total ELSE 0 END) as importe_facturado
        FROM diesel.consumos
        WHERE 1=1
        '''
        params = []
        if obra:
            query += " AND obra_destino = ?"
            params.append(obra)
        if movimiento:
            query += " AND tipo_movimiento = ?"
            params.append(movimiento)
            
        query += " GROUP BY sem_num ORDER BY CAST(sem_num as INTEGER) DESC"
        
        db = get_db()
        cur = db.cursor(cursor_factory=DictCursor)
        cur.execute(query, params)
        rows = cur.fetchall()
        
        tot_l_cons = sum([r['litros_consumidos'] or 0 for r in rows])
        tot_i_cons = sum([r['importe_consumido'] or 0 for r in rows])
        tot_l_fact = sum([r['litros_facturados'] or 0 for r in rows])
        tot_i_fact = sum([r['importe_facturado'] or 0 for r in rows])
        
        kpis = {
            'litros_consumidos': tot_l_cons,
            'importe_consumido': tot_i_cons,
            'litros_facturados': tot_l_fact,
            'importe_facturado': tot_i_fact
        }
        
        table = []
        for r in rows:
            table.append({
                'semana': f"Semana {r['sem_num']}",
                'litros_consumidos': r['litros_consumidos'] or 0,
                'importe_consumido': r['importe_consumido'] or 0,
                'litros_facturados': r['litros_facturados'] or 0,
                'importe_facturado': r['importe_facturado'] or 0
            })
            
        db.close()
        return jsonify({'success': True, 'kpis': kpis, 'table': table})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/diesel/factura', methods=['POST'])
def api_post_diesel_factura():
    try:
        db = get_db()
        data = request.form
        pdf = request.files.get('archivo_pdf')
        xml = request.files.get('archivo_xml')
        pdf_blob = pdf.read() if pdf else None
        xml_blob = xml.read() if xml else None
        folio_fiscal = data.get('folio_fiscal', '')
        litros = float(data.get('litros_facturados', 0))
        importe = float(data.get('importe_total', 0))
        cur = db.cursor(cursor_factory=DictCursor)
        cur.execute('''INSERT INTO diesel.facturas 
            (uuid_cfdi, folio_factura, fecha_factura, semana, proveedor, punto_de_carga, litros_facturados, importe_total, archivo_pdf, archivo_xml)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''', (
            folio_fiscal, folio_fiscal, data.get('fecha_factura'), str(data.get('semana', '')).replace('Semana ', '').replace('Semana', '').strip(), data.get('proveedor', 'MANUAL'), data.get('estacion', ''), litros, importe, pdf_blob, xml_blob
        ))
        db.commit()
        db.close()
        return jsonify({'success': True, 'message': 'Factura guardada exitosamente.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ==============================================================================
# CAPTURA MASIVA Y CONCILIACIÓN DE GASOLINA DESDE EXCEL (OPTIMIZADO O(1) + BULK)
# ==============================================================================
from psycopg2.extras import execute_values

def parse_gasolina_excel_data(file_stream_or_path, db):
    import openpyxl, datetime
    wb = openpyxl.load_workbook(file_stream_or_path, data_only=True)
    all_rows = []
    semanas_set = set()
    
    # 1. OPTIMIZACIÓN ISO 9001: Pre-cargar consumos existentes en 1 SÓLA CONSULTA (Evita N+1 Queries)
    existentes_tickets = set()
    existentes_claves = set()  # Key: "FECHA|PLACA"
    
    if db:
        try:
            cur = db.cursor(cursor_factory=DictCursor)
            cur.execute("""
                SELECT 
                    LOWER(TRIM(COALESCE(folio_conciliacion, ''))) as ticket,
                    LOWER(TRIM(COALESCE(observaciones, ''))) as obs,
                    fecha::text,
                    LOWER(TRIM(COALESCE(placa, ''))) as placa
                FROM gasolina.consumos
            """)
            db_rows = cur.fetchall()
            cur.close()
            
            for row in db_rows:
                t = row['ticket']
                if t: existentes_tickets.add(t)
                if 'ticket #' in row['obs']:
                    t_obs = row['obs'].split('ticket #')[-1].strip().lower()
                    if t_obs: existentes_tickets.add(t_obs)
                
                f = row['fecha']
                p = row['placa']
                if f and p:
                    existentes_claves.add(f"{f}|{p}")
        except Exception as e:
            print("Warning pre-cargando duplicados BD:", e)

    # 2. Procesamiento optimizado del Excel
    for sheet in wb.sheetnames:
        ws = wb[sheet]
        hdr_map = {}
        header_row_idx = None
        
        for r in range(1, min(15, ws.max_row + 1)):
            row_vals = [str(ws.cell(r, c).value or '').strip().upper() for c in range(1, ws.max_column + 1)]
            if any('TICKET' in v or 'FOLIO' in v for v in row_vals) and any('FECHA' in v for v in row_vals):
                header_row_idx = r
                for c_idx, val in enumerate(row_vals, 1):
                    if 'TICKET' in val or 'FOLIO' in val: hdr_map['ticket'] = c_idx
                    elif 'FECHA' in val: hdr_map['fecha'] = c_idx
                    elif 'UNID' in val or 'PLACA' in val or 'VEHICULO' in val: hdr_map['placa'] = c_idx
                    elif 'CONDUCTOR' in val or 'RESPONSABLE' in val or 'CHOFER' in val: hdr_map['conductor'] = c_idx
                    elif 'OBRA' in val: hdr_map['obra'] = c_idx
                    elif 'LTS' in val or 'LITROS' in val: hdr_map['litros'] = c_idx
                    elif 'PRECIO' in val: hdr_map['precio'] = c_idx
                    elif 'IMPORTE' in val or 'TOTAL' in val or 'MONTO' in val: hdr_map['importe'] = c_idx
                break
            
        if not header_row_idx or 'ticket' not in hdr_map or 'fecha' not in hdr_map:
            header_row_idx = 4
            hdr_map = {'ticket': 2, 'fecha': 3, 'placa': 4, 'conductor': 6, 'obra': 7, 'litros': 8, 'precio': 9, 'importe': 10}

        for r in range(header_row_idx + 1, ws.max_row + 1):
            ticket_val = ws.cell(r, hdr_map.get('ticket', 2)).value
            fecha_val = ws.cell(r, hdr_map.get('fecha', 3)).value
            if not ticket_val or not fecha_val:
                continue
                
            ticket_str = str(ticket_val).strip()
            if not ticket_str or ticket_str.upper() in ('TICKET', 'TOTAL', 'TOTALES', 'NONE', 'NAN'):
                continue
                
            placa_val = ws.cell(r, hdr_map.get('placa', 4)).value
            conductor_val = ws.cell(r, hdr_map.get('conductor', 6)).value
            obra_val = ws.cell(r, hdr_map.get('obra', 7)).value
            litros_val = ws.cell(r, hdr_map.get('litros', 8)).value
            precio_val = ws.cell(r, hdr_map.get('precio', 9)).value
            importe_val = ws.cell(r, hdr_map.get('importe', 10)).value
            
            dt_obj = None
            if isinstance(fecha_val, (datetime.datetime, datetime.date)):
                dt_obj = fecha_val
                fecha_str = fecha_val.strftime('%Y-%m-%d')
            else:
                fecha_str = str(fecha_val)[:10].strip()
                try: dt_obj = datetime.datetime.strptime(fecha_str, '%Y-%m-%d')
                except: dt_obj = None
                
            if dt_obj:
                week_num = dt_obj.isocalendar()[1]
                semana_str = f"Semana {week_num}"
            else:
                semana_str = "Semana N/A"
                
            semanas_set.add(semana_str)
            
            try: lts = float(litros_val or 0)
            except: lts = 0.0
            try: prc = float(precio_val or 0)
            except: prc = 0.0
            try: imp = float(importe_val or 0)
            except: imp = 0.0
            
            if lts == 0 and imp > 0 and prc > 0:
                lts = round(imp / prc, 3)
            elif imp == 0 and lts > 0 and prc > 0:
                imp = round(lts * prc, 2)
                
            placa = str(placa_val or '').strip().upper()
            conductor = str(conductor_val or '').strip().upper()
            obra = str(obra_val or '').strip().upper()
            
            # 3. VERIFICACIÓN DE DUPLICADO EN MEMORIA O(1)
            t_low = ticket_str.lower()
            p_low = placa.lower()
            clave_fp = f"{fecha_str}|{p_low}"
            
            es_duplicado = (t_low in existentes_tickets) or (clave_fp in existentes_claves and p_low not in ('', 'S/P', 'SIN PLACA'))
            estatus = 'DUPLICADO' if es_duplicado else 'NUEVO'
            
            all_rows.append({
                'row_id': len(all_rows) + 1,
                'sheet': sheet,
                'ticket': ticket_str,
                'fecha': fecha_str,
                'semana': semana_str,
                'placa': placa if placa else 'S/P',
                'conductor': conductor,
                'obra': obra if obra else 'GENERAL / SIN OBRA',
                'litros': round(lts, 2),
                'precio': round(prc, 2) if prc > 0 else 23.90,
                'importe': round(imp, 2),
                'estatus': estatus,
                'match_info': "Registrado previamente en BD" if es_duplicado else None
            })
            
    wb.close()
    return all_rows, sorted(list(semanas_set))


@app.route('/api/gasolina/procesar_excel_masivo', methods=['POST'])
def api_gasolina_procesar_excel_masivo():
    try:
        file = request.files.get('archivo_excel')
        if not file:
            return jsonify({'success': False, 'error': 'No se proporcionó ningún archivo Excel.'}), 400
            
        db = get_db()
        cargas, semanas = parse_gasolina_excel_data(file, db)
        db.close()
        
        tot_litros = sum([c['litros'] for c in cargas])
        tot_importe = sum([c['importe'] for c in cargas])
        cnt_duplicados = sum([1 for c in cargas if c['estatus'] == 'DUPLICADO'])
        cnt_nuevos = sum([1 for c in cargas if c['estatus'] == 'NUEVO'])
        
        return jsonify({
            'success': True,
            'semanas': semanas,
            'totales': {
                'total_cargas': len(cargas),
                'total_litros': round(tot_litros, 2),
                'total_importe': round(tot_importe, 2),
                'cnt_duplicados': cnt_duplicados,
                'cnt_nuevos': cnt_nuevos
            },
            'cargas': cargas
        })
    except Exception as e:
        print("ERROR PROCESANDO EXCEL MASIVO GASOLINA:", e)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/gasolina/guardar_captura_masiva', methods=['POST'])
def api_gasolina_guardar_captura_masiva():
    try:
        data = request.get_json() or {}
        cargas = data.get('cargas', [])
        
        if not cargas:
            return jsonify({'success': False, 'error': 'No se enviaron cargas para guardar'}), 400
            
        db = get_db()
        cur = db.cursor()
        
        records_to_insert = []
        for c in cargas:
            ticket = str(c.get('ticket', '')).strip()
            fecha = str(c.get('fecha', '')).strip()
            semana = str(c.get('semana', '')).replace('Semana ', '').strip()
            placa = str(c.get('placa', '')).strip().upper()
            conductor = str(c.get('conductor', '')).strip().upper()
            obra = str(c.get('obra', '')).strip().upper() or 'GENERAL / SIN OBRA'
            litros = float(c.get('litros', 0) or 0)
            precio = float(c.get('precio', 23.90) or 23.90)
            importe = float(c.get('importe', 0) or 0)
            
            if importe == 0 and litros > 0:
                importe = round(litros * precio, 2)
                
            vehiculo_label = f"{placa} - {conductor}" if placa else conductor
            obs_label = f"Captura Masiva Excel Levet Ticket #{ticket}"
            
            records_to_insert.append((
                fecha, semana, conductor, vehiculo_label, placa, obra,
                litros, precio, importe, 'LEVET', ticket, 'APROBADO',
                'CAPTURA_MASIVA_EXCEL', obs_label
            ))
        
        insert_query = """
            INSERT INTO gasolina.consumos (
                fecha, semana, conductor, vehiculo, placa, obra_destino,
                litros, costo_por_litro, importe_total, gasolineria,
                folio_conciliacion, estatus_revision, origen, observaciones
            ) VALUES %s
        """
        execute_values(cur, insert_query, records_to_insert)
        
        db.commit()
        db.close()
        
        return jsonify({
            'success': True,
            'message': f"¡Se guardaron exitosamente {len(records_to_insert)} cargas en la base de datos de Gasolina!",
            'inserted_count': len(records_to_insert)
        })
    except Exception as e:
        print("ERROR GUARDANDO CARGAS MASIVAS GASOLINA:", e)
        return jsonify({'success': False, 'error': str(e)}), 500

# ─────────────────────────────────────────────────────────────
# MÓDULO TRANSPORTES (TANQUE PEGASO) - APIS DE CAPTURA
# ─────────────────────────────────────────────────────────────

@app.route('/api/transportes/diesel/consumo', methods=['POST'])
def api_post_transportes_diesel():
    try:
        db = get_db()
        data = request.form
        fotos = request.files.getlist('foto_evidencia')
        
        foto_blob = None
        if fotos and len(fotos) > 0 and fotos[0].filename != '':
            if len(fotos) == 1:
                foto_blob = fotos[0].read()
            else:
                import io, zipfile
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for i, f in enumerate(fotos):
                        if f.filename:
                            zip_file.writestr(f.filename, f.read())
                foto_blob = zip_buffer.getvalue()
                
        cur = db.cursor(cursor_factory=DictCursor)
        # Buscar descripción de equipo de transporte
        equipo_eco = data.get('equipo_economico', '').strip()
        cur.execute('SELECT descripcion FROM transportes.equipos WHERE numero_economico=%s', (equipo_eco,))
        eq_row = cur.fetchone()
        equipo_desc = eq_row['descripcion'] if eq_row else (data.get('equipo') or equipo_eco)
        
        # Obra destino y código para el folio
        obra_destino = data.get('obra_destino', '').strip()
        cur.execute('SELECT codigo FROM catalogos.obras WHERE nombre=%s', (obra_destino,))
        obra_row = cur.fetchone()
        obra_codigo = obra_row['codigo'] if obra_row else 'TRP'
        
        semana = str(data.get('semana', '')).replace('Semana ', '').replace('Semana', '').strip()
        if not semana:
            semana = str(get_current_week())
            
        # Consecutivo para Transportes: TRP-D-{obra_codigo}-{semana}-{consecutivo:03d}
        cur.execute("SELECT folio_conciliacion FROM transportes.consumos_diesel WHERE folio_conciliacion LIKE %s", (f"TRP-D-%-{semana}-%%",))
        folios = cur.fetchall()
        max_cons = 0
        for f in folios:
            parts = f['folio_conciliacion'].split('-')
            if len(parts) >= 4:
                try:
                    num = int(parts[-1])
                    if num > max_cons: max_cons = num
                except: pass
        consecutivo = max_cons + 1
        folio = f"TRP-D-{obra_codigo}-{semana}-{consecutivo:03d}"
        
        litros = float(data.get('litros', 0))
        costo = float(data.get('costo_por_litro', 27.0))
        importe = round(litros * costo, 2)
        
        fecha_val = data.get('fecha')
        if not fecha_val:
            import datetime
            fecha_val = datetime.date.today().strftime('%Y-%m-%d')
            
        responsable_unidad = data.get('responsable_unidad') or data.get('responsable') or 'Sin Registro'
        origen = data.get('origen') or 'Tanque Pegaso'
        odometro = float(data.get('odometro_km') or 0)
        horometro = float(data.get('horometro') or 0)
        observaciones = data.get('observaciones') or ''
        
        cur.execute('''
            INSERT INTO transportes.consumos_diesel 
            (folio_conciliacion, fecha, semana, origen, obra_destino, responsable_unidad, equipo_economico, equipo, litros, costo_por_litro, importe_total, odometro_km, horometro, observaciones, foto_evidencia, usuario_captura, estatus_revision)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'PENDIENTE')
        ''', (folio, fecha_val, semana, origen, obra_destino, responsable_unidad, equipo_eco, equipo_desc, litros, costo, importe, odometro, horometro, observaciones, foto_blob, responsable_unidad))
        db.commit()
        db.close()
        return jsonify({'success': True, 'folio': folio, 'message': f'¡Carga de Transportes registrada con éxito! Folio: {folio}'})
    except Exception as e:
        print("ERROR EN CONSUMO TRANSPORTES DIESEL:", e)
        if 'db' in locals() and db:
            db.rollback(); db.close()
        return jsonify({'success': False, 'error': str(e), 'message': f'Error al guardar consumo de transportes: {str(e)}'})

@app.route('/api/transportes/diesel/extraer_bitacora_excel', methods=['POST'])
def api_captura_transportes_extraer_bitacora():
    from motor_transportes import extraer_bitacora_transportes_excel, generar_propuesta_autorizaciones
    if 'archivo' not in request.files:
        return jsonify({'success': False, 'error': 'No se recibió ningún archivo Excel.'}), 400
    file = request.files['archivo']
    if not file.filename:
        return jsonify({'success': False, 'error': 'Nombre de archivo vacío.'}), 400
    
    try:
        content = file.read()
        res = extraer_bitacora_transportes_excel(content, filename=file.filename)
        if not res.get('hojas'):
            return jsonify({'success': False, 'error': 'No se encontraron hojas válidas de bitácora diésel en el archivo.'}), 400
        
        db = get_db()
        try:
            for h in res['hojas']:
                h['propuesta_autorizaciones'] = generar_propuesta_autorizaciones(db, h['balance']['semana'], h['resumen_vehiculos'])
        finally:
            db.close()
            
        return jsonify({'success': True, 'data': res})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/transportes/diesel/guardar_bitacora_excel', methods=['POST'])
def api_captura_transportes_guardar_bitacora():
    from motor_transportes import inyectar_bitacora_transportes_bd
    data = request.get_json(silent=True) or {}
    hoja_data = data.get('hoja_data')
    if not hoja_data:
        return jsonify({'success': False, 'error': 'Faltan datos de la hoja a guardar.'}), 400
    
    db = get_db()
    try:
        res = inyectar_bitacora_transportes_bd(db, hoja_data, usuario='CAPTURA_WEB')
        return jsonify({'success': True, 'resultado': res})
    except Exception as e:
        if db: db.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if db: db.close()

@app.route('/api/transportes/diesel/balance_semanal', methods=['GET'])
def api_captura_transportes_balance_semanal():
    semana = request.args.get('semana', '').strip().replace('Semana ', '').replace('Semana', '').strip()
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=DictCursor)
        if semana:
            cur.execute("""
                SELECT * FROM transportes.balance_tanque_semanal 
                WHERE semana = %s 
                ORDER BY id DESC LIMIT 1;
            """, (semana,))
        else:
            cur.execute("""
                SELECT * FROM transportes.balance_tanque_semanal 
                ORDER BY id DESC LIMIT 1;
            """)
        row = cur.fetchone()
        if not row:
            return jsonify({'success': False, 'error': f'No hay balance registrado para la semana {semana or "reciente"}.'})
        
        d = dict(row)
        for k in ['created_at', 'updated_at']:
            if k in d: d[k] = str(d[k])
        for k in ['diesel_inicial', 'diesel_final', 'cuentalitros_inicial', 'cuentalitros_final', 'litros_tanque', 'litros_despacho_directo', 'litros_totales', 'costo_por_litro', 'costo_total']:
            if k in d and d[k] is not None: d[k] = float(d[k])
        if isinstance(d.get('detalles_vehiculos'), str):
            d['detalles_vehiculos'] = json.loads(d['detalles_vehiculos'])
        if isinstance(d.get('propuesta_autorizaciones'), str):
            d['propuesta_autorizaciones'] = json.loads(d['propuesta_autorizaciones'])
            
        return jsonify({'success': True, 'balance': d})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/transportes/gasolina/consumo', methods=['POST'])
def api_post_transportes_gasolina():
    try:
        db = get_db()
        data = request.form
        fotos = request.files.getlist('foto_evidencia')
        
        foto_blob = None
        if fotos and len(fotos) > 0 and fotos[0].filename != '':
            if len(fotos) == 1:
                foto_blob = fotos[0].read()
            else:
                import io, zipfile
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for i, f in enumerate(fotos):
                        if f.filename:
                            zip_file.writestr(f.filename, f.read())
                foto_blob = zip_buffer.getvalue()
                
        cur = db.cursor(cursor_factory=DictCursor)
        semana = str(data.get('semana', '')).replace('Semana ', '').replace('Semana', '').strip()
        if not semana:
            semana = str(get_current_week())
            
        cur.execute("SELECT folio_conciliacion FROM transportes.consumos_gasolina WHERE folio_conciliacion LIKE %s", (f"TRP-G-%-{semana}-%%",))
        folios = cur.fetchall()
        max_cons = 0
        for f in folios:
            parts = f['folio_conciliacion'].split('-')
            if len(parts) >= 4:
                try:
                    num = int(parts[-1])
                    if num > max_cons: max_cons = num
                except: pass
        consecutivo = max_cons + 1
        folio = f"TRP-G-PEG-{semana}-{consecutivo:03d}"
        
        litros = float(data.get('litros', 0))
        costo = float(data.get('costo_por_litro', 23.90))
        importe = round(litros * costo, 2)
        
        fecha_val = data.get('fecha') or datetime.date.today().strftime('%Y-%m-%d')
        gasolineria = data.get('gasolineria') or 'LEVET'
        obra_destino = data.get('obra_destino') or 'PATIO PEGASO'
        responsable_unidad = data.get('responsable_unidad') or data.get('responsable') or 'Sin Registro'
        vehiculo = data.get('vehiculo') or data.get('equipo') or ''
        placa = data.get('placa') or 'S/P'
        km = float(data.get('kilometraje') or 0)
        observaciones = data.get('observaciones') or ''
        
        cur.execute('''
            INSERT INTO transportes.consumos_gasolina
            (folio_conciliacion, fecha, semana, gasolineria, obra_destino, responsable_unidad, vehiculo, placa, litros, costo_por_litro, importe_total, kilometraje, observaciones, foto_evidencia, usuario_captura, estatus_revision)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'PENDIENTE')
        ''', (folio, fecha_val, semana, gasolineria, obra_destino, responsable_unidad, vehiculo, placa, litros, costo, importe, km, observaciones, foto_blob, responsable_unidad))
        db.commit()
        db.close()
        return jsonify({'success': True, 'folio': folio, 'message': f'¡Carga de Gasolina para Transportes registrada con éxito! Folio: {folio}'})
    except Exception as e:
        print("ERROR EN CONSUMO TRANSPORTES GASOLINA:", e)
        if 'db' in locals() and db:
            db.rollback(); db.close()
        return jsonify({'success': False, 'error': str(e), 'message': f'Error al guardar gasolina de transportes: {str(e)}'})

@app.route('/api/transportes/catalogos', methods=['GET'])
def api_get_transportes_catalogos():
    db = get_db()
    cur = db.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT numero_economico, descripcion, tipo_equipo, placas, responsable_default FROM transportes.equipos WHERE activo = TRUE ORDER BY numero_economico")
    equipos = [dict(r) for r in cur.fetchall()]
    cur.execute("SELECT nombre, puesto FROM transportes.operadores WHERE activo = TRUE ORDER BY nombre")
    operadores = [dict(r) for r in cur.fetchall()]
    db.close()
    return jsonify({'equipos': equipos, 'operadores': operadores})

# ==========================================
# MÓDULO N8N & CONCILIACIÓN DIÉSEL AUTOMATIZADA
# ==========================================
import requests

N8N_CONCILIACION_WEBHOOK_URL = os.environ.get('N8N_DIESEL_WEBHOOK', 'http://localhost:5678/webhook/fenix-conciliacion-diesel')

@app.route('/api/diesel/facturas_pendientes_clasificar', methods=['GET'])
def api_diesel_facturas_pendientes_clasificar():
    try:
        db = get_db()
        cur = db.cursor(cursor_factory=DictCursor)
        cur.execute("""
            SELECT id, folio_conciliacion, folio_factura, fecha_factura, semana,
                   proveedor, litros_facturados, importe_total, uuid_cfdi,
                   (archivo_pdf IS NOT NULL) as tiene_pdf,
                   (archivo_xml IS NOT NULL) as tiene_xml,
                   obra_destino, estatus_revision
            FROM diesel.facturas
            WHERE obra_destino IS NULL 
               OR obra_destino = '' 
               OR estatus_revision = 'PENDIENTE_OBRA'
            ORDER BY id DESC
            LIMIT 50
        """)
        rows = [dict(r) for r in cur.fetchall()]
        for r in rows:
            if r.get('litros_facturados') is not None:
                r['litros_facturados'] = float(r['litros_facturados'])
            if r.get('importe_total') is not None:
                r['importe_total'] = float(r['importe_total'])
        db.close()
        return jsonify({'success': True, 'facturas': rows, 'total': len(rows)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'facturas': []})

@app.route('/api/diesel/asignar_obra_factura', methods=['POST'])
def api_diesel_asignar_obra_factura():
    try:
        data = request.json or request.form
        factura_id = data.get('factura_id')
        obra_destino = normalizar_obra_nombre(data.get('obra_destino'))
        semana = data.get('semana')

        if not factura_id or not obra_destino:
            return jsonify({'success': False, 'message': 'Se requiere factura_id y obra_destino'}), 400

        db = get_db()
        cur = db.cursor(cursor_factory=DictCursor)
        cur.execute("""
            UPDATE diesel.facturas
            SET obra_destino = %s,
                estatus_revision = 'ASIGNADA_OBRA'
            WHERE id = %s
            RETURNING id, folio_factura, semana, proveedor, litros_facturados, importe_total, obra_destino
        """, (obra_destino, factura_id))
        factura_actualizada = cur.fetchone()
        db.commit()
        db.close()

        if not factura_actualizada:
            return jsonify({'success': False, 'message': f'Factura con ID {factura_id} no encontrada'}), 404

        # Disparar webhook a n8n en background si está activo
        try:
            requests.post(N8N_CONCILIACION_WEBHOOK_URL, json={
                'semana': factura_actualizada['semana'],
                'obra_destino': obra_destino,
                'factura_id': factura_id,
                'evento': 'OBRA_ASIGNADA_MANUAL'
            }, timeout=1.5)
        except Exception:
            pass # No bloquea la UI si n8n no está corriendo

        return jsonify({
            'success': True,
            'message': f'Factura {factura_actualizada["folio_factura"]} asignada exitosamente a "{obra_destino}".',
            'factura': dict(factura_actualizada)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/diesel/balance_conciliacion_live', methods=['GET', 'POST'])
def api_diesel_balance_conciliacion_live():
    try:
        data = request.args if request.method == 'GET' else (request.json or request.form)
        semana = str(data.get('semana', '')).replace('Semana ', '').replace('Semana', '').strip()
        obra = data.get('obra_destino') or data.get('obra') or ''
        obra = normalizar_obra_nombre(obra) if obra and obra != 'TODAS' else obra

        if not semana:
            semana = str(get_current_week())

        db = get_db()
        cur = db.cursor(cursor_factory=DictCursor)

        # 1. Suma de Facturas de la semana / obra
        query_fac = """
            SELECT COALESCE(SUM(litros_facturados), 0) as total_litros,
                   COALESCE(SUM(importe_total), 0) as total_importe,
                   COUNT(*) as total_count
            FROM diesel.facturas
            WHERE semana = %s
        """
        params_fac = [semana]
        if obra and obra != 'TODAS':
            query_fac += " AND obra_destino = %s"
            params_fac.append(obra)

        cur.execute(query_fac, params_fac)
        fac_summary = cur.fetchone()

        # Detalle de facturas
        query_fac_det = """
            SELECT id, folio_factura, proveedor, litros_facturados, importe_total, fecha_factura, obra_destino, estatus_revision
            FROM diesel.facturas
            WHERE semana = %s
        """
        if obra and obra != 'TODAS':
            query_fac_det += " AND obra_destino = %s"
        query_fac_det += " ORDER BY id DESC"
        cur.execute(query_fac_det, params_fac)
        facturas_detalle = [dict(r) for r in cur.fetchall()]
        for f in facturas_detalle:
            if f.get('litros_facturados'): f['litros_facturados'] = float(f['litros_facturados'])
            if f.get('importe_total'): f['importe_total'] = float(f['importe_total'])

        # 2. Suma de Cargas de Obra de la semana / obra
        query_car = """
            SELECT COALESCE(SUM(litros), 0) as total_litros,
                   COALESCE(SUM(importe_total), 0) as total_importe,
                   COUNT(*) as total_count,
                   COUNT(CASE WHEN foto_evidencia IS NOT NULL THEN 1 END) as con_foto,
                   COUNT(CASE WHEN horometro_inicial IS NOT NULL AND horometro_inicial > 0 THEN 1 END) as con_horometro
            FROM diesel.consumos
            WHERE semana = %s
        """
        params_car = [semana]
        if obra and obra != 'TODAS':
            query_car += " AND obra_destino = %s"
            params_car.append(obra)

        cur.execute(query_car, params_car)
        car_summary = cur.fetchone()

        # Detalle de cargas
        query_car_det = """
            SELECT id, folio_conciliacion, fecha, equipo_economico, litros, importe_total,
                   responsable, operador, horometro_inicial, (foto_evidencia IS NOT NULL) as tiene_foto
            FROM diesel.consumos
            WHERE semana = %s
        """
        if obra and obra != 'TODAS':
            query_car_det += " AND obra_destino = %s"
        query_car_det += " ORDER BY id DESC LIMIT 50"
        cur.execute(query_car_det, params_car)
        cargas_detalle = [dict(r) for r in cur.fetchall()]
        for c in cargas_detalle:
            if c.get('litros'): c['litros'] = float(c['litros'])
            if c.get('importe_total'): c['importe_total'] = float(c['importe_total'])
            if c.get('horometro_inicial'): c['horometro_inicial'] = float(c['horometro_inicial'])

        db.close()

        litros_fac = float(fac_summary['total_litros']) if fac_summary else 0.0
        importe_fac = float(fac_summary['total_importe']) if fac_summary else 0.0
        count_fac = int(fac_summary['total_count']) if fac_summary else 0

        litros_car = float(car_summary['total_litros']) if car_summary else 0.0
        importe_car = float(car_summary['total_importe']) if car_summary else 0.0
        count_car = int(car_summary['total_count']) if car_summary else 0
        con_foto = int(car_summary['con_foto']) if car_summary else 0
        con_horo = int(car_summary['con_horometro']) if car_summary else 0

        diff_litros = round(litros_fac - litros_car, 2)
        diff_importe = round(importe_fac - importe_car, 2)

        pct_consumido = round((litros_car / litros_fac * 100), 1) if litros_fac > 0 else 0.0
        pct_fotos = round((con_foto / count_car * 100), 1) if count_car > 0 else 100.0
        pct_horo = round((con_horo / count_car * 100), 1) if count_car > 0 else 100.0

        if count_fac == 0:
            estatus = 'SIN_FACTURA'
            color = '#94a3b8'
            msg = f'No hay facturas registradas en la Semana {semana} para {obra or "todas las obras"}.'
        elif abs(diff_litros) <= 15.0:
            estatus = 'CONCILIADO'
            color = '#10b981'
            msg = f'✔ Conciliado. Facturados: {litros_fac:,.1f} L vs Cargas: {litros_car:,.1f} L (Diferencia: {diff_litros:,.1f} L).'
        elif diff_litros > 15.0:
            estatus = 'SALDO_DISPONIBLE'
            color = '#3b82f6'
            msg = f'ℹ️ Saldo en tanque/pipa: {diff_litros:,.1f} L disponibles ({pct_consumido}% consumido).'
        else:
            estatus = 'ALERTA_EXCEDIDO'
            color = '#ef4444'
            msg = f'⚠️ ALERTA: Las cargas en obra exceden lo facturado por {abs(diff_litros):,.1f} L.'

        return jsonify({
            'success': True,
            'semana': semana,
            'obra': obra or 'TODAS',
            'estatus': estatus,
            'color': color,
            'mensaje': msg,
            'balance': {
                'litros_facturados': litros_fac,
                'litros_consumidos': litros_car,
                'diferencia_litros': diff_litros,
                'porcentaje_consumido': pct_consumido,
                'importe_facturado': importe_fac,
                'importe_consumido': importe_car,
                'diferencia_importe': diff_importe
            },
            'auditoria_fotos': {
                'total_cargas': count_car,
                'con_foto': con_foto,
                'porcentaje_fotos': pct_fotos,
                'con_horometro': con_horo,
                'porcentaje_horometros': pct_horo
            },
            'facturas': facturas_detalle,
            'cargas': cargas_detalle
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/diesel/webhook_nueva_factura', methods=['POST'])
def api_diesel_webhook_nueva_factura():
    data = request.json or {}
    print("📢 WEBHOOK RECIBIDO DE N8N (Nueva Factura Diésel):", data)
    return jsonify({'success': True, 'received': data})

if __name__ == '__main__':
    print('Iniciando Portal de Captura Fénix v2')
    app.run(host='0.0.0.0', port=5001, debug=True)

