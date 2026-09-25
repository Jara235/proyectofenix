import os
import sys
import io
import re
import datetime
from flask import Flask, render_template, jsonify, request, send_file, redirect, url_for
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable, Image
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import psycopg2
from psycopg2.extras import DictCursor
import xml.etree.ElementTree as ET

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import os
app = Flask(__name__, template_folder=os.path.join("servidor", "templates", "admin"), static_folder=os.path.join("servidor", "static"), static_url_path='/static')
app.config['JSON_AS_ASCII'] = False

class DbProxy:
    def __init__(self, conn):
        self.conn = conn
    def execute(self, sql, params=()):
        cur = self.conn.cursor(cursor_factory=DictCursor)
        cur.execute(sql, params)
        return cur
    def commit(self):
        self.conn.commit()
    def close(self):
        self.conn.close()

def get_db():
    conn = psycopg2.connect(
        dbname="fenix_db",
        user="postgres",
        password="Bupito*268",
        host="localhost"
    )
    conn.autocommit = True
    return DbProxy(conn)

import json
def registrar_auditoria(db, tabla, registro_id, accion, anterior=None, nuevo=None, usuario='ADMIN'):
    try:
        val_ant_json = json.dumps(anterior, default=str) if anterior else None
        val_nuev_json = json.dumps(nuevo, default=str) if nuevo else None
        db.execute("""
            INSERT INTO catalogos.audit_log (tabla_afectada, registro_id, usuario, accion, valor_anterior, valor_nuevo)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (tabla, registro_id, usuario, accion, val_ant_json, val_nuev_json))
    except Exception as e:
        print("Error al registrar auditoría:", e)
    

# ─────────────────────────────────────────
@app.route('/')
def admin_home():
    # Bandeja de entrada global
    db = get_db()
    kpis = {}
    
    def count_pendientes(table):
        row = db.execute(f"SELECT COUNT(*) FROM {table} WHERE estatus_revision = 'PENDIENTE'").fetchone()
        return row[0] if row else 0

    kpis['diesel_consumos'] = count_pendientes('diesel.consumos')
    kpis['diesel_facturas'] = count_pendientes('diesel.facturas')
    kpis['gasolina_consumos'] = count_pendientes('gasolina.consumos')
    kpis['gasolina_facturas'] = count_pendientes('gasolina.facturas')
    
    db.close()
    return render_template('admin_home.html', kpis=kpis)

@app.route('/admin/diesel')
def admin_diesel():
    db = get_db()
    semanas = db.execute("SELECT DISTINCT semana FROM diesel.consumos WHERE semana IS NOT NULL ORDER BY semana DESC").fetchall()
    obras = db.execute("""
        SELECT nombre FROM catalogos.obras 
        UNION 
        SELECT DISTINCT obra_destino FROM diesel.consumos WHERE obra_destino IS NOT NULL
        ORDER BY nombre
    """).fetchall()
    equipos = db.execute("""
        SELECT descripcion FROM catalogos.equipos WHERE tipo_equipo='DIESEL' 
        UNION 
        SELECT DISTINCT equipo FROM diesel.consumos WHERE equipo IS NOT NULL
        ORDER BY descripcion
    """).fetchall()
    responsables = db.execute("""
        SELECT DISTINCT nombre FROM (
            SELECT referencia AS nombre FROM catalogos.autorizaciones
                WHERE tipo = 'DIESEL' AND referencia IS NOT NULL AND referencia NOT IN ('S/R','nan','')
            UNION
            SELECT DISTINCT responsable AS nombre FROM diesel.consumos
                WHERE responsable IS NOT NULL AND responsable NOT IN ('S/R','nan','')
        ) t
        ORDER BY nombre
    """).fetchall()
    db.close()
    return render_template('admin_diesel.html', semanas=semanas, obras=obras, equipos=equipos, responsables=responsables)

@app.route('/admin/resumen')
def admin_resumen():
    return render_template('admin_resumen.html')

@app.route('/admin/gasolina')
def admin_gasolina():
    db = get_db()
    obras = db.execute("SELECT nombre FROM catalogos.obras ORDER BY nombre").fetchall()
    vehiculos = db.execute("SELECT descripcion FROM catalogos.equipos WHERE tipo_equipo='GASOLINA' ORDER BY descripcion").fetchall()
    db.close()
    return render_template('admin_gasolina.html', obras=obras, vehiculos=vehiculos)

@app.route('/admin/facturas')
def admin_subir_facturas():
    db = get_db()
    
    # Obtener historial reciente de facturas de las bases de respaldo
    q_diesel = "SELECT id, 'Diésel' as combustible, folio_factura, fecha_factura, litros_facturados, importe_total, proveedor, obra_destino, uuid_cfdi FROM diesel.facturas ORDER BY id DESC LIMIT 5"
    q_gasolina = "SELECT id, 'Gasolina' as combustible, folio_factura, fecha_factura, litros_facturados, importe_total, proveedor, '' as obra_destino, uuid_cfdi FROM gasolina.facturas ORDER BY id DESC LIMIT 5"
    
    historial = []
    try:
        historial += db.execute(q_diesel).fetchall()
        historial += db.execute(q_gasolina).fetchall()
        # Ordenar por ID asumiendo que los IDs más altos son los más recientes globalmente (aproximado)
        historial.sort(key=lambda x: x['id'], reverse=True)
    except Exception as e:
        print("Error fetching historial:", e)
        
    db.close()
    return render_template('admin_subir_facturas.html', historial_facturas=historial[:10])

@app.route('/admin/catalogos')
def admin_catalogos():
    return render_template('admin_catalogos.html')

@app.route('/api/admin/catalogos/obras', methods=['GET', 'POST'])
def api_obras():
    db = get_db()
    if request.method == 'GET':
        obras = db.execute('SELECT codigo, nombre FROM catalogos.obras ORDER BY nombre').fetchall()
        db.close()
        return jsonify([dict(o) for o in obras])
    elif request.method == 'POST':
        data = request.json
        try:
            db.execute('INSERT INTO catalogos.obras (codigo, nombre) VALUES (%s, %s)', (data['codigo'], data['nombre']))
            if 'tope_diesel' in data and data['tope_diesel']:
                semana_actual = datetime.date.today().isocalendar()[1]
                db.execute('INSERT INTO catalogos.autorizaciones (tipo, semana, referencia, litros_autorizados) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING', ('DIESEL', semana_actual, data['nombre'], float(data['tope_diesel'])))
            db.commit()
            db.close()
            return jsonify({'success': True})
        except Exception as e:
            db.close()
            return jsonify({'success': False, 'error': str(e)})

@app.route('/api/admin/catalogos/obras/<codigo>', methods=['DELETE'])
def api_obras_delete(codigo):
    db = get_db()
    try:
        db.execute('DELETE FROM catalogos.obras WHERE codigo = %s', (codigo,))
        db.commit()
        db.close()
        return jsonify({'success': True})
    except Exception as e:
        db.close()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/admin/catalogos/equipos', methods=['GET', 'POST'])
def api_equipos():
    db = get_db()
    if request.method == 'GET':
        equipos = db.execute('SELECT numero_economico, descripcion, tipo_equipo FROM catalogos.equipos ORDER BY descripcion').fetchall()
        db.close()
        return jsonify([dict(e) for e in equipos])
    elif request.method == 'POST':
        data = request.json
        try:
            db.execute('INSERT INTO catalogos.equipos (numero_economico, descripcion, tipo_equipo) VALUES (%s, %s, %s)', (data['numero_economico'], data['descripcion'], data['tipo_equipo']))
            if 'tope_gasolina' in data and data['tope_gasolina'] and data['tipo_equipo'] == 'GASOLINA':
                semana_actual = datetime.date.today().isocalendar()[1]
                db.execute('INSERT INTO catalogos.autorizaciones (tipo, semana, referencia, litros_autorizados) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING', ('GASOLINA', semana_actual, data['descripcion'], float(data['tope_gasolina'])))
            db.commit()
            db.close()
            return jsonify({'success': True})
        except Exception as e:
            db.close()
            return jsonify({'success': False, 'error': str(e)})

@app.route('/api/admin/catalogos/equipos/<path:num_eco>', methods=['DELETE'])
def api_equipos_delete(num_eco):
    db = get_db()
    try:
        db.execute('DELETE FROM catalogos.equipos WHERE numero_economico = %s', (num_eco,))
        db.commit()
        db.close()
        return jsonify({'success': True})
    except Exception as e:
        db.close()
        return jsonify({'success': False, 'error': str(e)})

# ─────────────────────────────────────────
# APIS DE AUTORIZACIONES
# ─────────────────────────────────────────
@app.route('/api/admin/autorizaciones')
def api_autorizaciones():
    tipo = request.args.get('tipo', 'DIESEL')
    semana = request.args.get('semana', datetime.date.today().isocalendar()[1])
    is_resumen = request.args.get('resumen', 'false') == 'true'
    try: semana = int(semana)
    except: return jsonify([])

    db = get_db()
    
    # Asegurar que existan todos los registros activos (obras/equipos) para la semana actual copiando de la anterior si es necesario
    auths = db.execute("SELECT id, referencia, litros_autorizados FROM catalogos.autorizaciones WHERE tipo=%s AND semana=%s", (tipo, semana)).fetchall()
    
    if not auths:
        last_week_row = db.execute("SELECT MAX(semana) as s FROM catalogos.autorizaciones WHERE tipo=%s AND semana<%s", (tipo, semana)).fetchone()
        last_week = last_week_row['s'] if last_week_row and last_week_row['s'] else None
        
        if last_week:
            db.execute("""
                INSERT INTO catalogos.autorizaciones (tipo, semana, referencia, litros_autorizados)
                SELECT tipo, %s, referencia, litros_autorizados
                FROM catalogos.autorizaciones WHERE tipo=%s AND semana=%s
            """, (semana, tipo, last_week))
            db.commit()

    # Si hay nuevas obras o equipos que no se copiaron de la semana anterior, los insertamos en 0
    if tipo == 'DIESEL':
        referencias = db.execute("SELECT nombre as ref FROM catalogos.responsables").fetchall()
    else:
        referencias = db.execute("SELECT descripcion as ref FROM catalogos.equipos WHERE tipo_equipo='GASOLINA'").fetchall()
        
    for r in referencias:
        db.execute("INSERT INTO catalogos.autorizaciones (tipo, semana, referencia, litros_autorizados) VALUES (%s, %s, %s, 0) ON CONFLICT (tipo, semana, referencia) DO NOTHING", (tipo, semana, r['ref']))
    db.commit()
    
    auths = db.execute("SELECT id, referencia, litros_autorizados FROM catalogos.autorizaciones WHERE tipo=%s AND semana=%s ORDER BY referencia", (tipo, semana)).fetchall()
    
    auths_data = []
    try:
        for a in auths:
            semana_str = str(semana)
            if tipo == 'DIESEL':
                cons = db.execute("SELECT SUM(litros) as total, SUM(importe_total) as costo FROM diesel.consumos WHERE semana=%s AND responsable=%s AND estatus_revision != 'RECHAZADO'", (semana_str, a['referencia'])).fetchone()
            else:
                cons = db.execute("SELECT SUM(litros) as total, SUM(importe_total) as costo FROM gasolina.consumos WHERE semana=%s AND (vehiculo=%s OR placa=%s) AND estatus_revision != 'RECHAZADO'", (semana_str, a['referencia'], a['referencia'])).fetchone()
                
            consumo_actual = float(cons['total'] or 0) if cons else 0.0
            costo_total = float(cons['costo'] or 0) if cons else 0.0
            
            # Filtro: Solo en pestaña resumen ocultamos las obras sin consumo
            if is_resumen and consumo_actual <= 0:
                continue
            
            auths_data.append({
                'id': a['id'],
                'referencia': a['referencia'],
                'litros_autorizados': float(a['litros_autorizados'] or 0),
                'consumo_actual': consumo_actual,
                'costo_total': costo_total,
                'excedido': consumo_actual > (float(a['litros_autorizados'] or 0) * 7) and float(a['litros_autorizados'] or 0) > 0
            })
    except Exception as e:
        print("ERROR en api_autorizaciones:", e)
        
    db.close()
    return jsonify(auths_data)

def sync_gasolina_autorizaciones_arrastre(db, semana_num):
    """Garantiza la continuidad/arrastre semanal de las autorizaciones de gasolina."""
    cnt = db.execute("SELECT COUNT(*) FROM gasolina.autorizaciones_semanal WHERE semana = %s", (semana_num,)).fetchone()[0]
    if cnt == 0:
        max_sem_prev_row = db.execute("SELECT MAX(semana) FROM gasolina.autorizaciones_semanal WHERE semana < %s", (semana_num,)).fetchone()
        max_sem_prev = max_sem_prev_row[0] if max_sem_prev_row else None
        
        if max_sem_prev:
            db.execute("""
                INSERT INTO gasolina.autorizaciones_semanal 
                    (semana, maestro_id, empresa, num_renglon, responsable, centro_trabajo, unidad_equipo, placas, importe_semanal)
                SELECT %s, maestro_id, empresa, num_renglon, responsable, centro_trabajo, unidad_equipo, placas, importe_semanal
                FROM gasolina.autorizaciones_semanal WHERE semana = %s
                ON CONFLICT (semana, maestro_id) DO NOTHING;
            """, (semana_num, max_sem_prev))
        else:
            db.execute("""
                INSERT INTO gasolina.autorizaciones_semanal 
                    (semana, maestro_id, empresa, num_renglon, responsable, centro_trabajo, unidad_equipo, placas, importe_semanal)
                SELECT %s, id, empresa, num_renglon, responsable, centro_trabajo, unidad_equipo, placas, importe_semanal
                FROM gasolina.autorizaciones_maestro WHERE activo = TRUE
                ON CONFLICT (semana, maestro_id) DO NOTHING;
            """, (semana_num,))

@app.route('/api/admin/gasolina/autorizaciones')
def api_gasolina_autorizaciones():
    db = get_db()
    semana_param = request.args.get('semana', '30')
    empresa_param = request.args.get('empresa', 'TODAS')
    
    try:
        sem_num = int(str(semana_param).replace('Semana ', '').strip())
    except:
        sem_num = 30
        
    sync_gasolina_autorizaciones_arrastre(db, sem_num)
    
    query = """
        SELECT id, semana, maestro_id, empresa, num_renglon, responsable, centro_trabajo, unidad_equipo, placas, importe_semanal
        FROM gasolina.autorizaciones_semanal
        WHERE semana = %s
    """
    params = [sem_num]
    
    if empresa_param in ['J.D.J.', 'TRD']:
        query += " AND empresa = %s"
        params.append(empresa_param)
        
    query += " ORDER BY CASE WHEN empresa='J.D.J.' THEN 1 ELSE 2 END, num_renglon ASC"
    
    rows = db.execute(query, tuple(params)).fetchall()
    data_rows = [dict(r) for r in rows]
    
    for r in data_rows:
        r['importe_semanal'] = float(r['importe_semanal'] or 0)
        placa_val = r['placas']
        vehiculo_val = r['unidad_equipo']
        
        c_row = db.execute("""
            SELECT SUM(litros) as total_litros, SUM(importe_total) as total_importe
            FROM gasolina.consumos
            WHERE semana = %s AND (
                (placa IS NOT NULL AND placa != 'S/P' AND placa ILIKE %s) OR
                (vehiculo IS NOT NULL AND vehiculo ILIKE %s)
            ) AND estatus_revision != 'RECHAZADO'
        """, (str(sem_num), f"%{placa_val}%", f"%{vehiculo_val}%")).fetchone()
        
        r['consumo_real_litros'] = float(c_row['total_litros'] or 0) if c_row else 0.0
        r['consumo_real_importe'] = float(c_row['total_importe'] or 0) if c_row else 0.0
        r['excedido'] = r['consumo_real_importe'] > r['importe_semanal'] and r['importe_semanal'] > 0

    tot_jdj = sum([r['importe_semanal'] for r in data_rows if r['empresa'] == 'J.D.J.'])
    tot_trd = sum([r['importe_semanal'] for r in data_rows if r['empresa'] == 'TRD'])
    tot_gen = sum([r['importe_semanal'] for r in data_rows])

    db.close()
    return jsonify({
        'success': True,
        'semana': sem_num,
        'totales': {
            'jdj': round(tot_jdj, 2),
            'trd': round(tot_trd, 2),
            'general': round(tot_gen, 2)
        },
        'autorizaciones': data_rows
    })

@app.route('/api/admin/gasolina/autorizaciones/guardar', methods=['POST'])
def api_gasolina_guardar_autorizacion():
    try:
        data = request.json or request.form
        id_reg = data.get('id')
        semana = int(data.get('semana', 30))
        monto = float(data.get('importe_semanal', 0))
        
        db = get_db()
        db.execute("""
            UPDATE gasolina.autorizaciones_semanal
            SET importe_semanal = %s
            WHERE id = %s AND semana = %s
        """, (monto, id_reg, semana))
        
        db.execute("""
            UPDATE gasolina.autorizaciones_semanal AS target
            SET importe_semanal = %s
            FROM gasolina.autorizaciones_semanal AS source
            WHERE target.maestro_id = source.maestro_id
              AND source.id = %s
              AND target.semana > %s
        """, (monto, id_reg, semana))
        
        db.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/admin/autorizaciones/guardar', methods=['POST'])
def api_guardar_autorizacion():
    try:
        data = request.json
        id_auth = data.get('id')
        monto = float(data.get('litros', 0))
        db = get_db()
        
        auth_info = db.execute("SELECT tipo, semana, referencia FROM catalogos.autorizaciones WHERE id = %s", (id_auth,)).fetchone()
        
        if auth_info:
            tipo = auth_info['tipo']
            semana = auth_info['semana']
            referencia = auth_info['referencia']
            
            # Actualizar la semana actual y semanas futuras para mantener continuidad
            db.execute("""
                UPDATE catalogos.autorizaciones 
                SET litros_autorizados = %s 
                WHERE tipo = %s AND referencia = %s AND semana >= %s
            """, (monto, tipo, referencia, semana))
            
            # Si es gasolina, sincronizar también en gasolina.estados_cuenta para semana actual y futuras
            if tipo == 'GASOLINA':
                db.execute("""
                    UPDATE gasolina.estados_cuenta
                    SET importe_autorizado = %s
                    WHERE (CASE WHEN semana ~ '^[0-9]+$' THEN semana::integer ELSE 0 END) >= %s
                      AND (vehiculo ILIKE %s OR placa ILIKE %s OR %s ILIKE '%%' || vehiculo || '%%')
                """, (monto, semana, f"%{referencia}%", f"%{referencia}%", referencia))
            
            registrar_auditoria(db, 'catalogos.autorizaciones', id_auth, 'CAMBIO_TOPE', {'referencia': referencia, 'semana': semana}, {'monto_nuevo': monto})
            db.commit()
            
        db.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ─────────────────────────────────────────
# APIS DE APROBACIÓN
# ─────────────────────────────────────────
@app.route('/api/admin/actualizar_estatus', methods=['POST'])
def api_actualizar_estatus():
    try:
        data = request.json
        tabla = data.get('tabla')
        id_registro = data.get('id')
        nuevo_estatus = data.get('estatus') # 'APROBADO' o 'RECHAZADO'
        
        # Validacion basica de seguridad
        tablas_permitidas = ['diesel.consumos', 'diesel.facturas', 'gasolina.consumos', 'gasolina.facturas', 'gasolina.estados_cuenta', 'diesel.solicitudes']
        if tabla not in tablas_permitidas:
            return jsonify({'success': False, 'error': 'Tabla no válida'})
            
        col_estatus = 'estatus_conciliacion' if 'solicitudes' in tabla else 'estatus_revision'
            
        db = get_db()
        db.execute(f"UPDATE {tabla} SET {col_estatus} = %s WHERE id = %s", (nuevo_estatus, id_registro))
        db.commit()
        db.close()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/admin/aprobar_batch', methods=['POST'])
def api_aprobar_batch():
    try:
        data = request.json
        tabla = data.get('tabla')
        ids = data.get('ids', [])
        nuevo_estatus = data.get('estatus', 'APROBADO')
        forzar = data.get('forzar', False)  # Si el user explicitamente elige continuar
        
        tablas_permitidas = ['diesel.consumos', 'diesel.facturas', 'diesel.solicitudes', 'gasolina.consumos', 'gasolina.facturas', 'gasolina.solicitudes']
        if tabla not in tablas_permitidas or not ids:
            return jsonify({'success': False, 'error': 'Datos inválidos'})
            
        col_estatus = 'estatus_conciliacion' if 'solicitudes' in tabla else 'estatus_revision'
        
        db = get_db()
        # Verificar duplicados si estamos aprobando y no se forzó
        if nuevo_estatus == 'APROBADO' and not forzar:
            duplicados_encontrados = []
            for id_reg in ids:
                row = db.execute(f"SELECT * FROM {tabla} WHERE id = %s", (id_reg,)).fetchone()
                if not row: continue
                
                dup_query = None
                dup_params = None
                
                if 'consumos' in tabla:
                    col_eq = 'vehiculo' if 'gasolina' in tabla else 'equipo'
                    col_op = 'conductor' if 'gasolina' in tabla else 'operador'
                    dup_query = f"SELECT id, folio_conciliacion, fecha::text as fecha, litros, importe_total, obra_destino, {col_eq} as equipo, {col_op} as operador FROM {tabla} WHERE fecha::text = %s::text AND litros = %s AND obra_destino = %s AND id != %s AND {col_estatus} = 'APROBADO'"
                    dup_params = (row['fecha'], row['litros'], row['obra_destino'], id_reg)
                elif 'facturas' in tabla:
                    dup_query = f"SELECT id, folio_conciliacion, fecha_factura::text as fecha_factura, litros_facturados, importe_total, proveedor FROM {tabla} WHERE fecha_factura::text = %s::text AND litros_facturados = %s AND proveedor = %s AND id != %s AND {col_estatus} = 'APROBADO'"
                    dup_params = (row['fecha_factura'], row['litros_facturados'], row['proveedor'], id_reg)
                elif 'solicitudes' in tabla:
                    dup_query = f"SELECT id, folio_solicitud, fecha::text as fecha, litros, importe_total, obra_destino, solicitante FROM {tabla} WHERE fecha::text = %s::text AND litros = %s AND importe_total = %s AND obra_destino = %s AND id != %s AND {col_estatus} = 'APROBADO'"
                    dup_params = (row['fecha'], row['litros'], row['importe_total'], row['obra_destino'], id_reg)
                    
                if dup_query:
                    dup = db.execute(dup_query, dup_params).fetchone()
                    if dup:
                        # Construir info del registro pendiente
                        pendiente_info = {}
                        if 'consumos' in tabla:
                            pendiente_info = {
                                'id': id_reg,
                                'folio': row['folio_conciliacion'],
                                'fecha': str(row['fecha']),
                                'litros': float(row['litros'] or 0),
                                'importe': float(row['importe_total'] or 0),
                                'obra': row['obra_destino'],
                                'equipo': row.get('vehiculo') or row.get('equipo', ''),
                            }
                        elif 'facturas' in tabla:
                            pendiente_info = {
                                'id': id_reg,
                                'folio': row['folio_conciliacion'],
                                'fecha': str(row['fecha_factura']),
                                'litros': float(row['litros_facturados'] or 0),
                                'importe': float(row['importe_total'] or 0),
                                'proveedor': row.get('proveedor', ''),
                            }
                        elif 'solicitudes' in tabla:
                            pendiente_info = {
                                'id': id_reg,
                                'folio': row['folio_solicitud'],
                                'fecha': str(row['fecha']),
                                'litros': float(row['litros'] or 0),
                                'importe': float(row['importe_total'] or 0),
                                'obra': row['obra_destino'],
                                'solicitante': row.get('solicitante', ''),
                            }
                        
                        duplicados_encontrados.append({
                            'pendiente': pendiente_info,
                            'aprobado': dict(dup)
                        })
            
            if duplicados_encontrados:
                db.close()
                return jsonify({
                    'success': False,
                    'duplicateWarning': True,
                    'duplicados': duplicados_encontrados,
                    'error': f'Se detectaron {len(duplicados_encontrados)} posible(s) duplicado(s).'
                })
        
        # Proceder a actualizar
        format_strings = ','.join(['%s'] * len(ids))
        db.execute(f"UPDATE {tabla} SET {col_estatus} = %s WHERE id IN ({format_strings})", [nuevo_estatus] + ids)
        db.commit()
        db.close()
        
        return jsonify({'success': True, 'aprobados': len(ids)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})



@app.route('/api/admin/borrar_registro', methods=['POST'])
def api_borrar_registro():
    try:
        data = request.json
        tabla = data.get('tabla')
        id_registro = data.get('id')
        
        tablas_permitidas = ['diesel.consumos', 'diesel.facturas', 'gasolina.consumos', 'gasolina.facturas', 'gasolina.estados_cuenta', 'diesel.solicitudes']
        if tabla not in tablas_permitidas:
            print(f"Borrar denegado: tabla no permitida {tabla}")
            return jsonify({'success': False, 'error': 'Tabla no válida para borrado'})
            
        db = get_db()
        print(f"Borrando de {tabla} el id {id_registro}")
        db.execute(f"DELETE FROM {tabla} WHERE id = %s", (id_registro,))
        db.commit()
        db.close()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/admin/editar_registro', methods=['POST'])
def api_editar_registro():
    try:
        if request.is_json:
            data = request.json
            tabla = data.get('tabla')
            id_registro = data.get('id')
            campos = data.get('campos') # dict of fields
        else:
            tabla = request.form.get('tabla')
            id_registro = request.form.get('id')
            import json
            campos = json.loads(request.form.get('campos', '{}'))
            
            fotos = request.files.getlist('foto_evidencia')
            if fotos and len(fotos) > 0 and fotos[0].filename != '':
                columna_binaria = 'archivo_pdf' if 'facturas' in tabla else 'foto_evidencia'
                if len(fotos) == 1:
                    campos[columna_binaria] = fotos[0].read()
                else:
                    import io, zipfile
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                        for i, f in enumerate(fotos):
                            if f.filename:
                                zip_file.writestr(f.filename, f.read())
                    campos[columna_binaria] = zip_buffer.getvalue()
        
        tablas_permitidas = [
            'diesel.consumos', 'diesel.facturas', 'diesel.solicitudes',
            'gasolina.consumos', 'gasolina.facturas', 'gasolina.solicitudes'
        ]
        if tabla not in tablas_permitidas:
            return jsonify({'success': False, 'error': 'Tabla no válida'})

            
        if not campos or not id_registro:
            return jsonify({'success': False, 'error': 'Faltan datos'})
            
        clean_campos = {}
        for k, v in campos.items():
            if isinstance(v, str) and v.strip() == '':
                clean_campos[k] = None
            else:
                clean_campos[k] = v

        # Auto-register vehicle/plate in catalogos.equipos if needed
        veh_val = clean_campos.get('vehiculo') or clean_campos.get('placa')
        if veh_val and 'consumos' in tabla:
            tipo_eq = 'GASOLINA' if 'gasolina' in tabla else 'DIESEL'
            db_eq = get_db()
            cur_eq = db_eq.execute('SELECT 1 FROM catalogos.equipos WHERE numero_economico = %s', (veh_val,))
            if not cur_eq.fetchone():
                db_eq.execute('''
                    INSERT INTO catalogos.equipos (numero_economico, descripcion, tipo_equipo)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (numero_economico) DO NOTHING
                ''', (veh_val, f"Vehículo {veh_val}", tipo_eq))
            db_eq.close()

        set_clause = ", ".join([f"{k} = %s" for k in clean_campos.keys()])
        valores = list(clean_campos.values())
        valores.append(id_registro)
        
        db = get_db()
        db.execute(f"UPDATE {tabla} SET {set_clause} WHERE id = %s", valores)
        db.commit()
        db.close()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ─────────────────────────────────────────
# API: DATOS PENDIENTES
# ─────────────────────────────────────────
@app.route('/api/admin/semanas')
def api_admin_semanas():
    db = get_db()
    sems = set()
    for tabla in ['diesel.consumos', 'diesel.facturas', 'gasolina.consumos', 'gasolina.facturas']:
        col = 'semana'
        for row in db.execute(f'SELECT DISTINCT {col} FROM {tabla} WHERE {col} IS NOT NULL'):
            val = str(row[0]).replace('Semana', '').strip()
            if val:
                sems.add(f"Semana {val}")
    db.close()
    def sort_key(s):
        num = s.replace('Semana','').strip()
        return int(num) if num.isdigit() else 0
    return jsonify(sorted(sems, key=sort_key, reverse=True))

@app.route('/api/admin/pendientes/gasolina_consumos')
def api_pendientes_gasolina_consumos():
    db = get_db()
    estatus = request.args.get('estatus', 'PENDIENTE')
    semana = str(request.args.get('semana', '')).replace('Semana ', '').replace('Semana', '').strip()
    cond_estatus = "estatus_revision = %s" if estatus != 'TODOS' else "1=1"
    params = [estatus] if estatus != 'TODOS' else []
    cond_semana = ''
    if semana:
        cond_semana = ' AND semana = %s'
        params.append(semana)
    rows = db.execute(f'''
        SELECT id, folio_conciliacion, fecha, semana, origen, obra_destino, vehiculo, placa, litros, importe_total, conductor, observaciones, estatus_revision
        FROM gasolina.consumos 
        WHERE {cond_estatus}{cond_semana}
        ORDER BY id DESC
    ''', params).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/admin/pendientes/diesel_consumos')
def api_pendientes_diesel_consumos():
    db = get_db()
    estatus = request.args.get('estatus', 'PENDIENTE')
    semana = str(request.args.get('semana', '')).replace('Semana ', '').replace('Semana', '').strip()
    cond_estatus = "estatus_revision = %s" if estatus != 'TODOS' else "1=1"
    params = [estatus] if estatus != 'TODOS' else []
    cond_semana = ''
    if semana:
        cond_semana = ' AND semana = %s'
        params.append(semana)
    rows = db.execute(f'''
        SELECT id, folio_conciliacion, fecha, semana, origen, obra_destino, equipo, litros, importe_total, operador, estatus_revision
        FROM diesel.consumos 
        WHERE {cond_estatus}{cond_semana}
        ORDER BY id DESC
    ''', params).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/admin/pendientes/diesel_solicitudes')
def api_pendientes_diesel_solicitudes():
    db = get_db()
    estatus = request.args.get('estatus', 'PENDIENTE')
    semana = str(request.args.get('semana', '')).replace('Semana ', '').replace('Semana', '').strip()
    cond_estatus = "estatus_conciliacion = %s" if estatus != 'TODOS' else "1=1"
    params = [estatus] if estatus != 'TODOS' else []
    cond_semana = ''
    if semana:
        cond_semana = ' AND semana = %s'
        params.append(semana)
    rows = db.execute(f'''
        SELECT id, folio_solicitud, fecha::text as fecha, semana, solicitante, tipo_movimiento, obra_destino, equipo, equipo_economico, litros, costo_por_litro, importe_total, responsable, operador, estatus_conciliacion, observaciones
        FROM diesel.solicitudes 
        WHERE {cond_estatus}{cond_semana}
        ORDER BY id DESC
    ''', params).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/admin/pendientes/diesel_facturas')
def api_pendientes_diesel_facturas():
    db = get_db()
    estatus = request.args.get('estatus', 'PENDIENTE')
    semana = str(request.args.get('semana', '')).replace('Semana ', '').replace('Semana', '').strip()
    q = str(request.args.get('q', '') or request.args.get('folio', '')).strip()
    cond_estatus = "estatus_revision = %s" if estatus != 'TODOS' else "1=1"
    params = [estatus] if estatus != 'TODOS' else []
    cond_semana = ''
    if semana:
        cond_semana = ' AND semana = %s'
        params.append(semana)
    cond_q = ''
    if q:
        cond_q = ' AND (folio_factura ILIKE %s OR folio_conciliacion ILIKE %s OR uuid_cfdi ILIKE %s OR proveedor ILIKE %s)'
        params.extend([f'%{q}%', f'%{q}%', f'%{q}%', f'%{q}%'])
    rows = db.execute(f'''
        SELECT id, folio_conciliacion, folio_factura, fecha_factura, semana, proveedor, litros_facturados, importe_total, uuid_cfdi, estatus_revision
        FROM diesel.facturas 
        WHERE {cond_estatus}{cond_semana}{cond_q}
        ORDER BY id DESC
    ''', params).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/admin/pendientes/gasolina_facturas')
def api_pendientes_gasolina_facturas():
    db = get_db()
    estatus = request.args.get('estatus', 'PENDIENTE')
    semana = str(request.args.get('semana', '')).replace('Semana ', '').replace('Semana', '').strip()
    q = str(request.args.get('q', '') or request.args.get('folio', '')).strip()
    cond_estatus = "estatus_revision = %s" if estatus != 'TODOS' else "1=1"
    params = [estatus] if estatus != 'TODOS' else []
    cond_semana = ''
    if semana:
        cond_semana = ' AND semana = %s'
        params.append(semana)
    cond_q = ''
    if q:
        cond_q = ' AND (folio_factura ILIKE %s OR folio_conciliacion ILIKE %s OR uuid_cfdi ILIKE %s OR proveedor ILIKE %s)'
        params.extend([f'%{q}%', f'%{q}%', f'%{q}%', f'%{q}%'])
    rows = db.execute(f'''
        SELECT id, folio_conciliacion, folio_factura, fecha_factura, semana, proveedor, litros_facturados, importe_total, uuid_cfdi, estatus_revision
        FROM gasolina.facturas 
        WHERE {cond_estatus}{cond_semana}{cond_q}
        ORDER BY id DESC
    ''', params).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/admin/todas_las_facturas')
def api_todas_las_facturas():
    db = get_db()
    q = str(request.args.get('q', '') or request.args.get('folio', '')).strip()
    tipo = str(request.args.get('tipo', 'TODOS')).strip().upper()
    estatus = str(request.args.get('estatus', 'TODOS')).strip().upper()
    semana = str(request.args.get('semana', 'TODAS')).strip()

    results = []

    # 1. Diesel Facturas
    if tipo in ['TODOS', 'DIESEL', 'DIÉSEL']:
        params_die = []
        conds_die = ["1=1"]
        if estatus != 'TODOS':
            conds_die.append("estatus_revision = %s")
            params_die.append(estatus)
        if semana != 'TODAS' and semana != '':
            conds_die.append("semana = %s")
            params_die.append(semana)
        if q:
            conds_die.append("(folio_factura ILIKE %s OR folio_conciliacion ILIKE %s OR uuid_cfdi ILIKE %s OR proveedor ILIKE %s)")
            params_die.extend([f'%{q}%', f'%{q}%', f'%{q}%', f'%{q}%'])

        where_die = " AND ".join(conds_die)
        rows_die = db.execute(f'''
            SELECT id, 'DIESEL' as tipo_combustible, folio_conciliacion, folio_factura, fecha_factura, semana, proveedor,
                   litros_facturados, importe_total, uuid_cfdi, estatus_revision,
                   (CASE WHEN archivo_pdf IS NOT NULL THEN true ELSE false END) as tiene_pdf
            FROM diesel.facturas
            WHERE {where_die}
            ORDER BY id DESC
        ''', params_die).fetchall()
        results.extend([dict(r) for r in rows_die])

    # 2. Gasolina Facturas
    if tipo in ['TODOS', 'GASOLINA']:
        params_gas = []
        conds_gas = ["1=1"]
        if estatus != 'TODOS':
            conds_gas.append("estatus_revision = %s")
            params_gas.append(estatus)
        if semana != 'TODAS' and semana != '':
            conds_gas.append("semana = %s")
            params_gas.append(semana)
        if q:
            conds_gas.append("(folio_factura ILIKE %s OR folio_conciliacion ILIKE %s OR uuid_cfdi ILIKE %s OR proveedor ILIKE %s)")
            params_gas.extend([f'%{q}%', f'%{q}%', f'%{q}%', f'%{q}%'])

        where_gas = " AND ".join(conds_gas)
        rows_gas = db.execute(f'''
            SELECT id, 'GASOLINA' as tipo_combustible, folio_conciliacion, folio_factura, fecha_factura, semana, proveedor,
                   litros_facturados, importe_total, uuid_cfdi, estatus_revision,
                   (CASE WHEN archivo_pdf IS NOT NULL THEN true ELSE false END) as tiene_pdf
            FROM gasolina.facturas
            WHERE {where_gas}
            ORDER BY id DESC
        ''', params_gas).fetchall()
        results.extend([dict(r) for r in rows_gas])

    db.close()

    # Sort combined results by fecha_factura or id DESC
    results.sort(key=lambda x: (str(x.get('fecha_factura') or ''), x.get('id') or 0), reverse=True)

    return jsonify(results)


@app.route('/api/admin/facturas/semanas')
def api_facturas_semanas():
    db = get_db()
    weeks_die = db.execute("SELECT DISTINCT semana FROM diesel.facturas WHERE semana IS NOT NULL AND semana != ''").fetchall()
    weeks_gas = db.execute("SELECT DISTINCT semana FROM gasolina.facturas WHERE semana IS NOT NULL AND semana != ''").fetchall()
    db.close()

    raw_weeks = list(set([str(w['semana']) for w in weeks_die] + [str(w['semana']) for w in weeks_gas]))

    def sort_key(s):
        try:
            return (0, int(s))
        except ValueError:
            return (1, s)

    all_weeks = sorted(raw_weeks, key=sort_key, reverse=True)
    return jsonify(all_weeks)


@app.route('/api/admin/facturas/pdf_combinado', methods=['POST'])
def api_facturas_pdf_combinado():
    data = request.json or {}
    items = data.get('items', [])
    if not items:
        return "No se proporcionaron facturas para combinar", 400

    import PyPDF2

    db = get_db()
    merger = PyPDF2.PdfMerger()
    added_count = 0

    for item in items:
        f_tipo = str(item.get('tipo', '')).lower()
        f_id = item.get('id')
        if f_tipo not in ['diesel', 'gasolina'] or not f_id:
            continue

        schema = 'diesel' if f_tipo == 'diesel' else 'gasolina'
        row = db.execute(f"SELECT folio_factura, archivo_pdf FROM {schema}.facturas WHERE id = %s", (f_id,)).fetchone()
        if row and row['archivo_pdf']:
            try:
                pdf_io = io.BytesIO(bytes(row['archivo_pdf']))
                merger.append(pdf_io)
                added_count += 1
            except Exception as e:
                print(f"Error uniendo PDF factura ID {f_id}: {e}")

    db.close()

    if added_count == 0:
        return "Ninguna de las facturas seleccionadas contiene un archivo PDF válido", 400

    out = io.BytesIO()
    merger.write(out)
    out.seek(0)

    from flask import send_file
    return send_file(
        out,
        mimetype='application/pdf',
        as_attachment=False,
        download_name=f'Facturas_Combinadas_{added_count}_archivos.pdf'
    )

# ─────────────────────────────────────────
# API: VISOR DE EVIDENCIA
# ─────────────────────────────────────────
@app.route('/api/evidencia/<tabla_schema>/<tabla_nombre>/<int:id_registro>')
def api_ver_evidencia(tabla_schema, tabla_nombre, id_registro):
    tabla_completa = f"{tabla_schema}.{tabla_nombre}"
    tablas_permitidas = ['diesel.consumos', 'diesel.facturas', 'gasolina.consumos', 'gasolina.facturas']
    if tabla_completa not in tablas_permitidas:
        return "Tabla no válida", 400
        
    db = get_db()
    columna_binaria = 'foto_evidencia' if 'consumos' in tabla_nombre else 'archivo_pdf'
    row = db.execute(f"SELECT {columna_binaria} FROM {tabla_completa} WHERE id = %s", (id_registro,)).fetchone()
    
    data = bytes(row[0]) if (row and row[0]) else None

    # Disk Fallback for facturas PDF if binary column in DB is empty
    if not data and 'facturas' in tabla_nombre:
        info = db.execute(f"SELECT folio_factura, folio_conciliacion, uuid_cfdi FROM {tabla_completa} WHERE id = %s", (id_registro,)).fetchone()
        if info:
            f_fac = str(info['folio_factura'] or '').strip()
            f_con = str(info['folio_conciliacion'] or '').strip()
            uuid_val = str(info['uuid_cfdi'] or '').strip()

            search_dirs = [os.path.join(BASE_DIR, 'facturas'), BASE_DIR]
            found_path = None
            for s_dir in search_dirs:
                if found_path:
                    break
                if not os.path.exists(s_dir):
                    continue
                for r_dir, _, files in os.walk(s_dir):
                    if found_path:
                        break
                    if any(sk in r_dir.lower() for sk in ['node_modules', '.git', 'venv', 'antigravity']):
                        continue
                    for f in files:
                        if not f.lower().endswith('.pdf'):
                            continue
                        f_u = f.upper()
                        if (f_fac and f_fac.upper() in f_u) or (f_con and f_con.upper() in f_u) or (uuid_val and len(uuid_val) > 5 and uuid_val.upper() in f_u):
                            found_path = os.path.join(r_dir, f)
                            break
            if found_path and os.path.exists(found_path):
                try:
                    with open(found_path, 'rb') as fp:
                        data = fp.read()
                    db.execute(f"UPDATE {tabla_completa} SET archivo_pdf = %s WHERE id = %s", (psycopg2.Binary(data), id_registro))
                except Exception as e:
                    pass

    db.close()
    
    if data:
        import io
        import zipfile
        is_zip = data[:4] == b'PK\x03\x04'
        
        action = request.args.get('action', 'view')
        filename = request.args.get('file', '')
        
        if is_zip:
            with zipfile.ZipFile(io.BytesIO(data), 'r') as zf:
                if action == 'list':
                    return jsonify({'type': 'zip', 'files': zf.namelist()})
                elif action == 'view' and filename:
                    file_data = zf.read(filename)
                    ext = filename.lower()
                    if ext.endswith('.pdf'):
                        mimetype = 'application/pdf'
                    elif ext.endswith('.png'):
                        mimetype = 'image/png'
                    else:
                        mimetype = 'image/jpeg'
                    return send_file(io.BytesIO(file_data), mimetype=mimetype)
                else:
                    return jsonify({'type': 'zip', 'files': zf.namelist()})
        else:
            if action == 'list':
                return jsonify({'type': 'single'})
            
            # single file fallback
            mimetype = 'application/pdf' if 'facturas' in tabla_nombre else 'image/jpeg'
            # try to detect pdf from signature
            if data[:4] == b'%PDF':
                mimetype = 'application/pdf'
                
            return send_file(io.BytesIO(data), mimetype=mimetype)
    if 'facturas' in tabla_nombre:
        return """
        <html>
        <body style="background-color: #0f172a; color: #94a3b8; font-family: sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; overflow: hidden;">
            <div style="text-align: center; background: rgba(255,255,255,0.05); padding: 30px; border-radius: 12px; border: 1px dashed rgba(255,255,255,0.1);">
                <div style="font-size: 3rem; margin-bottom: 10px;">📄</div>
                <h2 style="margin: 0; font-size: 1.2rem; color: #cbd5e1;">PDF No Disponible</h2>
                <p style="font-size: 0.9rem; max-width: 250px; margin: 10px auto 0;">Este registro fue guardado sin su archivo PDF correspondiente.</p>
            </div>
        </body>
        </html>
        """, 404
        
    return "No hay evidencia subida para este registro", 404

# ─────────────────────────────────────────
# API: PARSER Y CARGA DE FACTURAS
# ─────────────────────────────────────────
def verificar_factura_duplicada(uuid, folio, proveedor):
    if not uuid and not (folio and proveedor):
        return False, ''
    
    try:
        db = get_db()
        # 1. Checar por UUID CFDI
        if uuid and not str(uuid).startswith('SOLO-PDF'):
            for tabla in ['diesel.facturas', 'gasolina.facturas']:
                row = db.execute(f"SELECT folio_conciliacion, folio_factura, fecha_factura, proveedor FROM {tabla} WHERE uuid_cfdi = %s LIMIT 1", (uuid,)).fetchone()
                if row:
                    db.close()
                    f_fol = row['folio_factura'] or row['folio_conciliacion'] or 'S/F'
                    f_fec = row['fecha_factura'] or ''
                    return True, f"⚠️ Factura duplicada: UUID ya registrado en {tabla} (Folio: {f_fol}, Fecha: {f_fec})"

        # 2. Checar por Folio + Proveedor
        if folio and proveedor:
            for tabla in ['diesel.facturas', 'gasolina.facturas']:
                row = db.execute(f"SELECT folio_conciliacion, folio_factura, fecha_factura, uuid_cfdi FROM {tabla} WHERE UPPER(folio_factura) = %s AND UPPER(proveedor) ILIKE %s LIMIT 1", (str(folio).strip().upper(), f"%{str(proveedor).strip().upper()}%")).fetchone()
                if row:
                    db.close()
                    f_fec = row['fecha_factura'] or ''
                    return True, f"⚠️ Factura duplicada: Folio '{folio}' / '{proveedor}' ya existe en {tabla} ({f_fec})"

        db.close()
    except Exception as e:
        print("Error verificando duplicados:", e)
    return False, ''

# ─────────────────────────────────────────
# API: PARSER Y CARGA DE FACTURAS
# ─────────────────────────────────────────
@app.route('/api/admin/parse_factura', methods=['POST'])
def api_parse_factura():
    import re, io, datetime
    import xml.etree.ElementTree as ET
    res = {
        'cargas': [],
        'obra_texto': '',
        'obra_sugerida': '',
        'uuid': '',
        'fecha': '',
        'semana': '',
        'folio_factura': '',
        'proveedor': '',
        'placa': '',
        'tipo_gasolina': 'EXTRA',
        'litros_pdf': 0.0,
        'es_duplicada': False,
        'duplicado_info': ''
    }
    
    archivo_pdf = request.files.get('archivo_pdf')
    archivo_xml = request.files.get('archivo_xml')
    tipo_combustible = request.form.get('tipo', '') # 'diesel', 'gasolina', o '' (auto)
    pdf_text = ''
    
    if archivo_pdf and pdfplumber:
        try:
            pdf_bytes = archivo_pdf.read()
            archivo_pdf.seek(0)
            if pdf_bytes:
                import io
                with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                    for page in pdf.pages:
                        t = page.extract_text()
                        if t: pdf_text += t + '\n'
                
                # Extracción de Encabezados PDF (fallback si no hay XML)
                uuid_m = re.search(r'FOLIO FISCAL\s*([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})', pdf_text, re.IGNORECASE)
                if uuid_m and not res['uuid']: res['uuid'] = uuid_m.group(1).strip()
                
                fol_m = re.search(r'FACTURA No\.\s*([A-Z0-9\s-]+)', pdf_text, re.IGNORECASE)
                if fol_m and not res['folio_factura']: res['folio_factura'] = fol_m.group(1).split('\n')[0].strip()
                
                fec_m = re.search(r'FECHA:\s*(\d{4}-\d{2}-\d{2})', pdf_text, re.IGNORECASE)
                if fec_m and not res['fecha']:
                    res['fecha'] = fec_m.group(1)
                    try: res['semana'] = str(datetime.datetime.strptime(res['fecha'], '%Y-%m-%d').isocalendar()[1])
                    except: pass
                
                if not res['proveedor'] and pdf_text.strip():
                    lines = [l.strip() for l in pdf_text.split('\n') if l.strip()]
                    if lines: res['proveedor'] = lines[0]

                # 1. Extracción de Obra y Placa tras Fecha de Vencimiento
                match_venc = re.search(r'Fecha de Vencimiento:\s*\S+\s+(.*)', pdf_text, re.IGNORECASE)
                if match_venc:
                    venc_line = match_venc.group(1).strip()
                    res['obra_texto'] = venc_line
                    
                    placa_m = re.search(r'PLACAS?\s*:?\s*([A-Z0-9]+)', venc_line, re.IGNORECASE)
                    if placa_m:
                        res['placa'] = placa_m.group(1).strip()
                    else:
                        placa_matches = re.findall(r'\b([A-Z0-9]{3,4}[0-9]{3,4}[A-Z0-9]?|[A-Z]{3}[0-9]{4})\b', venc_line)
                        if placa_matches:
                            candidates = [p for p in placa_matches if p not in ['52760', '52790', 'P24814', 'JEC040429LS4', '15101514', '15101515', '32025', '32026']]
                            if candidates:
                                res['placa'] = candidates[-1]

                if not res['placa']:
                    p_all = re.search(r'(?:PLACAS?|PLACA|UNIDAD|VEHICULO)\s*:?\s*([A-Z0-9]{6,8})\b', pdf_text, re.IGNORECASE)
                    if p_all:
                        res['placa'] = p_all.group(1).strip()

                # 2. Tipo de Gasolina desde PDF
                if re.search(r'PREMIUM|SUPREME|91 OCTANOS|15101515|32026|32012', pdf_text, re.IGNORECASE):
                    res['tipo_gasolina'] = 'PREMIUM'
                elif re.search(r'EXTRA|MAGNA|REGULAR|87 OCTANOS|32025|32011|15101514', pdf_text, re.IGNORECASE):
                    res['tipo_gasolina'] = 'EXTRA'

                # 3. Litros desde PDF (por si el XML viene en 0 o sin conceptos)
                lts_m = re.search(r'(\d+(?:\.\d+)?)\s*(?:LTR|Litros|Lts|L)\b', pdf_text, re.IGNORECASE)
                if lts_m:
                    res['litros_pdf'] = round(float(lts_m.group(1)), 2)
        except Exception as e:
            import traceback
            print("PDF Parse Error:", traceback.format_exc())

    # Detección Automática de Combustible si no fue enviado explícitamente
    if not tipo_combustible or tipo_combustible == 'auto':
        if re.search(r'magna|premium|extra|supreme|regular|gasolina|15101514|15101515|32025|32026|32011|32012', pdf_text, re.IGNORECASE):
            tipo_combustible = 'gasolina'
        else:
            tipo_combustible = 'diesel'

    if archivo_xml:
        try:
            tree = ET.parse(archivo_xml)
            root = tree.getroot()
            ns = {'cfdi': 'http://www.sat.gob.mx/cfd/4', 'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'}
            
            res['fecha'] = root.get('Fecha', '').split('T')[0]
            if res['fecha']:
                try: res['semana'] = str(datetime.datetime.strptime(res['fecha'], '%Y-%m-%d').isocalendar()[1])
                except: res['semana'] = ''

            serie = root.get('Serie', '')
            folio_num = root.get('Folio', '')
            res['folio_factura'] = f"{serie}{folio_num}".strip() if (serie or folio_num) else ''

            emisor = root.find('cfdi:Emisor', ns)
            res['proveedor'] = emisor.get('Nombre', '') if emisor is not None else ''

            timbre = root.find('.//tfd:TimbreFiscalDigital', ns)
            if timbre is not None: res['uuid'] = timbre.get('UUID', '')
            
            xml_str = ET.tostring(root, encoding='utf-8').decode('utf-8', errors='ignore').lower()

            for c in root.findall('.//cfdi:Concepto', ns):
                desc = c.get('Descripcion', '').lower()
                clave = c.get('ClaveProdServ', '')
                
                litros = float(c.get('Cantidad', 0))
                if litros <= 0:
                    continue

                precio = float(c.get('ValorUnitario', 0))
                subtotal = float(c.get('Importe', 0))
                iva = 0
                for imp in c.findall('.//cfdi:Traslado', ns):
                    if imp.get('Impuesto') == '002':
                        iva += float(imp.get('Importe', 0))

                is_gas = (clave in ['15101514', '15101515', '15101500', '15101506'] or any(x in desc for x in ['magna', 'premium', 'extra', 'supreme', 'regular', 'gasolina', '32011', '32012', '32025', '32026']))
                item_tipo = 'gasolina' if is_gas else 'diesel'

                if 'premium' in desc or 'supreme' in desc or clave == '15101515' or '32026' in desc:
                    res['tipo_gasolina'] = 'PREMIUM'

                res['cargas'].append({
                    'descripcion': c.get('Descripcion'),
                    'litros': round(litros, 2),
                    'precio': round(precio, 2),
                    'subtotal': round(subtotal, 2),
                    'iva': round(iva, 2),
                    'total': round(subtotal + iva, 2),
                    'tipo': item_tipo
                })
        except Exception as e:
            print("XML Error:", e)

    has_diesel = any(c.get('tipo') == 'diesel' for c in res['cargas'])
    has_gasolina = any(c.get('tipo') == 'gasolina' for c in res['cargas'])

    if has_diesel and has_gasolina:
        tipo_combustible = 'mixta'
        res['es_mixta'] = True
    elif has_gasolina:
        tipo_combustible = 'gasolina'
        res['es_mixta'] = False
    else:
        tipo_combustible = 'diesel'
        res['es_mixta'] = False

    res['combustible'] = tipo_combustible

    # Si las cargas venían vacías en XML o en 0, pero hallamos litros en PDF
    sum_xml_lts = sum(float(c.get('litros', 0)) for c in res['cargas'])
    if sum_xml_lts == 0 and res['litros_pdf'] > 0:
        res['cargas'] = [{
            'descripcion': f"Gasolina {res['tipo_gasolina']} (Lector PDF)",
            'litros': res['litros_pdf'],
            'precio': 0.0,
            'subtotal': 0.0,
            'iva': 0.0,
            'total': 0.0,
            'tipo': 'gasolina' if res['tipo_gasolina'] else 'diesel'
        }]

    # Buscar obra sugerida
    if res['obra_texto']:
        db = get_db()
        obras = db.execute("SELECT nombre, codigo FROM catalogos.obras").fetchall()
        db.close()
        texto = res['obra_texto'].upper()
        if 'PEGASO' in texto and 'ASFALTO' not in texto: res['obra_sugerida'] = 'Maquinaria Pegaso'
        elif 'TRES MARIAS' in texto: res['obra_sugerida'] = 'Lerma - Tres Marías'
        elif 'HUIXQUILUCAN' in texto:
            for o in obras:
                if 'HUIXQUILUCAN' in o['nombre'].upper():
                    res['obra_sugerida'] = o['nombre']
                    break
        if not res['obra_sugerida']:
            for o in obras:
                if o['nombre'].upper() in texto or (o['codigo'] and o['codigo'].upper() in texto):
                    res['obra_sugerida'] = o['nombre']
                    break

    # Checar duplicados
    es_dup, msg_dup = verificar_factura_duplicada(res['uuid'], res['folio_factura'], res['proveedor'])
    res['es_duplicada'] = es_dup
    res['duplicado_info'] = msg_dup

    return jsonify(res)

@app.route('/api/admin/guardar_facturas', methods=['POST'])
def api_guardar_facturas():
    try:
        tipo = request.form.get('tipo', 'diesel') # 'diesel', 'gasolina', o 'mixta'
        datos = request.form.get('datos_json') # Las cargas en JSON string
        import json
        data = json.loads(datos)
        
        archivo_pdf = request.files.get('archivo_pdf')
        archivo_xml = request.files.get('archivo_xml')
        
        pdf_blob = archivo_pdf.read() if archivo_pdf and archivo_pdf.filename else None
        xml_blob = archivo_xml.read() if archivo_xml and archivo_xml.filename else None
        
        semana = str(data.get('semana', '')).replace('Semana ', '').replace('Semana', '').strip()
        obra_nombre = data.get('obra', '')
        placa = str(data.get('placa', '')).strip()
        tipo_gasolina = data.get('tipo_gasolina', 'EXTRA')
        
        db = get_db()
        obra_row = db.execute("SELECT codigo FROM catalogos.obras WHERE nombre=%s", (obra_nombre,)).fetchone()
        obra_codigo = obra_row['codigo'] if obra_row else 'XX'
        
        fecha_factura = data.get('fecha')
        if not fecha_factura: 
            import datetime
            fecha_factura = datetime.date.today().strftime('%Y-%m-%d')
            
        uuid_cfdi = data.get('uuid')
        if not uuid_cfdi:
            import time
            uuid_cfdi = f"SOLO-PDF-{int(time.time())}"
            
        proveedor_final = data.get('proveedor', 'PROVEEDOR')
        if not proveedor_final: proveedor_final = 'PROVEEDOR'
        
        cargas = data.get('cargas', [])
        cargas_diesel = [c for c in cargas if c.get('tipo') == 'diesel']
        cargas_gasolina = [c for c in cargas if c.get('tipo') == 'gasolina']

        if not cargas_diesel and not cargas_gasolina and cargas:
            if tipo == 'gasolina':
                cargas_gasolina = cargas
            else:
                cargas_diesel = cargas

        def get_consecutivo(schema_table):
            folios = db.execute(f"SELECT folio_conciliacion FROM {schema_table} WHERE semana=%s AND folio_conciliacion LIKE 'FA-%%'", (semana,)).fetchall()
            max_c = 0
            for f in folios:
                parts = f['folio_conciliacion'].split('-')
                if len(parts) >= 4:
                    try:
                        num = int(parts[-1])
                        if num > max_c: max_c = num
                    except: pass
            return max_c + 1

        res_folios = []

        if cargas_diesel:
            total_lts_d = sum(float(c.get('litros', 0)) for c in cargas_diesel)
            total_imp_d = sum(float(c.get('total', 0)) for c in cargas_diesel)
            cons_d = get_consecutivo('diesel.facturas')
            folio_final_d = f"FA-{obra_codigo}-{semana}-{cons_d:03d}"
            db.execute('''INSERT INTO diesel.facturas
                (folio_conciliacion, folio_factura, fecha_factura, semana, proveedor, litros_facturados, importe_total, uuid_cfdi, archivo_pdf, archivo_xml, estatus_revision, obra_destino, placa, tipo_gasolina)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'APROBADO', %s, %s, %s)''',
                (folio_final_d, data.get('folio_factura', ''), fecha_factura, semana, proveedor_final, total_lts_d, total_imp_d, uuid_cfdi, pdf_blob, xml_blob, obra_nombre, placa, tipo_gasolina))
            res_folios.append(f"Diésel ({folio_final_d})")

        if cargas_gasolina:
            total_lts_g = sum(float(c.get('litros', 0)) for c in cargas_gasolina)
            total_imp_g = sum(float(c.get('total', 0)) for c in cargas_gasolina)
            cons_g = get_consecutivo('gasolina.facturas')
            folio_final_g = f"FA-{obra_codigo}-{semana}-{cons_g:03d}"
            db.execute('''INSERT INTO gasolina.facturas
                (folio_conciliacion, folio_factura, fecha_factura, semana, proveedor, litros_facturados, importe_total, uuid_cfdi, archivo_pdf, archivo_xml, estatus_revision, obra_destino, placa, tipo_gasolina)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'APROBADO', %s, %s, %s)''',
                (folio_final_g, data.get('folio_factura', ''), fecha_factura, semana, proveedor_final, total_lts_g, total_imp_g, uuid_cfdi, pdf_blob, xml_blob, obra_nombre, placa, tipo_gasolina))
            res_folios.append(f"Gasolina ({folio_final_g})")

        db.commit()
        db.close()
        return jsonify({'success': True, 'folio': ', '.join(res_folios)})
    except Exception as e:
        import traceback
        print("Guardar Factura Error:", traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/admin/jalisco/vales')
def api_jalisco_vales():
    # Helper to calculate the ledger up to the current week
    try:
        db = get_db()
        # Obtenemos todas las semanas ordenadas
        cur = db.execute("SELECT DISTINCT semana FROM diesel.control_vales_jalisco ORDER BY semana ASC")
        semanas_db = cur.fetchall()
        semanas = [s[0] for s in semanas_db]
        
        # Consultar semana extra si hay consumos nuevos
        cur = db.execute("SELECT DISTINCT semana FROM diesel.consumos WHERE obra_destino='BD_JALISCO' ORDER BY semana ASC")
        semanas_cons = cur.fetchall()
        for sc in semanas_cons:
            try:
                sem_num = int(str(sc[0]).replace('Semana ', '').strip())
                if sem_num not in semanas:
                    semanas.append(sem_num)
            except:
                pass
        semanas.sort()
        
        historial = []
        remanente_acumulado = 0.0
        
        for sem in semanas:
            # Obtener el ajuste de la semana
            cur = db.execute("SELECT ajuste_semanal FROM diesel.control_vales_jalisco WHERE semana=%s", (sem,))
            ajuste_row = cur.fetchone()
            ajuste = float(ajuste_row[0]) if ajuste_row and ajuste_row[0] is not None else 0.0
            
            # Obtener cargas de la semana
            cur = db.execute("SELECT SUM(litros) as total FROM diesel.consumos WHERE obra_destino='BD_JALISCO' AND semana=%s AND estatus_revision != 'RECHAZADO'", (str(sem),))
            cargas_row = cur.fetchone()
            cargas = float(cargas_row[0]) if cargas_row and cargas_row[0] is not None else 0.0
            
            # Calcular
            remanente_anterior = remanente_acumulado
            total_disponible = remanente_anterior + ajuste
            remanente_actual = total_disponible - cargas
            
            # Actualizamos acumulado para la siguiente iteracion
            remanente_acumulado = remanente_actual
            
            historial.append({
                'semana': sem,
                'remanente_anterior': round(remanente_anterior, 2),
                'ajuste': round(ajuste, 2),
                'total_disponible': round(total_disponible, 2),
                'cargas': round(cargas, 2),
                'remanente_actual': round(remanente_actual, 2)
            })
            
        # Si se solicita una semana específica, filtramos el resultado
        semana_req = request.args.get('semana')
        if semana_req:
            try: 
                semana_req = int(semana_req)
                historial = [h for h in historial if h['semana'] == semana_req]
                if not historial:
                    # Semana no encontrada, pero si es una semana nueva, devolver default
                    historial = [{
                        'semana': semana_req,
                        'remanente_anterior': round(remanente_acumulado, 2),
                        'ajuste': 0.0,
                        'total_disponible': round(remanente_acumulado, 2),
                        'cargas': 0.0,
                        'remanente_actual': round(remanente_acumulado, 2)
                    }]
            except:
                pass
        
        db.close()
        # Invertir para mostrar lo más reciente primero si no hay filtro
        historial.reverse()
        return jsonify(historial)
    except Exception as e:
        import traceback
        with open('error_jalisco.txt', 'w') as f:
            f.write(traceback.format_exc())
        print("Error en api_jalisco_vales:", e)
        return jsonify([])

@app.route('/api/admin/jalisco/vales/datos/<int:semana>', methods=['GET'])
def api_jalisco_vales_datos(semana):
    try:
        db = get_db()
        
        # Obtener saldo inicial
        row = db.execute("SELECT saldo_inicial_vales FROM diesel.control_vales_jalisco WHERE semana = %s", (semana,)).fetchone()
        saldo_ini = float(row['saldo_inicial_vales']) if row else 0.0
        
        # Obtener ajustes
        ajustes_rows = db.execute("""
            SELECT id, fecha, monto, (recibo_pdf IS NOT NULL) as tiene_pdf
            FROM diesel.jalisco_vales_ajustes
            WHERE semana = %s
            ORDER BY fecha ASC, id ASC
        """, (semana,)).fetchall()
        
        ajustes = []
        for a in ajustes_rows:
            ajustes.append({
                'id': a['id'],
                'fecha': a['fecha'].strftime('%Y-%m-%d') if a['fecha'] else '',
                'monto': float(a['monto']),
                'tiene_pdf': a['tiene_pdf']
            })
            
        db.close()
        return jsonify({"success": True, "saldo_inicial": saldo_ini, "ajustes": ajustes})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

def sincronizar_entradas_vales_jalisco(db):
    try:
        db.execute("DELETE FROM diesel.jalisco_movimientos WHERE tipo_movimiento = 'ENTRADA' AND (equipo_economico IS NULL OR equipo_economico = '')")
        ajustes = db.execute("SELECT id, semana, fecha, monto, recibo_pdf FROM diesel.jalisco_vales_ajustes ORDER BY semana, fecha").fetchall()
        for a in ajustes:
            monto = float(a['monto'] or 0)
            litros = round(monto / 27.0, 2)
            obs = f"Recibo de Vales S{a['semana']} (${monto:,.2f})"
            db.execute("""
                INSERT INTO diesel.jalisco_movimientos
                (fecha, semana, tipo_movimiento, litros, costo_por_litro, importe_total, observaciones, archivo_pdf)
                VALUES (%s, %s, 'ENTRADA', %s, 27.00, %s, %s, %s)
            """, (a['fecha'], a['semana'], litros, monto, obs, psycopg2.Binary(a['recibo_pdf']) if a['recibo_pdf'] else None))
        
        recalcular_saldos_jalisco(db)
    except Exception as e:
        print("Error sincronizando entradas de vales:", e)

@app.route('/api/admin/jalisco/vales/guardar', methods=['POST'])
def api_jalisco_guardar_vales():
    try:
        db = get_db()
        sem_str = str(request.form.get('semana', '')).replace('Semana ', '').replace('Semana', '').strip()
        sem = int(sem_str) if sem_str else 0
        saldo_ini = float(request.form.get('saldo_inicial_vales', 0))
        ajustes_count = int(request.form.get('ajustes_count', 0))
        
        if sem <= 0:
            db.close()
            return jsonify({"success": False, "error": "Debe especificar un número de semana válido."})

        # UPSERT el saldo inicial
        db.execute("""
            INSERT INTO diesel.control_vales_jalisco (semana, saldo_inicial_vales, tipo_combustible) 
            VALUES (%s, %s, 'DIESEL') 
            ON CONFLICT (semana, tipo_combustible) DO UPDATE 
            SET saldo_inicial_vales = EXCLUDED.saldo_inicial_vales
        """, (sem, saldo_ini))

        # 1. Recolectar datos enviados del formulario
        ajustes_data = []
        ids_presentes = []
        for i in range(ajustes_count):
            a_id = request.form.get(f'ajuste_id_{i}')
            a_fecha = request.form.get(f'ajuste_fecha_{i}')
            a_monto_str = request.form.get(f'ajuste_monto_{i}', '0')
            a_monto = float(a_monto_str) if a_monto_str else 0.0
            a_pdf = request.files.get(f'ajuste_pdf_{i}')
            pdf_blob = a_pdf.read() if a_pdf and a_pdf.filename else None
            
            if not a_fecha or a_monto <= 0:
                continue
                
            item = {
                'id': int(a_id) if a_id and a_id.strip() else None,
                'fecha': a_fecha,
                'monto': a_monto,
                'pdf_blob': pdf_blob
            }
            ajustes_data.append(item)
            if item['id']:
                ids_presentes.append(item['id'])

        # 2. Eliminar de la BD los ajustes existentes de esta semana que ya no venían en la lista
        if ids_presentes:
            db.execute("DELETE FROM diesel.jalisco_vales_ajustes WHERE semana = %s AND id != ALL(%s)", (sem, ids_presentes))
        else:
            db.execute("DELETE FROM diesel.jalisco_vales_ajustes WHERE semana = %s", (sem,))

        # 3. Insertar o actualizar cada ajuste
        for item in ajustes_data:
            if item['id']:
                if item['pdf_blob']:
                    db.execute("""
                        UPDATE diesel.jalisco_vales_ajustes 
                        SET fecha=%s, monto=%s, recibo_pdf=%s 
                        WHERE id=%s AND semana=%s
                    """, (item['fecha'], item['monto'], psycopg2.Binary(item['pdf_blob']), item['id'], sem))
                else:
                    db.execute("""
                        UPDATE diesel.jalisco_vales_ajustes 
                        SET fecha=%s, monto=%s 
                        WHERE id=%s AND semana=%s
                    """, (item['fecha'], item['monto'], item['id'], sem))
            else:
                db.execute("""
                    INSERT INTO diesel.jalisco_vales_ajustes (semana, fecha, monto, recibo_pdf) 
                    VALUES (%s, %s, %s, %s)
                """, (sem, item['fecha'], item['monto'], psycopg2.Binary(item['pdf_blob']) if item['pdf_blob'] else None))

        sincronizar_entradas_vales_jalisco(db)
        db.close()
        return jsonify({"success": True})
    except Exception as e:
        import traceback
        print("Error en api_jalisco_guardar_vales:", e)
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/admin/resumen/cosum')
def api_resumen_cosum():
    """Devuelve las facturas asignadas exclusivamente a la obra Sindicato COSUM."""
    db = get_db()
    semana = request.args.get('semana', 'TODOS')
    
    cond_facturas = "WHERE (obra_destino ILIKE %s OR proveedor ILIKE %s)"
    cond_consumos = "WHERE (obra_destino ILIKE %s OR observaciones ILIKE %s)"
    
    params_fac = ['%COSUM%', '%COSUM%']
    params_con = ['%COSUM%', '%COSUM%']
    
    if semana != 'TODOS':
        sem_limpia = str(semana).replace('Semana ', '').strip()
        cond_facturas += " AND semana = %s"
        cond_consumos += " AND semana = %s"
        params_fac.append(sem_limpia)
        params_con.append(sem_limpia)

    try:
        q_d = f"""
            SELECT 'Diésel' as combustible, id, folio_conciliacion, folio_factura, fecha_factura::text as fecha_str,
                   semana, proveedor, litros_facturados, importe_total, obra_destino, uuid_cfdi, '' as observaciones
            FROM diesel.facturas {cond_facturas}
            ORDER BY fecha_factura DESC, id DESC
        """
        facturas_diesel = db.execute(q_d, tuple(params_fac)).fetchall()
        
        q_g = f"""
            SELECT 'Gasolina' as combustible, id, folio_conciliacion, folio_factura, fecha_factura::text as fecha_str,
                   semana, proveedor, litros_facturados, importe_total, obra_destino, uuid_cfdi, '' as observaciones
            FROM gasolina.facturas {cond_facturas}
            ORDER BY fecha_factura DESC, id DESC
        """
        facturas_gasolina = db.execute(q_g, tuple(params_fac)).fetchall()
        
        q_c_diesel = f"""
            SELECT 'Diésel (Consumo)' as combustible, id, folio_conciliacion, folio_conciliacion as folio_factura, fecha::text as fecha_str,
                   semana, origen as proveedor, litros as litros_facturados, importe_total, obra_destino, '' as uuid_cfdi, observaciones
            FROM diesel.consumos {cond_consumos} AND origen = 'FACTURA'
            ORDER BY fecha DESC, id DESC
        """
        consumos_diesel = db.execute(q_c_diesel, tuple(params_con)).fetchall()
        
        todas = [dict(r) for r in (list(facturas_diesel) + list(facturas_gasolina) + list(consumos_diesel))]
        
        tot_litros = sum([float(r.get('litros_facturados') or 0) for r in todas])
        tot_importe = sum([float(r.get('importe_total') or 0) for r in todas])
        
        db.close()
        return jsonify({
            'success': True,
            'facturas': todas,
            'totales': {
                'cantidad': len(todas),
                'litros': round(tot_litros, 2),
                'importe': round(tot_importe, 2)
            }
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        db.close()
        return jsonify({'success': False, 'error': str(e), 'facturas': [], 'totales': {'cantidad': 0, 'litros': 0, 'importe': 0}})

@app.route('/api/admin/jalisco/vales/registrar', methods=['POST'])
def api_jalisco_registrar_vale():
    try:
        db = get_db()
        sem = int(request.form.get('semana', 0))
        monto = float(request.form.get('monto', 0) or 0)
        costo = float(request.form.get('costo_diesel', 27.00) or 27.00)
        fecha = request.form.get('fecha') or datetime.date.today().strftime('%Y-%m-%d')
        obs = request.form.get('observaciones', '')
        
        if sem <= 0 or monto <= 0:
            db.close()
            return jsonify({"success": False, "error": "Debe proporcionar una semana válida y un importe mayor a cero."})
            
        pdf_file = request.files.get('recibo_pdf')
        pdf_blob = pdf_file.read() if pdf_file and pdf_file.filename else None
        
        db.execute("""
            INSERT INTO diesel.jalisco_vales_ajustes (semana, fecha, monto, recibo_pdf)
            VALUES (%s, %s, %s, %s)
        """, (sem, fecha, monto, psycopg2.Binary(pdf_blob) if pdf_blob else None))
        
        sincronizar_entradas_vales_jalisco(db)
        db.close()
        return jsonify({"success": True, "semana": sem, "monto": monto})
    except Exception as e:
        import traceback
        print("Error en api_jalisco_registrar_vale:", e)
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/admin/resumen/gasolina')
def api_resumen_gasolina():
    semana_param = str(request.args.get('semana', '')).replace('Semana ', '').replace('Semana', '').strip()
    if not semana_param or semana_param == 'TODOS':
        semana_num = 30
        es_todos = True
    else:
        try:
            semana_num = int(semana_param)
            es_todos = False
        except:
            semana_num = 30
            es_todos = False

    db = get_db()

    # 1. Garantizar continuidad/arrastre para la semana
    if not es_todos:
        sync_gasolina_autorizaciones_arrastre(db, semana_num)

    # 2. Consultar consumos registrados aprobados para la tabla principal
    if es_todos:
        where_cond = "WHERE c.estatus_revision != 'RECHAZADO'"
        params = ()
    else:
        where_cond = "WHERE c.estatus_revision != 'RECHAZADO' AND c.semana = %s"
        params = (str(semana_num),)

    sql_consumos = f"""
        SELECT 
            c.id, c.fecha, c.semana, c.folio_conciliacion,
            COALESCE(NULLIF(c.conductor, ''), m.responsable, 'General') as responsable,
            COALESCE(NULLIF(c.obra_destino, ''), m.centro_trabajo, 'General') as centro_trabajo,
            COALESCE(c.placa, 'S/P') as placa,
            COALESCE(c.vehiculo, m.unidad_equipo, 'Unidad') as vehiculo,
            COALESCE(c.litros, 0) as litros,
            COALESCE(c.costo_por_litro, 23.90) as costo_por_litro,
            COALESCE(c.importe_total, 0) as carga_monto,
            COALESCE(c.foto_evidencia IS NOT NULL, FALSE) as tiene_foto,
            COALESCE(s.importe_semanal, m.importe_semanal, 0) as autorizado_semanal
        FROM gasolina.consumos c
        LEFT JOIN LATERAL (
            SELECT id, responsable, centro_trabajo, unidad_equipo, importe_semanal
            FROM gasolina.autorizaciones_maestro
            WHERE (c.placa IS NOT NULL AND c.placa != 'S/P' AND UPPER(TRIM(placas)) = UPPER(TRIM(c.placa)))
               OR (c.placa IS NOT NULL AND c.placa != 'S/P' AND (UPPER(placas) LIKE '%%' || UPPER(c.placa) || '%%' OR UPPER(c.placa) LIKE '%%' || UPPER(placas) || '%%'))
               OR (UPPER(TRIM(responsable)) = UPPER(TRIM(c.conductor)) AND UPPER(TRIM(centro_trabajo)) = UPPER(TRIM(c.obra_destino)))
               OR (UPPER(TRIM(unidad_equipo)) = UPPER(TRIM(c.vehiculo)) AND UPPER(TRIM(centro_trabajo)) = UPPER(TRIM(c.obra_destino)))
            ORDER BY 
                CASE 
                    WHEN c.placa IS NOT NULL AND c.placa != 'S/P' AND UPPER(TRIM(placas)) = UPPER(TRIM(c.placa)) THEN 1
                    WHEN c.placa IS NOT NULL AND c.placa != 'S/P' AND (UPPER(placas) LIKE '%%' || UPPER(c.placa) || '%%' OR UPPER(c.placa) LIKE '%%' || UPPER(placas) || '%%') THEN 2
                    WHEN UPPER(TRIM(responsable)) = UPPER(TRIM(c.conductor)) AND UPPER(TRIM(centro_trabajo)) = UPPER(TRIM(c.obra_destino)) THEN 3
                    ELSE 4
                END,
                id ASC
            LIMIT 1
        ) m ON TRUE
        LEFT JOIN gasolina.autorizaciones_semanal s ON (m.id = s.maestro_id AND s.semana = CAST(c.semana AS INTEGER))
        {where_cond}
        ORDER BY c.fecha ASC, c.id ASC
    """
    cargas_raw = db.execute(sql_consumos, params).fetchall()

    unidad_acumulado = {}
    consumos_list = []
    total_cargas_monto = 0.0
    total_cargas_litros = 0.0

    for c in cargas_raw:
        key = (c['semana'], c['placa'], c['vehiculo'], c['responsable'])
        prev_acum = unidad_acumulado.get(key, 0.0)
        carga_m = float(c['carga_monto'])
        new_acum = prev_acum + carga_m
        unidad_acumulado[key] = new_acum

        auth_semanal = float(c['autorizado_semanal'])
        cuanto_queda = auth_semanal - new_acum

        item = {
            'id': c['id'],
            'folio': c['folio_conciliacion'] or f"GAS-{c['id']}",
            'fecha': str(c['fecha']),
            'semana': c['semana'],
            'responsable': c['responsable'],
            'centro_trabajo': c['centro_trabajo'],
            'placa': c['placa'],
            'vehiculo': c['vehiculo'],
            'litros': round(float(c['litros']), 2),
            'costo_por_litro': round(float(c['costo_por_litro']), 2),
            'carga_monto': round(carga_m, 2),
            'autorizado_semanal': round(auth_semanal, 2),
            'cuanto_queda': round(cuanto_queda, 2),
            'tiene_foto': c['tiene_foto']
        }
        consumos_list.append(item)
        total_cargas_monto += carga_m
        total_cargas_litros += float(c['litros'])

    consumos_list.reverse()

    # 3. Resumen por Obra / Centro de Trabajo
    if es_todos:
        sql_obras = """
            SELECT 
                m.centro_trabajo as obra,
                SUM(COALESCE(m.importe_semanal, 0)) as monto_autorizado,
                COALESCE(c_agg.consumo_total, 0) as consumo_real,
                COALESCE(c_agg.litros_totales, 0) as litros_consumidos,
                COALESCE(c_agg.num_cargas, 0) as num_cargas
            FROM gasolina.autorizaciones_maestro m
            LEFT JOIN (
                SELECT 
                    obra_destino,
                    SUM(importe_total) as consumo_total,
                    SUM(litros) as litros_totales,
                    COUNT(*) as num_cargas
                FROM gasolina.consumos
                WHERE estatus_revision != 'RECHAZADO'
                GROUP BY obra_destino
            ) c_agg ON UPPER(TRIM(m.centro_trabajo)) = UPPER(TRIM(c_agg.obra_destino))
            WHERE m.activo = TRUE
            GROUP BY m.centro_trabajo, c_agg.consumo_total, c_agg.litros_totales, c_agg.num_cargas
            ORDER BY monto_autorizado DESC
        """
        params_obras = ()
    else:
        sql_obras = """
            SELECT 
                m.centro_trabajo as obra,
                SUM(COALESCE(s.importe_semanal, m.importe_semanal, 0)) as monto_autorizado,
                COALESCE(c_agg.consumo_total, 0) as consumo_real,
                COALESCE(c_agg.litros_totales, 0) as litros_consumidos,
                COALESCE(c_agg.num_cargas, 0) as num_cargas
            FROM gasolina.autorizaciones_maestro m
            LEFT JOIN gasolina.autorizaciones_semanal s ON (m.id = s.maestro_id AND s.semana = %s)
            LEFT JOIN (
                SELECT 
                    obra_destino,
                    SUM(importe_total) as consumo_total,
                    SUM(litros) as litros_totales,
                    COUNT(*) as num_cargas
                FROM gasolina.consumos
                WHERE estatus_revision != 'RECHAZADO' AND semana = %s
                GROUP BY obra_destino
            ) c_agg ON UPPER(TRIM(m.centro_trabajo)) = UPPER(TRIM(c_agg.obra_destino))
            WHERE m.activo = TRUE
            GROUP BY m.centro_trabajo, c_agg.consumo_total, c_agg.litros_totales, c_agg.num_cargas
            ORDER BY monto_autorizado DESC
        """
        params_obras = (semana_num, str(semana_num))

    obras_raw = db.execute(sql_obras, params_obras).fetchall()
    obras_list = []
    total_presupuesto_obras = 0.0
    total_consumo_obras = 0.0

    for o in obras_raw:
        auth_m = float(o['monto_autorizado'] or 0)
        cons_m = float(o['consumo_real'] or 0)
        rem_m = auth_m - cons_m
        pct = (cons_m / auth_m * 100.0) if auth_m > 0 else 0.0

        obras_list.append({
            'obra': o['obra'],
            'monto_autorizado': round(auth_m, 2),
            'consumo_real': round(cons_m, 2),
            'litros_consumidos': round(float(o['litros_consumidos'] or 0), 2),
            'remanente': round(rem_m, 2),
            'porcentaje_uso': round(pct, 1),
            'num_cargas': int(o['num_cargas'] or 0)
        })
        total_presupuesto_obras += auth_m
        total_consumo_obras += cons_m

    db.close()

    return jsonify({
        'success': True,
        'semana': semana_param,
        'consumos': consumos_list,
        'obras': obras_list,
        'totales': {
            'cargas_monto': round(total_cargas_monto, 2),
            'cargas_litros': round(total_cargas_litros, 2),
            'presupuesto_autorizado': round(total_presupuesto_obras, 2),
            'remanente_total': round(total_presupuesto_obras - total_consumo_obras, 2)
        }
    })


@app.route('/api/admin/resumen/gasolina/gasolinerias', methods=['GET'])
def api_resumen_gasolina_gasolinerias():
    db = get_db()
    semana_param = request.args.get('semana', 'TODOS').strip()
    es_todos = (semana_param.upper() == 'TODOS')

    if es_todos:
        sql_cargas = """
            SELECT id, folio_conciliacion, fecha::text as fecha, semana,
                   COALESCE(NULLIF(gasolineria,''), 'LEVET') as gasolineria,
                   COALESCE(NULLIF(obra_destino,''), 'General') as obra,
                   COALESCE(NULLIF(conductor,''), 'General') as conductor,
                   COALESCE(NULLIF(vehiculo,''), 'Unidad') as vehiculo,
                   COALESCE(placa, 'S/P') as placa,
                   litros, costo_por_litro, importe_total,
                   (foto_evidencia IS NOT NULL) as tiene_foto
            FROM gasolina.consumos
            WHERE estatus_revision != 'RECHAZADO'
            ORDER BY gasolineria, fecha ASC, id ASC
        """
        cargas = db.execute(sql_cargas).fetchall()
        
        sql_facturas = """
            SELECT id, folio_factura, fecha_factura::text as fecha, semana,
                   COALESCE(NULLIF(proveedor,''), 'SIN PROVEEDOR') as proveedor,
                   litros_facturados as litros, importe_total,
                   COALESCE(placa, '') as placa, COALESCE(obra_destino, '') as obra
            FROM gasolina.facturas
            WHERE (estatus_revision IS NULL OR estatus_revision != 'RECHAZADO')
            ORDER BY proveedor, fecha_factura ASC
        """
        facturas = db.execute(sql_facturas).fetchall()
    else:
        semana_num = re.sub(r'\D', '', semana_param) or semana_param
        sql_cargas = """
            SELECT id, folio_conciliacion, fecha::text as fecha, semana,
                   COALESCE(NULLIF(gasolineria,''), 'LEVET') as gasolineria,
                   COALESCE(NULLIF(obra_destino,''), 'General') as obra,
                   COALESCE(NULLIF(conductor,''), 'General') as conductor,
                   COALESCE(NULLIF(vehiculo,''), 'Unidad') as vehiculo,
                   COALESCE(placa, 'S/P') as placa,
                   litros, costo_por_litro, importe_total,
                   (foto_evidencia IS NOT NULL) as tiene_foto
            FROM gasolina.consumos
            WHERE estatus_revision != 'RECHAZADO' AND semana = %s
            ORDER BY gasolineria, fecha ASC, id ASC
        """
        cargas = db.execute(sql_cargas, (semana_num,)).fetchall()
        
        sql_facturas = """
            SELECT id, folio_factura, fecha_factura::text as fecha, semana,
                   COALESCE(NULLIF(proveedor,''), 'SIN PROVEEDOR') as proveedor,
                   litros_facturados as litros, importe_total,
                   COALESCE(placa, '') as placa, COALESCE(obra_destino, '') as obra
            FROM gasolina.facturas
            WHERE (estatus_revision IS NULL OR estatus_revision != 'RECHAZADO') AND semana = %s
            ORDER BY proveedor, fecha_factura ASC
        """
        facturas = db.execute(sql_facturas, (semana_num,)).fetchall()

    def norm_gasolineria(name):
        if not name: return 'LEVET'
        n = name.strip().upper()
        if 'DERIVADO' in n or 'MOBIL' in n or 'CASTILLA' in n:
            return 'MOBIL / DERIVADOS DE PETROLEO'
        if 'LEVET' in n:
            return 'LEVET / SERVICIO LEVET'
        return n

    # Group cargas
    gas_groups = {}
    for c in cargas:
        g_norm = norm_gasolineria(c['gasolineria'])
        if g_norm not in gas_groups:
            gas_groups[g_norm] = {
                'gasolineria_key': g_norm,
                'nombre_gasolineria': g_norm,
                'total_importe': 0.0,
                'total_litros': 0.0,
                'num_cargas': 0,
                'cargas_lista': []
            }
        gas_groups[g_norm]['total_importe'] += float(c['importe_total'] or 0)
        gas_groups[g_norm]['total_litros'] += float(c['litros'] or 0)
        gas_groups[g_norm]['num_cargas'] += 1
        gas_groups[g_norm]['cargas_lista'].append({
            'id': c['id'],
            'folio': c['folio_conciliacion'] or f"GAS-{c['id']}",
            'fecha': c['fecha'],
            'semana': c['semana'],
            'obra': c['obra'],
            'conductor': c['conductor'],
            'vehiculo': c['vehiculo'],
            'placa': c['placa'],
            'litros': round(float(c['litros'] or 0), 2),
            'importe': round(float(c['importe_total'] or 0), 2),
            'tiene_foto': c['tiene_foto']
        })

    # Group facturas
    fac_groups = {}
    for f in facturas:
        p_norm = norm_gasolineria(f['proveedor'])
        if p_norm not in fac_groups:
            fac_groups[p_norm] = {
                'nombre_proveedor': p_norm,
                'total_importe': 0.0,
                'total_litros': 0.0,
                'facturas_lista': []
            }
        fac_groups[p_norm]['total_importe'] += float(f['importe_total'] or 0)
        fac_groups[p_norm]['total_litros'] += float(f['litros'] or 0)
        fac_groups[p_norm]['facturas_lista'].append({
            'id': f['id'],
            'folio': f['folio_factura'],
            'fecha': f['fecha'],
            'placa': f['placa'],
            'obra': f['obra'],
            'litros': round(float(f['litros'] or 0), 2),
            'importe': round(float(f['importe_total'] or 0), 2)
        })

    todas_gas = set(list(gas_groups.keys()) + list(fac_groups.keys()))
    conciliacion_list = []
    gasolinerias_cargas_list = []

    for g in sorted(todas_gas):
        imp_cargas = gas_groups[g]['total_importe'] if g in gas_groups else 0.0
        lts_cargas = gas_groups[g]['total_litros'] if g in gas_groups else 0.0
        num_c = gas_groups[g]['num_cargas'] if g in gas_groups else 0
        cargas_l = gas_groups[g]['cargas_lista'] if g in gas_groups else []

        imp_facs = fac_groups[g]['total_importe'] if g in fac_groups else 0.0
        lts_facs = fac_groups[g]['total_litros'] if g in fac_groups else 0.0
        facs_l = fac_groups[g]['facturas_lista'] if g in fac_groups else []

        # Enrich cargas with matching factura folio
        cargas_concil = []
        for c in cargas_l:
            c_copy = dict(c)
            matched_fac = None
            if c_copy['placa'] and c_copy['placa'] != 'S/P':
                for f in facs_l:
                    if f['placa'] and f['placa'].upper().strip() == c_copy['placa'].upper().strip():
                        matched_fac = f['folio']
                        break
            if not matched_fac:
                for f in facs_l:
                    if abs(f['importe'] - c_copy['importe']) < 2.0:
                        matched_fac = f['folio']
                        break
            c_copy['factura_relacionada'] = matched_fac or 'Sin Factura'
            cargas_concil.append(c_copy)

        diff_imp = imp_facs - imp_cargas
        diff_lts = lts_facs - lts_cargas

        if abs(diff_imp) < 1.0:
            estatus = 'Conciliado'
        elif diff_imp > 0:
            estatus = 'Pendiente Cargar Ticket'
        else:
            estatus = 'Excedente Cargas'

        gasolinerias_cargas_list.append({
            'gasolineria_key': g,
            'nombre_gasolineria': g,
            'total_importe': round(imp_cargas, 2),
            'total_litros': round(lts_cargas, 2),
            'num_cargas': num_c,
            'cargas_lista': cargas_l
        })

        conciliacion_list.append({
            'gasolineria_key': g,
            'nombre_mostrar': g,
            'facturado_importe': round(imp_facs, 2),
            'facturado_litros': round(lts_facs, 2),
            'capturado_importe': round(imp_cargas, 2),
            'capturado_litros': round(lts_cargas, 2),
            'diferencia_importe': round(diff_imp, 2),
            'diferencia_litros': round(diff_lts, 2),
            'estatus': estatus,
            'facturas_lista': facs_l,
            'cargas_lista': cargas_concil
        })

    db.close()

    return jsonify({
        'success': True,
        'semana': semana_param,
        'gasolinerias_cargas': gasolinerias_cargas_list,
        'conciliacion_facturas': conciliacion_list
    })

@app.route('/api/admin/jalisco/vales/pdf/<int:ajuste_id>')
def api_jalisco_ajuste_pdf(ajuste_id):
    try:
        db = get_db()
        row = db.execute("SELECT recibo_pdf FROM diesel.jalisco_vales_ajustes WHERE id = %s", (ajuste_id,)).fetchone()
        db.close()
        
        if not row or not row['recibo_pdf']:
            return "No hay archivo PDF para este ajuste.", 404
            
        from flask import make_response
        response = make_response(bytes(row['recibo_pdf']))
        response.headers.set('Content-Type', 'application/pdf')
        response.headers.set('Content-Disposition', f'inline; filename="ajuste_{ajuste_id}.pdf"')
        return response
    except Exception as e:
        return str(e), 500

# ═══════════════════════════════════════════════════════════════════════════════
# API: RESUMEN GENERAL DE GASOLINA (Topes, Consumo Real, Extraordinarios)
# ═══════════════════════════════════════════════════════════════════════════════
@app.route('/api/admin/resumen/gasolina_legacy')
def api_resumen_gasolina_legacy():
    semana = str(request.args.get('semana', '')).replace('Semana ', '').replace('Semana', '').strip()
    if not semana or semana == 'TODOS':
        semana = '26'

    db = get_db()
    try:
        rows = db.execute("""
            SELECT 
                COALESCE(ec.vehiculo, 'Unidad') as vehiculo,
                COALESCE(ec.placa, '') as placa,
                COALESCE(ec.responsable, 'General') as responsable,
                COALESCE(ec.obra_destino, 'General') as obra_destino,
                COALESCE(ec.importe_autorizado, 0) as importe_autorizado,
                COALESCE(ec.consumo_real, 0) as consumo_real,
                COALESCE(ec.diferencia, 0) as diferencia,
                COALESCE(ec.estatus, 'OK') as estatus
            FROM gasolina.estados_cuenta ec
            WHERE ec.semana = %s
            ORDER BY ec.importe_autorizado DESC, ec.vehiculo
        """, (semana,)).fetchall()

        result = []
        totales = {
            'monto_autorizado': 0.0,
            'consumo_real': 0.0,
            'cargas_extraordinarias': 0.0,
            'cnt_extraordinarias': 0,
            'diferencia': 0.0,
            'vehiculos_excedidos': 0
        }

        for r in rows:
            veh_ref = r['vehiculo']
            placa_ref = r['placa']
            
            cur_extra = db.execute("""
                SELECT SUM(importe_total) as extra_monto, COUNT(*) as cnt
                FROM gasolina.consumos
                WHERE semana = %s AND (vehiculo ILIKE %s OR placa ILIKE %s)
                  AND observaciones ILIKE '%%CARGA EXTRAORDINARIA%%'
                  AND estatus_revision != 'RECHAZADO'
            """, (semana, f"%{veh_ref}%", f"%{placa_ref}%" if placa_ref else f"%{veh_ref}%")).fetchone()

            extra_monto = float(cur_extra['extra_monto'] or 0) if cur_extra else 0.0
            extra_cnt = int(cur_extra['cnt'] or 0) if cur_extra else 0

            imp_auth = float(r['importe_autorizado'] or 0)
            cons_real = float(r['consumo_real'] or 0)
            dif = float(r['diferencia'] if r['diferencia'] is not None else (imp_auth - cons_real))
            excedido = cons_real > imp_auth and imp_auth > 0

            totales['monto_autorizado'] += imp_auth
            totales['consumo_real'] += cons_real
            totales['cargas_extraordinarias'] += extra_monto
            totales['cnt_extraordinarias'] += extra_cnt
            totales['diferencia'] += dif
            if excedido:
                totales['vehiculos_excedidos'] += 1

            result.append({
                'vehiculo': r['vehiculo'],
                'placa': r['placa'] or 'N/A',
                'responsable': r['responsable'],
                'obra_destino': r['obra_destino'],
                'importe_autorizado': imp_auth,
                'consumo_real': cons_real,
                'cargas_extraordinarias_monto': extra_monto,
                'cargas_extraordinarias_cnt': extra_cnt,
                'diferencia': dif,
                'excedido': excedido,
                'estatus_label': f"⚠️ Excedido por ${abs(dif):,.2f}" if excedido else f"✅ En Regla (+${dif:,.2f})"
            })

        db.close()
        return jsonify({
            'success': True,
            'semana': semana,
            'data': result,
            'totales': totales
        })
    except Exception as e:
        db.close()
        return jsonify({'success': False, 'error': str(e)}), 500

# ═══════════════════════════════════════════════════════════════════════════════
# API: RESUMEN DE REGISTROS EN OBSERVACIÓN (Disputa / Bajo Investigación)
# ═══════════════════════════════════════════════════════════════════════════════
@app.route('/api/admin/resumen/observaciones')
def api_resumen_observaciones():
    semana = str(request.args.get('semana', '')).replace('Semana ', '').replace('Semana', '').strip()
    db = get_db()
    try:
        results = []
        cond_sem = "AND semana = %s" if semana and semana != 'TODOS' else ""
        params = [semana] if semana and semana != 'TODOS' else []

        # 1. Diesel Consumos
        rows_dc = db.execute(f"""
            SELECT id, folio_conciliacion, fecha, semana, obra_destino, equipo_economico, equipo, litros, importe_total, responsable, observaciones, estatus_revision
            FROM diesel.consumos
            WHERE estatus_revision = 'OBSERVACION' {cond_sem}
            ORDER BY id DESC
        """, params).fetchall()
        for r in rows_dc:
            results.append({
                'modulo': '🛢 Diésel (Consumo)',
                'id': r['id'],
                'folio': r['folio_conciliacion'],
                'fecha': str(r['fecha']),
                'semana': r['semana'],
                'obra': r['obra_destino'] or 'N/A',
                'equipo': f"{r['equipo_economico'] or ''} {r['equipo'] or ''}".strip(),
                'litros': float(r['litros'] or 0),
                'importe': float(r['importe_total'] or 0),
                'responsable': r['responsable'] or 'N/A',
                'observaciones': r['observaciones'] or 'Puesto en observación por mesa de control',
                'estatus': r['estatus_revision']
            })

        # 2. Gasolina Consumos
        rows_gc = db.execute(f"""
            SELECT id, folio_conciliacion, fecha, semana, obra_destino, vehiculo, placa, litros, importe_total, conductor, observaciones, estatus_revision
            FROM gasolina.consumos
            WHERE estatus_revision = 'OBSERVACION' {cond_sem}
            ORDER BY id DESC
        """, params).fetchall()
        for r in rows_gc:
            results.append({
                'modulo': '⛽ Gasolina (Consumo)',
                'id': r['id'],
                'folio': r['folio_conciliacion'],
                'fecha': str(r['fecha']),
                'semana': r['semana'],
                'obra': r['obra_destino'] or 'N/A',
                'equipo': f"{r['vehiculo'] or ''} {r['placa'] or ''}".strip(),
                'litros': float(r['litros'] or 0),
                'importe': float(r['importe_total'] or 0),
                'responsable': r['conductor'] or 'N/A',
                'observaciones': r['observaciones'] or 'Puesto en observación por mesa de control',
                'estatus': r['estatus_revision']
            })

        # 3. Diesel Facturas
        rows_df = db.execute(f"""
            SELECT id, folio_factura, fecha_factura, semana, proveedor, litros_facturados, importe_total, obra_destino, estatus_revision
            FROM diesel.facturas
            WHERE estatus_revision = 'OBSERVACION' {cond_sem}
            ORDER BY id DESC
        """, params).fetchall()
        for r in rows_df:
            results.append({
                'modulo': '🧾 Factura Diésel',
                'id': r['id'],
                'folio': r['folio_factura'],
                'fecha': str(r['fecha_factura']),
                'semana': r['semana'],
                'obra': r['obra_destino'] or 'N/A',
                'equipo': r['proveedor'] or 'N/A',
                'litros': float(r['litros_facturados'] or 0),
                'importe': float(r['importe_total'] or 0),
                'responsable': r['proveedor'] or 'N/A',
                'observaciones': 'Factura en disputa / bajo revisión',
                'estatus': r['estatus_revision']
            })

        db.close()
        return jsonify({'success': True, 'count': len(results), 'data': results})
    except Exception as e:
        db.close()
        return jsonify({'success': False, 'error': str(e)}), 500

# ═══════════════════════════════════════════════════════════════════════════════
# API: CANCELACIÓN DE FACTURAS (Con Respaldo y Evidencia Obligatoria)
# ═══════════════════════════════════════════════════════════════════════════════
@app.route('/api/admin/cancelar_factura', methods=['POST'])
def api_cancelar_factura():
    try:
        modulo = request.form.get('modulo', 'diesel').lower()
        factura_id = request.form.get('id')
        motivo = request.form.get('motivo_cancelacion', '').strip()
        archivo = request.files.get('archivo_cancelacion')
        
        if not factura_id or not motivo:
            return jsonify({'success': False, 'error': 'El motivo de cancelación es obligatorio.'})
        if not archivo or not archivo.filename:
            return jsonify({'success': False, 'error': 'Es obligatorio adjuntar el comprobante o acuse SAT de cancelación (PDF/Imagen).'})

        archivo_bytes = archivo.read()
        db = get_db()
        
        table_name = 'diesel.facturas' if modulo == 'diesel' else 'gasolina.facturas'
        backup_table = 'diesel.facturas_respaldo' if modulo == 'diesel' else 'gasolina.facturas_respaldo'
        
        orig = db.execute(f"SELECT * FROM {table_name} WHERE id = %s", (factura_id,)).fetchone()
        if not orig:
            db.close()
            return jsonify({'success': False, 'error': 'Factura no encontrada.'})
            
        orig_dict = dict(orig)
        
        if modulo == 'diesel':
            db.execute(f"""
                INSERT INTO {backup_table}
                (folio_conciliacion, folio_factura, fecha_factura, semana, proveedor, punto_de_carga, litros_facturados, precio_unitario, importe, iva, importe_total, uuid_cfdi, archivo_pdf, archivo_xml, estatus_revision, obra_destino, estatus_pago, motivo_cancelacion, archivo_cancelacion, fecha_cancelacion)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'RESPALDO_CANCELADA', %s, %s, %s, %s, CURRENT_TIMESTAMP)
            """, (
                orig_dict.get('folio_conciliacion'), orig_dict.get('folio_factura'), orig_dict.get('fecha_factura'), orig_dict.get('semana'), orig_dict.get('proveedor'), orig_dict.get('punto_de_carga'), orig_dict.get('litros_facturados'), orig_dict.get('precio_unitario'), orig_dict.get('importe'), orig_dict.get('iva'), orig_dict.get('importe_total'), orig_dict.get('uuid_cfdi'), orig_dict.get('archivo_pdf'), orig_dict.get('archivo_xml'), orig_dict.get('obra_destino'), orig_dict.get('estatus_pago'), motivo, archivo_bytes
            ))
        else:
            db.execute(f"""
                INSERT INTO {backup_table}
                (folio_conciliacion, folio_factura, fecha_factura, semana, proveedor, litros_facturados, importe_total, uuid_cfdi, archivo_pdf, archivo_xml, estatus_revision, obra_destino, motivo_cancelacion, archivo_cancelacion, fecha_cancelacion)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'RESPALDO_CANCELADA', %s, %s, %s, CURRENT_TIMESTAMP)
            """, (
                orig_dict.get('folio_conciliacion'), orig_dict.get('folio_factura'), orig_dict.get('fecha_factura'), orig_dict.get('semana'), orig_dict.get('proveedor'), orig_dict.get('litros_facturados'), orig_dict.get('importe_total'), orig_dict.get('uuid_cfdi'), orig_dict.get('archivo_pdf'), orig_dict.get('archivo_xml'), orig_dict.get('obra_destino'), motivo, archivo_bytes
            ))

        db.execute(f"""
            UPDATE {table_name}
            SET estatus_revision = 'CANCELADA',
                motivo_cancelacion = %s,
                archivo_cancelacion = %s,
                fecha_cancelacion = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (motivo, archivo_bytes, factura_id))

        registrar_auditoria(db, table_name, factura_id, 'CANCELAR_FACTURA', {'uuid': orig_dict.get('uuid_cfdi'), 'folio': orig_dict.get('folio_factura')}, {'motivo': motivo})
        db.commit()
        db.close()
        return jsonify({'success': True, 'message': 'Factura cancelada exitosamente y respaldada.'})
    except Exception as e:
        db.close()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/ver_archivo_cancelacion')
def api_ver_archivo_cancelacion():
    modulo = request.args.get('modulo', 'diesel').lower()
    factura_id = request.args.get('id')
    db = get_db()
    table_name = 'diesel.facturas' if modulo == 'diesel' else 'gasolina.facturas'
    row = db.execute(f"SELECT archivo_cancelacion FROM {table_name} WHERE id = %s", (factura_id,)).fetchone()
    db.close()
    if row and row['archivo_cancelacion']:
        import io
        return send_file(io.BytesIO(row['archivo_cancelacion']), mimetype='application/pdf')
    return "Archivo de cancelación no encontrado", 404

# ═══════════════════════════════════════════════════════════════════════════════
# API: RESUMEN JALISCO — tabla por semana (saldo vales, importe, saldo final, ajuste)
# ═══════════════════════════════════════════════════════════════════════════════
@app.route('/api/admin/resumen/jalisco')
def api_resumen_jalisco():
    """
    Devuelve resumen semanal de Jalisco (Lógica Original):
    - Saldo Inicial: Saldo de vales de control_vales_jalisco (o suma de vales registrados)
    - Importe: Suma de consumos/salidas de jalisco_movimientos
    - Ajuste: Suma de vales registrados en la semana
    - Saldo Final: Saldo Inicial - Importe
    """
    try:
        db = get_db()

        # 1. Cargar saldo_inicial_vales de control_vales_jalisco
        vales_map = {}
        for row in db.execute("""
            SELECT semana, 
                   COALESCE(saldo_inicial_vales, 0) as saldo_ini
            FROM diesel.control_vales_jalisco
            ORDER BY semana
        """).fetchall():
            vales_map[int(row['semana'])] = {
                'saldo_ini': float(row['saldo_ini']),
                'ajuste':    0.0
            }

        # 2. Cargar suma de vales/ajustes registrados por semana
        for row in db.execute("""
            SELECT semana, SUM(monto) as total_ajuste
            FROM diesel.jalisco_vales_ajustes
            GROUP BY semana
        """).fetchall():
            sem = int(row['semana'])
            if sem not in vales_map:
                vales_map[sem] = {'saldo_ini': 0.0, 'ajuste': 0.0}
            vales_map[sem]['ajuste'] = float(row['total_ajuste'] or 0.0)

        # Semanas únicas con movimientos
        semanas_movs = [int(r['semana']) for r in db.execute("""
            SELECT DISTINCT semana FROM diesel.jalisco_movimientos
            ORDER BY semana ASC
        """).fetchall()]
        
        semanas = sorted(list(set(list(vales_map.keys()) + semanas_movs)))

        filas   = []
        tot_saldo_ini = 0.0
        tot_importe   = 0.0
        tot_ajuste    = 0.0
        saldo_anterior = 0.0

        for sem in semanas:
            sem = int(sem)
            v = vales_map.get(sem, {'saldo_ini': 0.0, 'ajuste': 0.0})
            ajuste = v['ajuste']

            # Regla del usuario:
            # Para semanas históricas (< 30), tomar saldo_ini registrado en control_vales_jalisco
            # Para semana 30 en adelante (>= 30), Saldo Inicial = Saldo Final de semana anterior + Ajuste / Vales
            if sem < 30:
                saldo_ini = v['saldo_ini'] if v['saldo_ini'] > 0 else ajuste
            else:
                saldo_ini = saldo_anterior + ajuste

            # Importe = SALIDAS + movimientos de tipo AJUSTE en jalisco_movimientos
            imp_row = db.execute("""
                SELECT COALESCE(SUM(importe_total), 0) as v
                FROM diesel.jalisco_movimientos
                WHERE semana = %s AND tipo_movimiento IN ('SALIDA','AJUSTE')
            """, (sem,)).fetchone()
            importe = float(imp_row['v'] or 0)

            # Saldo final = Saldo inicial - Importe de salidas
            saldo_final = saldo_ini - importe

            # Guardar saldo_final para la siguiente semana
            saldo_anterior = saldo_final

            tot_saldo_ini += saldo_ini
            tot_importe   += importe
            tot_ajuste    += ajuste

            filas.append({
                'semana':        f'Semana {sem}',
                'semana_num':    sem,
                'saldo_inicial': round(saldo_ini, 2),
                'ajuste':        round(ajuste, 2),
                'importe':       round(importe, 2),
                'saldo_final':   round(saldo_final, 2),
            })

        db.close()

        last_saldo_final = filas[-1]['saldo_final'] if filas else 0.0

        return jsonify({
            'filas': filas,
            'totales': {
                'saldo_inicial': round(tot_saldo_ini, 2),
                'importe':       round(tot_importe, 2),
                'ajuste':        round(tot_ajuste, 2),
                'saldo_final':   round(last_saldo_final, 2),
            }
        })
    except Exception as e:
        import traceback
        print("ERROR api_resumen_jalisco:", traceback.format_exc())
        return jsonify({'error': str(e), 'filas': [], 'totales': {}})

# ═══════════════════════════════════════════════════════════════════════════════
# API: REPORTE EXCEL JALISCO (Pestañas por semana + Resumen General Vales + Cargas Diarias)
# ═══════════════════════════════════════════════════════════════════════════════
@app.route('/api/admin/jalisco/reporte/excel')
def api_jalisco_reporte_excel():
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from openpyxl.utils import get_column_letter
        from collections import OrderedDict
        import io, datetime as dt_module

        db = get_db()

        COL_HDR_FILL   = '1E293B'   # Encabezado principal (Oscuro)
        COL_TITLE_FILL = '1E3A5F'   # Encabezado secundario (Azul marino)
        COL_ALT1       = 'FFFFFF'
        COL_ALT2       = 'F8FAFC'
        COL_TOTAL_FILL = 'EFF6FF'
        WHITE          = 'FFFFFF'

        def fill(hex_color):
            return PatternFill("solid", fgColor=hex_color)

        def font(bold=False, color='000000', size=10, name='Calibri'):
            return Font(bold=bold, color=color, size=size, name=name)

        def align(h='center', v='center', wrap=False):
            return Alignment(horizontal=h, vertical=v, wrap_text=wrap)

        def thin_border():
            s = Side(style='thin', color='CBD5E1')
            return Border(left=s, right=s, top=s, bottom=s)

        def thick_border():
            s = Side(style='medium', color='1E293B')
            return Border(left=s, right=s, top=s, bottom=s)

        wb = openpyxl.Workbook()
        wb.remove(wb.active)  # Quitar hoja inicial vacía

        # 1. Obtener todas las semanas disponibles de Jalisco
        vales_rows = db.execute("SELECT semana, saldo_inicial_vales FROM diesel.control_vales_jalisco ORDER BY semana").fetchall()
        vales_map = {int(r['semana']): float(r['saldo_inicial_vales'] or 0) for r in vales_rows}

        ajustes_rows = db.execute("SELECT semana, fecha, monto, (recibo_pdf IS NOT NULL) as tiene_pdf, id FROM diesel.jalisco_vales_ajustes ORDER BY semana, fecha, id").fetchall()
        ajustes_by_sem = {}
        ajustes_tot_map = {}
        for r in ajustes_rows:
            sem = int(r['semana'])
            if sem not in ajustes_by_sem: ajustes_by_sem[sem] = []
            ajustes_by_sem[sem].append(r)
            ajustes_tot_map[sem] = ajustes_tot_map.get(sem, 0.0) + float(r['monto'] or 0)

        movs_rows = db.execute("""
            SELECT semana, fecha::text as fecha_str, litros, equipo_economico, equipo, tipo_movimiento, importe_total, observaciones
            FROM diesel.jalisco_movimientos
            ORDER BY semana, fecha, id
        """).fetchall()
        movs_by_sem = {}
        movs_semanas = set()
        for r in movs_rows:
            sem = int(r['semana'])
            movs_semanas.add(sem)
            if sem not in movs_by_sem: movs_by_sem[sem] = []
            movs_by_sem[sem].append(r)

        todas_semanas = sorted(list(set(list(vales_map.keys()) + list(ajustes_tot_map.keys()) + list(movs_semanas))))

        # ── HOJA 1: RESUMEN GENERAL VALES JALISCO ───────────────────────────
        ws_gen = wb.create_sheet(title="Resumen Vales General")
        ws_gen.views.sheetView[0].showGridLines = True

        ws_gen.merge_cells("A1:E1")
        cell_t = ws_gen["A1"]
        cell_t.value = "🚧 JALISCO — RESUMEN GENERAL DE VALES Y MOVIMIENTOS"
        cell_t.font = font(bold=True, color=WHITE, size=13)
        cell_t.fill = fill(COL_HDR_FILL)
        cell_t.alignment = align('left', 'center')
        ws_gen.row_dimensions[1].height = 30

        headers_gen = ["SEMANA", "SALDO INICIAL (VALES $)", "SUMA DE IMPORTE (SALIDAS)", "AJUSTES ($)", "SALDO FINAL (VALES $)"]
        ws_gen.row_dimensions[3].height = 24
        for col_idx, text in enumerate(headers_gen, 1):
            c = ws_gen.cell(row=3, column=col_idx)
            c.value = text
            c.font = font(bold=True, color=WHITE, size=10)
            c.fill = fill(COL_TITLE_FILL)
            c.alignment = align('center' if col_idx==1 else 'right', 'center')
            c.border = thin_border()

        row_idx = 4
        tot_ini = 0.0
        tot_imp = 0.0
        tot_aj = 0.0

        last_s_fin = 0.0
        for sem in todas_semanas:
            s_ini = vales_map.get(sem, 0.0)
            s_aj  = ajustes_tot_map.get(sem, 0.0)
            
            m_list = movs_by_sem.get(sem, [])
            s_imp = sum([(float(m['importe_total']) if m.get('importe_total') else (float(m['litros'] or 0) * (23.97 if 'GASOLINA' in (str(m.get('equipo_economico') or '')+' '+str(m.get('equipo') or '')+' '+str(m.get('observaciones') or '')).upper() else 27.0))) for m in m_list if m['tipo_movimiento'] in ('SALIDA', 'AJUSTE')])

            s_fin = s_ini - s_imp
            last_s_fin = s_fin

            tot_ini += s_ini
            tot_imp += s_imp
            tot_aj  += s_aj

            ws_gen.cell(row=row_idx, column=1, value=f"Semana {sem}").alignment = align('center', 'center')
            ws_gen.cell(row=row_idx, column=2, value=s_ini).number_format = '"$"#,##0.00'
            ws_gen.cell(row=row_idx, column=3, value=s_imp).number_format = '"$"#,##0.00'
            ws_gen.cell(row=row_idx, column=4, value=s_aj).number_format = '"$"#,##0.00'
            ws_gen.cell(row=row_idx, column=5, value=s_fin).number_format = '"$"#,##0.00'

            bg = COL_ALT2 if row_idx % 2 == 0 else COL_ALT1
            for c_i in range(1, 6):
                cell = ws_gen.cell(row=row_idx, column=c_i)
                cell.font = font(size=10, bold=(c_i==5))
                cell.fill = fill(bg)
                cell.border = thin_border()
                if c_i > 1: cell.alignment = align('right', 'center')

            row_idx += 1

        # Totales fila general
        ws_gen.cell(row=row_idx, column=1, value="TOTAL GENERAL").alignment = align('center', 'center')
        ws_gen.cell(row=row_idx, column=2, value=tot_ini).number_format = '"$"#,##0.00'
        ws_gen.cell(row=row_idx, column=3, value=tot_imp).number_format = '"$"#,##0.00'
        ws_gen.cell(row=row_idx, column=4, value=tot_aj).number_format = '"$"#,##0.00'
        ws_gen.cell(row=row_idx, column=5, value=last_s_fin).number_format = '"$"#,##0.00'

        for c_i in range(1, 6):
            cell = ws_gen.cell(row=row_idx, column=c_i)
            cell.font = font(bold=True, size=10, color='1E3A5F')
            cell.fill = fill(COL_TOTAL_FILL)
            cell.border = thick_border()
            if c_i > 1: cell.alignment = align('right', 'center')

        for col in ws_gen.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = get_column_letter(col[0].column)
            ws_gen.column_dimensions[col_letter].width = max(max_len + 4, 22)


        # ── HOJAS POR SEMANA ────────────────────────────────────────────────
        for sem in todas_semanas:
            ws = wb.create_sheet(title=f"Semana {sem}")
            ws.views.sheetView[0].showGridLines = True

            # Título Semana
            ws.merge_cells("A1:D1")
            t_cell = ws["A1"]
            t_cell.value = f"🇲🇽 BASE JALISCO — CONTROL DE VALES Y CONSUMO (SEMANA {sem})"
            t_cell.font = font(bold=True, color=WHITE, size=11)
            t_cell.fill = fill(COL_HDR_FILL)
            t_cell.alignment = align('left', 'center')
            ws.row_dimensions[1].height = 28

            # SECCIÓN 1: VALES DE LA SEMANA
            s_ini = vales_map.get(sem, 0.0)
            m_list = movs_by_sem.get(sem, [])
            s_imp = sum([(float(m['importe_total']) if m.get('importe_total') else (float(m['litros'] or 0) * (23.97 if 'GASOLINA' in (str(m.get('equipo_economico') or '')+' '+str(m.get('equipo') or '')+' '+str(m.get('observaciones') or '')).upper() else 27.0))) for m in m_list if m['tipo_movimiento'] in ('SALIDA', 'AJUSTE')])
            s_aj  = ajustes_tot_map.get(sem, 0.0)
            s_fin = s_ini - s_imp

            ws.cell(row=3, column=1, value="CONTROL FINANCIERO DE VALES (PESOS)").font = font(bold=True, color='1E3A5F', size=10)

            vales_hdrs = ["SALDO INICIAL", "CONSUMIDO EN MÁQUINAS", "AJUSTES EXTRA", "SALDO FINAL DISPONIBLE"]
            for c_i, h in enumerate(vales_hdrs, 1):
                c = ws.cell(row=4, column=c_i, value=h)
                c.font = font(bold=True, color=WHITE, size=9)
                c.fill = fill(COL_TITLE_FILL)
                c.alignment = align('center', 'center')
                c.border = thin_border()

            vals = [s_ini, s_imp, s_aj, s_fin]
            for c_i, v in enumerate(vals, 1):
                c = ws.cell(row=5, column=c_i, value=v)
                c.font = font(bold=True, size=10)
                c.number_format = '"$"#,##0.00'
                c.alignment = align('right', 'center')
                c.fill = fill(COL_TOTAL_FILL if c_i==4 else COL_ALT1)
                c.border = thin_border()

            ajs_sem = ajustes_by_sem.get(sem, [])
            r_curr = 7
            if ajs_sem:
                ws.cell(row=r_curr, column=1, value="DESGLOSE DE AJUSTES EXTRA (RECIBOS/VALES)").font = font(bold=True, size=9, color='475569')
                r_curr += 1
                aj_hdrs = ["ID", "FECHA REGISTRO", "MONTO ($)", "ESTADO PDF"]
                for c_i, h in enumerate(aj_hdrs, 1):
                    c = ws.cell(row=r_curr, column=c_i, value=h)
                    c.font = font(bold=True, color=WHITE, size=8)
                    c.fill = fill('475569')
                    c.alignment = align('center', 'center')
                    c.border = thin_border()
                r_curr += 1

                for a_item in ajs_sem:
                    ws.cell(row=r_curr, column=1, value=f"#{a_item['id']}").alignment = align('center', 'center')
                    f_str = a_item['fecha'].strftime('%Y-%m-%d') if a_item['fecha'] else '-'
                    ws.cell(row=r_curr, column=2, value=f_str).alignment = align('center', 'center')
                    c_m = ws.cell(row=r_curr, column=3, value=float(a_item['monto'] or 0))
                    c_m.number_format = '"$"#,##0.00'
                    c_m.alignment = align('right', 'center')
                    ws.cell(row=r_curr, column=4, value="PDF Guardado" if a_item.get('tiene_pdf') else "Sin PDF").alignment = align('center', 'center')

                    for c_i in range(1, 5):
                        cell = ws.cell(row=r_curr, column=c_i)
                        cell.font = font(size=9)
                        cell.border = thin_border()
                    r_curr += 1

                r_curr += 1

            # SECCIÓN 2: CONSUMO DIARIO (MISMO FORMATO EXCEL DE REFERENCIA `▶ Base Jalisco`)
            ws.cell(row=r_curr, column=1, value="▶ Base Jalisco").font = font(bold=True, color='1E293B', size=11)
            r_curr += 1

            diario_hdrs = ["DÍA", "LITROS CONSUMIDOS", "PRECIO PROM. ($/L)", "IMPORTE TOTAL"]
            for c_i, h in enumerate(diario_hdrs, 1):
                c = ws.cell(row=r_curr, column=c_i, value=h)
                c.font = font(bold=True, color=WHITE, size=9)
                c.fill = fill(COL_HDR_FILL)
                c.alignment = align('center' if c_i==1 else 'right', 'center')
                c.border = thin_border()
            r_curr += 1

            salidas_by_date = OrderedDict()
            for m in m_list:
                if m['tipo_movimiento'] not in ('SALIDA', 'AJUSTE'): continue
                f_str = m['fecha_str'] or 'Sin Fecha'
                lts = float(m['litros'] or 0)
                is_gas = 'GASOLINA' in (str(m.get('equipo_economico') or '')+' '+str(m.get('equipo') or '')+' '+str(m.get('observaciones') or '')).upper()
                imp = float(m['importe_total']) if m.get('importe_total') else (lts * (23.97 if is_gas else 27.0))
                
                if f_str not in salidas_by_date:
                    salidas_by_date[f_str] = {'litros': 0.0, 'importe': 0.0}
                salidas_by_date[f_str]['litros'] += lts
                salidas_by_date[f_str]['importe'] += imp

            tot_litros_sem = 0.0
            tot_importe_sem = 0.0

            for f_str, data_item in salidas_by_date.items():
                lts = data_item['litros']
                imp = data_item['importe']
                prc_prom = (imp / lts) if lts > 0 else 27.0
                tot_litros_sem += lts
                tot_importe_sem += imp

                f_label = f_str
                try:
                    dt_obj = dt_module.datetime.strptime(f_str, '%Y-%m-%d')
                    dias_es = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
                    meses_es = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']
                    f_label = f"{dias_es[dt_obj.weekday()]} {dt_obj.day:02d}-{meses_es[dt_obj.month-1]}"
                except:
                    pass

                ws.cell(row=r_curr, column=1, value=f_label).alignment = align('left', 'center')
                c_lts = ws.cell(row=r_curr, column=2, value=lts)
                c_lts.number_format = '#,##0.000'
                c_lts.alignment = align('right', 'center')

                c_prc = ws.cell(row=r_curr, column=3, value=prc_prom)
                c_prc.number_format = '"$"#,##0.00'
                c_prc.alignment = align('right', 'center')

                c_imp = ws.cell(row=r_curr, column=4, value=imp)
                c_imp.number_format = '"$"#,##0.00'
                c_imp.alignment = align('right', 'center')

                bg = COL_ALT2 if r_curr % 2 == 0 else COL_ALT1
                for c_i in range(1, 5):
                    cell = ws.cell(row=r_curr, column=c_i)
                    cell.font = font(size=9)
                    cell.fill = fill(bg)
                    cell.border = thin_border()

                r_curr += 1

            # Fila Total Jalisco
            ws.cell(row=r_curr, column=1, value="TOTAL — Base Jalisco").alignment = align('left', 'center')
            c_lts_t = ws.cell(row=r_curr, column=2, value=tot_litros_sem)
            c_lts_t.number_format = '#,##0.000'

            c_imp_t = ws.cell(row=r_curr, column=4, value=tot_importe_sem)
            c_imp_t.number_format = '"$"#,##0.00'

            for c_i in range(1, 5):
                cell = ws.cell(row=r_curr, column=c_i)
                cell.font = font(bold=True, size=9, color=WHITE)
                cell.fill = fill(COL_HDR_FILL)
                cell.border = thick_border()
                if c_i > 1: cell.alignment = align('right', 'center')

            for col in ws.columns:
                max_len = max(len(str(cell.value or '')) for cell in col)
                col_letter = get_column_letter(col[0].column)
                ws.column_dimensions[col_letter].width = max(max_len + 4, 20)

        db.close()

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        from flask import send_file
        return send_file(
            output,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name="Reporte_Jalisco_Vales_y_Consumos.xlsx"
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return str(e), 500



# ═══════════════════════════════════════════════════════════════════════════════
# API: TABLA 6 — RESUMEN DIARIO POR OBRA (para la página de resumen)
# ═══════════════════════════════════════════════════════════════════════════════
@app.route('/api/admin/resumen/tabla6')
def api_tabla6():
    """
    Devuelve el resumen diario de litros e importe por obra y semana.
    Params: semana, obra (puede ser 'TODAS')
    Response: { obras: [...], filas: [{fecha, litros, precio_prom, importe}], total: {...} }
    """
    try:
        semana = request.args.get('semana', '')
        obra   = request.args.get('obra', 'TODAS')
        db = get_db()

        # Obtener obras disponibles para el combo (filtrado por semana si aplica)
        cond_obras = "WHERE estatus_revision = 'APROBADO' AND obra_destino IS NOT NULL AND obra_destino != ''"
        params_obras = []
        if semana and semana != 'TODOS':
            semana_num = str(semana).replace('Semana ', '').strip()
            cond_obras += " AND semana = %s"
            params_obras.append(semana_num)

        obras_rows = db.execute(f"""
            SELECT DISTINCT obra_destino FROM diesel.consumos
            {cond_obras}
            ORDER BY obra_destino
        """, tuple(params_obras)).fetchall()
        obras_list = [r['obra_destino'] for r in obras_rows]

        # Condición base para los datos
        cond = "WHERE estatus_revision = 'APROBADO'"
        params = []
        if semana and semana != 'TODOS':
            semana_num = str(semana).replace('Semana ', '').strip()
            cond += " AND semana = %s"
            params.append(semana_num)
        if obra and obra != 'TODAS':
            cond += " AND obra_destino = %s"
            params.append(obra)
        else:
            cond += " AND obra_destino IS NOT NULL AND obra_destino != ''"

        # Query de resumen diario
        filas_rows = db.execute(f"""
            SELECT fecha::text as fecha_str,
                   SUM(litros) as total_litros,
                   27.0 as precio_prom,
                   SUM(litros * 27.0) as importe_total,
                   COUNT(DISTINCT obra_destino) as num_obras
            FROM diesel.consumos
            {cond}
            GROUP BY fecha::text
            ORDER BY fecha::text
        """, tuple(params)).fetchall()
        db.close()

        DIAS_ES = {'Monday':'Lun','Tuesday':'Mar','Wednesday':'Mié','Thursday':'Jue',
                   'Friday':'Vie','Saturday':'Sáb','Sunday':'Dom'}
        MESES_ES = {1:'ene',2:'feb',3:'mar',4:'abr',5:'may',6:'jun',
                    7:'jul',8:'ago',9:'sep',10:'oct',11:'nov',12:'dic'}

        import datetime as _dt
        filas = []
        tot_lts = 0
        tot_imp = 0
        for row in filas_rows:
            lts  = float(row['total_litros'] or 0)
            prec = float(row['precio_prom'] or 0)
            imp  = float(row['importe_total'] or 0)
            if imp == 0 and prec > 0:
                imp = lts * prec
            tot_lts += lts
            tot_imp += imp

            try:
                d = _dt.date.fromisoformat(row['fecha_str'])
                dia_nom = DIAS_ES.get(d.strftime('%A'), d.strftime('%A'))
                mes_nom = MESES_ES.get(d.month, str(d.month))
                fecha_label = f"{dia_nom} {d.day:02d}-{mes_nom}"
            except:
                fecha_label = row['fecha_str']

            filas.append({
                'fecha_str':    row['fecha_str'],
                'fecha_label':  fecha_label,
                'litros':       round(lts, 3),
                'precio_prom':  round(prec, 4),
                'importe':      round(imp, 2),
            })

        return jsonify({
            'obras':  obras_list,
            'filas':  filas,
            'total':  {
                'litros':  round(tot_lts, 3),
                'importe': round(tot_imp, 2),
            }
        })
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# API: GENERADOR DE REPORTE EXCEL (todas las semanas, mismo formato DIESEL SEMANAL POR OBRA)
# ═══════════════════════════════════════════════════════════════════════════════
@app.route('/api/admin/reporte/excel')
def api_generar_reporte_excel():
    try:
        import openpyxl
        from openpyxl.styles import (Font, PatternFill, Alignment, Border, Side,
                                     GradientFill)
        from openpyxl.utils import get_column_letter
        from collections import OrderedDict
        import io, datetime as dt_module

        modulo = request.args.get('modulo', 'diesel')
        db = get_db()

        # ── Colores (mismos del Excel de referencia) ──────────────────────────
        COL_HDR_FILL   = '1E293B'   # encabezado oscuro
        COL_ING_FILL   = '312E81'   # fila ingeniero (morado oscuro)
        COL_TOT_FILL   = '1E3A5F'   # fila totales
        COL_IMP_FILL   = '2D1B69'   # fila importe
        COL_ALT1       = 'F8FAFC'   # alt row claro 1
        COL_ALT2       = 'EFF6FF'   # alt row claro 2
        COL_VERDE      = 'D1FAE5'
        COL_VERDE_FNT  = '065F46'
        COL_ROJO       = 'FEE2E2'
        COL_ROJO_FNT   = '991B1B'
        COL_OBRA_FILL  = 'E0E7FF'   # filas de obra

        WHITE          = 'FFFFFF'

        def fill(hex_color):
            return PatternFill("solid", fgColor=hex_color)

        def font(bold=False, color='000000', size=10, name='Calibri'):
            return Font(bold=bold, color=color, size=size, name=name)

        def align(h='center', v='center', wrap=False):
            return Alignment(horizontal=h, vertical=v, wrap_text=wrap)

        def thin_border():
            s = Side(style='thin', color='CBD5E1')
            return Border(left=s, right=s, top=s, bottom=s)

        def thick_border():
            s = Side(style='medium', color='1E293B')
            return Border(left=s, right=s, top=s, bottom=s)

        def fmt_num(n):
            if n is None or float(n) == 0:
                return ''
            return round(float(n), 2)

        def style_hdr(cell, text=None):
            cell.fill = fill(COL_HDR_FILL)
            cell.font = font(bold=True, color=WHITE, size=9)
            cell.alignment = align('center', 'center', wrap=True)
            cell.border = thin_border()
            if text is not None:
                cell.value = text

        def style_ing(cell, text=None):
            cell.fill = fill(COL_ING_FILL)
            cell.font = font(bold=True, color=WHITE, size=9)
            cell.alignment = align('left', 'center')
            cell.border = thin_border()
            if text is not None:
                cell.value = text

        def style_tot(cell, text=None):
            cell.fill = fill(COL_TOT_FILL)
            cell.font = font(bold=True, color=WHITE, size=9)
            cell.alignment = align('right', 'center')
            cell.border = thin_border()
            if text is not None:
                cell.value = text

        def style_data(cell, value=None, h='right', bg=None):
            if bg:
                cell.fill = fill(bg)
            cell.font = font(size=9)
            cell.alignment = align(h, 'center')
            cell.border = thin_border()
            if value is not None:
                cell.value = value

        tbl_consumos = 'gasolina.consumos' if modulo == 'gasolina' else 'diesel.consumos'
        field_resp = 'conductor' if modulo == 'gasolina' else 'responsable'
        col_resp = 'conductor' if modulo == 'gasolina' else 'responsable'
        tipo_auth = 'GASOLINA' if modulo == 'gasolina' else 'DIESEL'

        # ── Obtener todas las semanas disponibles ────────────────────────────
        semanas_rows = db.execute(
            f"SELECT semana FROM {tbl_consumos} WHERE semana IS NOT NULL GROUP BY semana ORDER BY semana::integer"
        ).fetchall()
        semanas = [r['semana'] for r in semanas_rows]

        wb = openpyxl.Workbook()
        wb.remove(wb.active)  # Quitar hoja por defecto

        # Default auth fallback from Week 29
        def norm_resp_excel(name):
            if not name: return 'S/R'
            n = name.strip().upper()
            if 'CARREOLA' in n or 'DIEGO' in n: return 'ING. DIEGO CARREOLA'
            if 'APOLINAR' in n: return 'APOLINAR'
            if 'DAYANNE' in n: return 'DAYANNE'
            if 'EDGAR' in n: return 'EDGAR'
            if 'FRANCISCO' in n or 'JAVIER' in n: return 'FRANCISCO JAVIER'
            if 'JACK' in n: return 'JACK'
            if 'LUIS' in n: return 'LUIS'
            if 'SAMUEL' in n: return 'SAMUEL'
            if 'PAOLA' in n: return 'PAOLA'
            return name.strip().upper()

        default_auth_29 = {
            'APOLINAR': 400.0,
            'DAYANNE': 0.0,
            'EDGAR': 0.0,
            'FRANCISCO JAVIER': 550.0,
            'ING. DIEGO CARREOLA': 900.0,
            'JACK': 400.0,
            'LUIS': 400.0,
            'SAMUEL': 0.0
        }

        # ── 1. PESTAÑA CONSOLIDADA HISTÓRICA (TODAS LAS SEMANAS POR OBRA) ───────
        try:
            ws_hist = wb.create_sheet(title='Histórico')
            ws_hist.views.sheetView[0].showGridLines = True

            # Título principal de la hoja Histórico
            ws_hist.merge_cells("A1:I1")
            title_cell = ws_hist.cell(row=1, column=1)
            title_cell.value = f"REPORTE HISTÓRICO CONSOLIDADO POR SEMANA ({'GASOLINA' if modulo == 'gasolina' else 'DIÉSEL'})"
            title_cell.fill = fill('0F172A')
            title_cell.font = font(bold=True, color=WHITE, size=11)
            title_cell.alignment = align('center', 'center')
            ws_hist.row_dimensions[1].height = 25

            # Subtítulo con fecha de generación
            ws_hist.merge_cells("A2:I2")
            sub_cell = ws_hist.cell(row=2, column=1)
            sub_cell.value = f"Generado el: {dt_module.datetime.now().strftime('%Y-%m-%d %H:%M')}"
            sub_cell.fill = fill('1E293B')
            sub_cell.font = font(color='94A3B8', size=9)
            sub_cell.alignment = align('center', 'center')
            ws_hist.row_dimensions[2].height = 18

            # Configurar anchos de columna para tablas lado a lado
            # Tabla 1 (Izquierda: Cols A, B, C, D)
            ws_hist.column_dimensions['A'].width = 18
            ws_hist.column_dimensions['B'].width = 18
            ws_hist.column_dimensions['C'].width = 18
            ws_hist.column_dimensions['D'].width = 18

            # Separador Columna E
            ws_hist.column_dimensions['E'].width = 3

            # Tabla 2 (Derecha: Cols F, G, H, I)
            ws_hist.column_dimensions['F'].width = 18
            ws_hist.column_dimensions['G'].width = 18
            ws_hist.column_dimensions['H'].width = 18
            ws_hist.column_dimensions['I'].width = 18

            # Consulta histórica por obra y semana
            sql_hist = f"""
                SELECT 
                    COALESCE(NULLIF(obra_destino,''), 'GENERAL / SIN OBRA') as obra,
                    semana::integer as semana_num,
                    SUM(litros) as total_litros,
                    AVG(costo_por_litro) as precio_prom,
                    SUM(importe_total) as importe_total
                FROM {tbl_consumos}
                WHERE (estatus_revision IS NULL OR estatus_revision != 'RECHAZADO')
                  AND (obra_destino IS NULL OR obra_destino NOT ILIKE '%%Tanque Pegaso%%')
                GROUP BY COALESCE(NULLIF(obra_destino,''), 'GENERAL / SIN OBRA'), semana::integer
                ORDER BY obra, semana::integer
            """
            rows_hist = db.execute(sql_hist).fetchall()

            por_obra_hist = OrderedDict()
            for rh in rows_hist:
                ob = rh['obra']
                por_obra_hist.setdefault(ob, []).append(rh)

            obras_hist_items = list(por_obra_hist.items())
            r_hist = 4  # Comenzar en fila 4

            for i in range(0, len(obras_hist_items), 2):
                chunk = obras_hist_items[i:i+2]
                r_start = r_hist
                max_r = r_hist

                for idx, (obra_nombre, obra_filas) in enumerate(chunk):
                    col_off = 1 if idx == 0 else 6  # Columna A (1) o F (6)
                    curr_r = r_start

                    # Título de obra (encabezado azul oscuro)
                    ws_hist.merge_cells(start_row=curr_r, start_column=col_off, end_row=curr_r, end_column=col_off+3)
                    tc = ws_hist.cell(row=curr_r, column=col_off)
                    tc.value = f"▶  {obra_nombre}"
                    tc.fill = fill('1E3A5F')
                    tc.font = font(bold=True, color=WHITE, size=10)
                    tc.alignment = align('left', 'center')
                    tc.border = thin_border()
                    ws_hist.row_dimensions[curr_r].height = 20
                    curr_r += 1

                    # Encabezados de columna
                    for c_idx, hdr_txt in enumerate(['SEMANA', 'LITROS CONSUMIDOS', 'PRECIO PROM. ($/L)', 'IMPORTE TOTAL'], start=col_off):
                        c = ws_hist.cell(row=curr_r, column=c_idx)
                        style_hdr(c, hdr_txt)
                    ws_hist.row_dimensions[curr_r].height = 20
                    curr_r += 1

                    # Filas por semana para esta obra
                    tot_lts_ob = 0.0
                    tot_imp_ob = 0.0

                    for rh_idx, rh in enumerate(obra_filas):
                        s_num = rh['semana_num']
                        s_lts = float(rh['total_litros'] or 0)
                        s_prec = float(rh['precio_prom'] or 0)
                        s_imp = float(rh['importe_total'] or 0)

                        if s_imp == 0 and s_prec > 0:
                            s_imp = s_lts * s_prec

                        tot_lts_ob += s_lts
                        tot_imp_ob += s_imp

                        bg_row = COL_ALT1 if rh_idx % 2 == 0 else COL_ALT2

                        c = ws_hist.cell(row=curr_r, column=col_off)
                        c.value = f"Semana {s_num}"
                        c.fill = fill(bg_row)
                        c.font = font(bold=True, size=9)
                        c.alignment = align('left', 'center')
                        c.border = thin_border()

                        c = ws_hist.cell(row=curr_r, column=col_off+1)
                        c.value = round(s_lts, 3) if s_lts else None
                        c.fill = fill(bg_row)
                        c.font = font(size=9)
                        c.alignment = align('right', 'center')
                        c.border = thin_border()
                        c.number_format = '#,##0.000'

                        c = ws_hist.cell(row=curr_r, column=col_off+2)
                        c.value = round(s_prec, 4) if s_prec else None
                        c.fill = fill(bg_row)
                        c.font = font(size=9)
                        c.alignment = align('right', 'center')
                        c.border = thin_border()
                        c.number_format = '"$"#,##0.0000'

                        c = ws_hist.cell(row=curr_r, column=col_off+3)
                        c.value = round(s_imp, 2) if s_imp else None
                        c.fill = fill(bg_row)
                        c.font = font(bold=True, size=9)
                        c.alignment = align('right', 'center')
                        c.border = thin_border()
                        c.number_format = '"$"#,##0.00'

                        ws_hist.row_dimensions[curr_r].height = 18
                        curr_r += 1

                    # Fila de TOTAL por obra
                    c_tot_lbl = ws_hist.cell(row=curr_r, column=col_off)
                    c_tot_lbl.value = f"TOTAL — {obra_nombre}"
                    c_tot_lbl.fill = fill('1E3A5F')
                    c_tot_lbl.font = font(bold=True, color=WHITE, size=9)
                    c_tot_lbl.alignment = align('left', 'center')
                    c_tot_lbl.border = thin_border()

                    c_tot_lts = ws_hist.cell(row=curr_r, column=col_off+1)
                    c_tot_lts.value = round(tot_lts_ob, 3) if tot_lts_ob else None
                    c_tot_lts.fill = fill('1E3A5F')
                    c_tot_lts.font = font(bold=True, color=WHITE, size=9)
                    c_tot_lts.alignment = align('right', 'center')
                    c_tot_lts.border = thin_border()
                    c_tot_lts.number_format = '#,##0.000'

                    c_tot_prec = ws_hist.cell(row=curr_r, column=col_off+2)
                    c_tot_prec.value = ''
                    c_tot_prec.fill = fill('1E3A5F')
                    c_tot_prec.border = thin_border()

                    c_tot_imp = ws_hist.cell(row=curr_r, column=col_off+3)
                    c_tot_imp.value = round(tot_imp_ob, 2) if tot_imp_ob else None
                    c_tot_imp.fill = fill('1E3A5F')
                    c_tot_imp.font = font(bold=True, color=WHITE, size=9)
                    c_tot_imp.alignment = align('right', 'center')
                    c_tot_imp.border = thin_border()
                    c_tot_imp.number_format = '"$"#,##0.00'

                    ws_hist.row_dimensions[curr_r].height = 20
                    curr_r += 1

                    if curr_r > max_r:
                        max_r = curr_r

                r_hist = max_r + 2  # Espacio entre filas de pares de obras
        except Exception as e_hist:
            print("ERROR GENERANDO HOJA HISTÓRICO:", e_hist)

        for semana_str in semanas:
            try:
                semana_num = int(semana_str)
            except:
                continue

            semana_label = f'Semana {semana_num}'

            # ── Autorizaciones ────────────────────────────────────────────────
            auth_map = {}
            try:
                auth_rows = db.execute(
                    "SELECT referencia, litros_autorizados FROM catalogos.autorizaciones WHERE tipo=%s AND semana=%s",
                    (tipo_auth, semana_num)
                ).fetchall()
                for ar in auth_rows:
                    ref_norm = norm_resp_excel(ar['referencia'])
                    lts = float(ar['litros_autorizados'] or 0)
                    if lts > 0:
                        auth_map[ref_norm] = lts
            except:
                pass

            # Fallback to default auth map if missing
            if modulo == 'diesel':
                for k, v in default_auth_29.items():
                    if k not in auth_map:
                        auth_map[k] = v

            cond = f"WHERE (estatus_revision IS NULL OR estatus_revision != 'RECHAZADO') AND (obra_destino IS NULL OR obra_destino NOT ILIKE %s) AND semana = %s"
            params = ['%Tanque Pegaso%', semana_str]

            dias_trabajados = 7

            # ── Tabla 1: pivot responsable -> obra -> litros ──────────────────
            try:
                rows_pivot = db.execute(f"""
                    SELECT COALESCE(NULLIF(NULLIF({field_resp}::text,'nan'),''),'S/R') as resp,
                           obra_destino,
                           SUM(litros) as litros
                    FROM {tbl_consumos}
                    {cond}
                    GROUP BY COALESCE(NULLIF(NULLIF({field_resp}::text,'nan'),''),'S/R'), obra_destino
                    ORDER BY resp, obra_destino
                """, tuple(params)).fetchall()
            except Exception as e:
                print("ROWS_PIVOT ERROR:", e)
                rows_pivot = []

            # ── Resumen Diario por Obra: litros + importe por día y obra ────────────
            try:
                rows_diario = db.execute(f"""
                    SELECT COALESCE(NULLIF(obra_destino,''), 'GENERAL / SIN OBRA') as obra,
                           fecha::text as fecha_str,
                           SUM(litros) as total_litros,
                           AVG(costo_por_litro) as precio_prom,
                           SUM(importe_total) as importe_total
                    FROM {tbl_consumos}
                    {cond}
                    GROUP BY COALESCE(NULLIF(obra_destino,''), 'GENERAL / SIN OBRA'), fecha::text
                    ORDER BY obra, fecha::text
                """, tuple(params)).fetchall()
            except:
                rows_diario = []

            # ── Tabla 5: por responsable, fecha, obra, equipo ─────────────────
            try:
                eq_col = "COALESCE(NULLIF(vehiculo,''), NULLIF(placa,''), 'SIN EQUIPO')" if modulo == 'gasolina' else "COALESCE(NULLIF(equipo,''),'SIN EQUIPO')"
                rows_maq = db.execute(f"""
                    SELECT COALESCE(NULLIF(NULLIF({field_resp}::text,'nan'),''),'S/R') as resp,
                           fecha::text as fecha_str,
                           obra_destino,
                           {eq_col} as equipo,
                           SUM(litros) as litros,
                           AVG(costo_por_litro) as precio_unit
                    FROM {tbl_consumos}
                    {cond}
                    GROUP BY COALESCE(NULLIF(NULLIF({field_resp}::text,'nan'),''),'S/R'),
                             fecha::text, obra_destino,
                             {eq_col}
                    ORDER BY resp, fecha::text, equipo
                """, tuple(params)).fetchall()
            except:
                rows_maq = []

            # Estructurar datos Tabla 5
            ing_data = OrderedDict()
            for r in rows_maq:
                resp = norm_resp_excel(r['resp'])
                if resp == 'S/R':
                    continue
                fecha = r['fecha_str']
                eq = r['equipo']
                lts = float(r['litros'] or 0)
                if resp not in ing_data:
                    ing_data[resp] = {'dias': set(), 'equipos': set(), 'consumos': {}, 'obras': {}, 'precio': 27.0}
                d = ing_data[resp]
                d['dias'].add(fecha)
                d['equipos'].add(eq)
                d['consumos'].setdefault(eq, {})[fecha] = d['consumos'].get(eq, {}).get(fecha, 0) + lts
                if fecha not in d['obras']:
                    d['obras'][fecha] = r['obra_destino'] or ''
                if r['precio_unit']:
                    d['precio'] = float(r['precio_unit'])

            for resp, d in ing_data.items():
                d['dias'] = sorted(d['dias'])
                d['equipos'] = sorted(d['equipos'])

            # ── Crear hoja ────────────────────────────────────────────────────
            ws = wb.create_sheet(title=semana_label)
            ws.sheet_view.showGridLines = False

            # ── Columnas Tabla 1: F G H I J K L (cols 6..12) ────────────────
            T4_COLS = {'F': 22, 'G': 18, 'H': 18, 'I': 24, 'J': 18, 'K': 22, 'L': 22}
            for col_letter, width in T4_COLS.items():
                ws.column_dimensions[col_letter].width = width

            # Columnas A-E vacias para margen izquierdo visual
            for cl in ['A','B','C','D','E']:
                ws.column_dimensions[cl].width = 3

            # ── Título Tabla 1 ────────────────────────────────────────────────
            r = 2
            ws.merge_cells(f'F{r}:L{r}')
            tc = ws[f'F{r}']
            tc.value = f'CONSUMO {semana_label.upper()}'
            tc.fill = fill(COL_HDR_FILL)
            tc.font = font(bold=True, color=WHITE, size=12)
            tc.alignment = align('center', 'center')
            tc.border = thin_border()

            r += 1
            # Encabezados Tabla 1
            hdrs4 = ['RESPONSABLE','AUTORIZADO DIARIO','SEMANAL (7 DÍAS)','OBRA',
                     'CONSUMO POR OBRA','CONSUMO POR INGENIERO','REMANENTE POR INGENIERO']
            for i, hdr in enumerate(hdrs4):
                cell = ws[f'{chr(70+i)}{r}']  # F=70
                style_hdr(cell, hdr)
            r += 1

            # Estructurar Tabla 1
            resp_obras = OrderedDict()
            for row in rows_pivot:
                resp = norm_resp_excel(row['resp'])
                if resp == 'S/R' and float(row['litros'] or 0) == 0:
                    continue
                resp_obras.setdefault(resp, {})
                obra_nom = row['obra_destino'] or 'GENERAL / SIN OBRA'
                resp_obras[resp][obra_nom] = resp_obras[resp].get(obra_nom, 0) + float(row['litros'] or 0)

            # Unir con responsables de autorizaciones
            if modulo == 'diesel':
                all_resps = sorted(set(list(default_auth_29.keys()) + list(resp_obras.keys()) + list(auth_map.keys())))
            else:
                all_resps = sorted(set(list(resp_obras.keys()) + list(auth_map.keys())))

            # Cargar dias_trabajados de la base de datos
            dias_map_db = {}
            try:
                r_db_rows = db.execute("SELECT nombre, dias_trabajados FROM catalogos.responsables").fetchall()
                for r_item in r_db_rows:
                    if r_item['nombre']:
                        dias_map_db[r_item['nombre'].strip().upper()] = int(r_item['dias_trabajados'] or 6)
            except Exception as e:
                pass

            def get_dias_for_resp(r_name):
                un = str(r_name or '').strip().upper()
                for k, v in dias_map_db.items():
                    if k in un or un in k:
                        return v
                if any(x in un for x in ['DAYANNE', 'EDGAR', 'SAMUEL']):
                    return 5
                return 6

            # Agrupar responsables por días trabajados (6 días primero, luego 5 días)
            resps_by_days = OrderedDict()
            for resp in all_resps:
                if resp == 'S/R':
                    continue
                d_val = get_dias_for_resp(resp)
                resps_by_days.setdefault(d_val, []).append(resp)

            tot_semanal_gen = 0
            tot_consumo_gen = 0
            tot_remanente_gen = 0

            # Iterar por grupos de días (6 Días, 5 Días, etc.)
            for d_val in sorted(resps_by_days.keys(), reverse=True):
                group_resps = resps_by_days[d_val]
                
                # Encabezado de la Sección por Días Trabajados
                hdrs4_sec = ['RESPONSABLE', 'AUTORIZADO DIARIO', f'SEMANAL ({d_val} DÍAS)', 'OBRA',
                             'CONSUMO POR OBRA', 'CONSUMO POR INGENIERO', 'REMANENTE POR INGENIERO']
                for i, hdr in enumerate(hdrs4_sec):
                    cell = ws[f'{chr(70+i)}{r}']
                    style_hdr(cell, hdr)
                r += 1

                tot_semanal_sec = 0
                tot_consumo_sec = 0
                tot_remanente_sec = 0

                for resp in group_resps:
                    obras_dict = resp_obras.get(resp, {})
                    obras_sorted = sorted(obras_dict.keys()) if obras_dict else ['SIN CONSUMOS']
                    con_ing = sum(obras_dict.values())
                    auto_dia = auth_map.get(resp, default_auth_29.get(resp, 0.0) if modulo == 'diesel' else 0.0)
                    auto_sem = auto_dia * float(d_val)
                    remanente = auto_sem - con_ing
                    
                    tot_semanal_sec += auto_sem
                    tot_consumo_sec += con_ing
                    tot_remanente_sec += remanente

                    num_obras = len(obras_sorted)
                    first = True
                    for j, obra in enumerate(obras_sorted):
                        con_obra = obras_dict.get(obra, 0)
                        bg = COL_ALT1 if (group_resps.index(resp) % 2 == 0) else COL_ALT2

                        # Col F - Responsable
                        fc = ws[f'F{r}']
                        if first:
                            style_ing(fc, resp.upper())
                            if num_obras > 1:
                                ws.merge_cells(f'F{r}:F{r+num_obras-1}')
                        else:
                            fc.fill = fill(COL_ING_FILL)
                            fc.border = thin_border()

                        # Col G - Aut. Diario
                        gc = ws[f'G{r}']
                        if first:
                            style_data(gc, auto_dia if auto_dia else None, h='center', bg=bg)
                            if num_obras > 1:
                                ws.merge_cells(f'G{r}:G{r+num_obras-1}')
                        else:
                            gc.fill = fill(bg)
                            gc.border = thin_border()

                        # Col H - Semanal (N días)
                        hc = ws[f'H{r}']
                        if first:
                            style_data(hc, auto_sem if auto_sem else None, h='center', bg=bg)
                            if num_obras > 1:
                                ws.merge_cells(f'H{r}:H{r+num_obras-1}')
                        else:
                            hc.fill = fill(bg)
                            hc.border = thin_border()

                        # Col I - Obra
                        ic = ws[f'I{r}']
                        style_data(ic, obra, h='left' if obra != 'SIN CONSUMOS' else 'center', bg=bg)

                        # Col J - Consumo por Obra
                        jc = ws[f'J{r}']
                        style_data(jc, con_obra if con_obra else None, h='center', bg=bg)

                        # Col K - Consumo por Ingeniero
                        kc = ws[f'K{r}']
                        if first:
                            style_data(kc, con_ing if con_ing else None, h='center', bg=bg)
                            kc.font = font(bold=True, size=9)
                            if num_obras > 1:
                                ws.merge_cells(f'K{r}:K{r+num_obras-1}')
                        else:
                            kc.fill = fill(bg)
                            kc.border = thin_border()

                        # Col L - Remanente por Ingeniero
                        lc = ws[f'L{r}']
                        if first:
                            rem_bg = 'E6F4EA' if remanente >= 0 else 'FCE4E4'
                            rem_fg = '166534' if remanente >= 0 else 'DC2626'
                            lc.value = remanente if remanente != 0 else None
                            lc.fill = fill(rem_bg)
                            lc.font = font(bold=True, color=rem_fg, size=9)
                            lc.alignment = align('center', 'center')
                            lc.border = thin_border()
                            if num_obras > 1:
                                ws.merge_cells(f'L{r}:L{r+num_obras-1}')
                        else:
                            lc.fill = fill(bg)
                            lc.border = thin_border()

                        ws.row_dimensions[r].height = 18
                        r += 1
                        first = False

                # Subtotal Sección Días
                ws.merge_cells(f'F{r}:G{r}')
                tc = ws[f'F{r}']
                style_tot(tc, f'SUBTOTAL ({d_val} DÍAS):')
                ws[f'G{r}'].fill = fill(COL_TOT_FILL)
                ws[f'G{r}'].border = thin_border()
                style_tot(ws[f'H{r}'], round(tot_semanal_sec, 2) if tot_semanal_sec else '')
                ws[f'I{r}'].fill = fill(COL_TOT_FILL)
                ws[f'I{r}'].border = thin_border()
                style_tot(ws[f'J{r}'], round(tot_consumo_sec, 2) if tot_consumo_sec else '')
                style_tot(ws[f'K{r}'], round(tot_consumo_sec, 2) if tot_consumo_sec else '')
                style_tot(ws[f'L{r}'], round(tot_remanente_sec, 2) if tot_remanente_sec else '')
                ws.row_dimensions[r].height = 20
                r += 1

                tot_semanal_gen += tot_semanal_sec
                tot_consumo_gen += tot_consumo_sec
                tot_remanente_gen += tot_remanente_sec

            # Fila TOTALES GENERALES
            ws.merge_cells(f'F{r}:G{r}')
            tc = ws[f'F{r}']
            style_tot(tc, 'TOTAL GENERAL:')
            ws[f'G{r}'].fill = fill(COL_TOT_FILL)
            ws[f'G{r}'].border = thin_border()
            style_tot(ws[f'H{r}'], round(tot_semanal_gen, 2) if tot_semanal_gen else '')
            ws[f'I{r}'].fill = fill(COL_TOT_FILL)
            ws[f'I{r}'].border = thin_border()
            style_tot(ws[f'J{r}'], round(tot_consumo_gen, 2) if tot_consumo_gen else '')
            style_tot(ws[f'K{r}'], round(tot_consumo_gen, 2) if tot_consumo_gen else '')
            style_tot(ws[f'L{r}'], round(tot_remanente_gen, 2) if tot_remanente_gen else '')
            ws.row_dimensions[r].height = 22
            r += 1

            # ── Espacio entre tablas ───────────────────────────────────────────
            r += 2

            # ── TABLA RESUMEN DIARIO POR OBRA ────────────────────────────────────
            # Mostrar 2 por nivel para evitar demasiada longitud
            DIAS_ES_RD = {'Mon':'Lun','Tue':'Mar','Wed':'Mié','Thu':'Jue','Fri':'Vie','Sat':'Sáb','Sun':'Dom'}
            MESES_ES = {1:'ene',2:'feb',3:'mar',4:'abr',5:'may',6:'jun',
                        7:'jul',8:'ago',9:'sep',10:'oct',11:'nov',12:'dic'}

            # Agrupar rows_diario por obra
            from collections import OrderedDict as _OD
            diario_por_obra = _OD()
            for rd in rows_diario:
                ob = rd['obra']
                diario_por_obra.setdefault(ob, []).append(rd)

            # Anchos fijos para las columnas de las dos tablas
            # Tabla 1 (Izquierda)
            ws.column_dimensions['F'].width = 18
            ws.column_dimensions['G'].width = 18
            ws.column_dimensions['H'].width = 16
            ws.column_dimensions['I'].width = 18

            # Espaciador
            ws.column_dimensions['J'].width = 3

            # Tabla 2 (Derecha)
            ws.column_dimensions['K'].width = 18
            ws.column_dimensions['L'].width = 18
            ws.column_dimensions['M'].width = 16
            ws.column_dimensions['N'].width = 18

            obras_items = list(diario_por_obra.items())

            for i in range(0, len(obras_items), 2):
                chunk = obras_items[i:i+2]
                r_start = r
                max_r = r
                
                for idx, (obra_nombre, obra_filas) in enumerate(chunk):
                    col_offset = 6 if idx == 0 else 11
                    curr_r = r_start
                    
                    # Título de obra (encabezado azul oscuro)
                    ws.merge_cells(start_row=curr_r, start_column=col_offset, end_row=curr_r, end_column=col_offset+3)
                    tc = ws.cell(row=curr_r, column=col_offset)
                    tc.value = f'▶  {obra_nombre}'
                    tc.fill = fill('1E3A5F')
                    tc.font = font(bold=True, color=WHITE, size=10)
                    tc.alignment = align('left', 'center')
                    tc.border = thin_border()
                    ws.row_dimensions[curr_r].height = 20
                    curr_r += 1

                    # Encabezados de columna
                    for c_idx, hdr_txt in enumerate(['DÍA', 'LITROS CONSUMIDOS', 'PRECIO PROM. ($/L)', 'IMPORTE TOTAL'], start=col_offset):
                        c = ws.cell(row=curr_r, column=c_idx)
                        style_hdr(c, hdr_txt)
                    ws.row_dimensions[curr_r].height = 20
                    curr_r += 1

                    # Filas de datos por día de esta obra
                    tot_lts_ob = 0
                    tot_imp_ob = 0
                    for rd_idx, rd in enumerate(obra_filas):
                        rd_fecha = rd['fecha_str']
                        rd_lts   = float(rd['total_litros'] or 0)
                        rd_prec  = float(rd['precio_prom'] or 0)
                        rd_imp   = float(rd['importe_total'] or 0)
                        if rd_imp == 0 and rd_prec > 0:
                            rd_imp = rd_lts * rd_prec
                        tot_lts_ob += rd_lts
                        tot_imp_ob += rd_imp

                        bg_rd = COL_ALT1 if rd_idx % 2 == 0 else COL_ALT2

                        try:
                            d_obj = dt_module.datetime.strptime(rd_fecha, '%Y-%m-%d')
                            dia_nom = DIAS_ES_RD.get(d_obj.strftime('%a'), d_obj.strftime('%a'))
                            mes_nom = MESES_ES.get(d_obj.month, str(d_obj.month))
                            fecha_label = f'{dia_nom} {d_obj.day:02d}-{mes_nom}'
                        except:
                            fecha_label = rd_fecha

                        c = ws.cell(row=curr_r, column=col_offset)
                        c.value = fecha_label
                        c.fill = fill(bg_rd); c.font = font(bold=True, size=9)
                        c.alignment = align('left', 'center'); c.border = thin_border()

                        c = ws.cell(row=curr_r, column=col_offset+1)
                        c.value = round(rd_lts, 3) if rd_lts else None
                        c.fill = fill(bg_rd); c.font = font(size=9)
                        c.alignment = align('right', 'center'); c.border = thin_border()
                        c.number_format = '#,##0.000'

                        c = ws.cell(row=curr_r, column=col_offset+2)
                        c.value = round(rd_prec, 4) if rd_prec else None
                        c.fill = fill(bg_rd); c.font = font(size=9)
                        c.alignment = align('right', 'center'); c.border = thin_border()
                        c.number_format = '"$"#,##0.0000'

                        c = ws.cell(row=curr_r, column=col_offset+3)
                        c.value = round(rd_imp, 2) if rd_imp else None
                        c.fill = fill(bg_rd); c.font = font(bold=True, size=9)
                        c.alignment = align('right', 'center'); c.border = thin_border()
                        c.number_format = '"$"#,##0.00'

                        ws.row_dimensions[curr_r].height = 18
                        curr_r += 1

                    # Fila de total por obra
                    c = ws.cell(row=curr_r, column=col_offset)
                    c.value = f'TOTAL — {obra_nombre}'
                    c.fill = fill(COL_TOT_FILL); c.font = font(bold=True, color=WHITE, size=9)
                    c.alignment = align('right', 'center'); c.border = thin_border()

                    c = ws.cell(row=curr_r, column=col_offset+1)
                    c.value = round(tot_lts_ob, 3) if tot_lts_ob else None
                    c.fill = fill(COL_TOT_FILL); c.font = font(bold=True, color=WHITE, size=9)
                    c.alignment = align('right', 'center'); c.border = thin_border()
                    c.number_format = '#,##0.000'

                    c = ws.cell(row=curr_r, column=col_offset+2)
                    c.fill = fill(COL_TOT_FILL); c.border = thin_border()

                    c = ws.cell(row=curr_r, column=col_offset+3)
                    c.value = round(tot_imp_ob, 2) if tot_imp_ob else None
                    c.fill = fill(COL_TOT_FILL); c.font = font(bold=True, color=WHITE, size=9)
                    c.alignment = align('right', 'center'); c.border = thin_border()
                    c.number_format = '"$"#,##0.00'
                    ws.row_dimensions[curr_r].height = 20
                    curr_r += 1

                    if curr_r > max_r:
                        max_r = curr_r
                        
                r = max_r + 1

            # Espacio antes de Tabla 5
            r += 1

            # ── TABLA 5: Consumo Diario por Ingeniero ─────────────────────────
            # Una sub-tabla por ingeniero
            # Columnas: F=idx, G=Responsable/Equipo/Obra, H=Importe Semanal, luego fechas, Total Lts, P.Unit, Total $

            for resp, d in ing_data.items():
                dias = d['dias']
                equipos = d['equipos']
                obras_map = d['obras']    # fecha -> obra
                consumos = d['consumos']  # equipo -> fecha -> litros
                precio = d['precio']
                auto_dia = auth_map.get(resp, 0)
                auto_sem = auto_dia * dias_trabajados

                num_dias = len(dias)

                # Columnas dinámicas para tabla 5:
                # F=idx, G=Responsable/Equipo, H=Importe, dias..., Total Lts, P.Unit, Total $
                # F(6), G(7), H(8), I...(9+n), luego Tot Lts, PU, Tot $
                col_start = 6   # F
                col_resp_idx = 6 # F
                col_importe = 8 # H
                col_dias_start = 9  # I
                col_dias_end = col_dias_start + num_dias - 1
                col_total_lts = col_dias_end + 1
                col_precio = col_total_lts + 1
                col_total_imp = col_precio + 1
                col_end = col_total_imp

                # Ajustar anchos de columnas de días
                for di in range(num_dias):
                    cl = get_column_letter(col_dias_start + di)
                    ws.column_dimensions[cl].width = 9
                ws.column_dimensions[get_column_letter(col_total_lts)].width = 11
                ws.column_dimensions[get_column_letter(col_precio)].width = 11
                ws.column_dimensions[get_column_letter(col_total_imp)].width = 13

                def wcell(row, col, val=None):
                    return ws.cell(row=row, column=col)

                def T5col(col):
                    return get_column_letter(col)

                # Título del bloque (Ingeniero)
                end_col_ltr = get_column_letter(col_end)
                ws.merge_cells(f'F{r}:{end_col_ltr}{r}')
                tc = ws.cell(row=r, column=6)
                tc.value = resp.upper()
                tc.fill = fill(COL_ING_FILL)
                tc.font = font(bold=True, color=WHITE, size=11)
                tc.alignment = align('left', 'center')
                tc.border = thin_border()
                ws.row_dimensions[r].height = 22
                r += 1

                # Fila encabezados Tabla 5
                hdr_row = r

                # Col F - # (índice)
                c = ws.cell(row=r, column=6)
                style_hdr(c, '#')
                ws.column_dimensions['F'].width = 5

                # Col G - Responsable / Equipo
                c = ws.cell(row=r, column=7)
                style_hdr(c, 'EQUIPO / MAQUINARIA')

                # Col H - Litros semanales autorizados (header)
                c = ws.cell(row=r, column=8)
                style_hdr(c, 'LTS. SEM.\nAUT.')

                # Mapeo de dias a español
                DIAS_ES = {'Mon':'Lun','Tue':'Mar','Wed':'Mié','Thu':'Jue','Fri':'Vie','Sat':'Sáb','Sun':'Dom'}

                # Cols días
                for di, dia in enumerate(dias):
                    try:
                        d_obj = dt_module.datetime.strptime(dia, '%Y-%m-%d')
                        nombre_dia = DIAS_ES.get(d_obj.strftime('%a'), d_obj.strftime('%a'))
                        dia_lbl = f"{nombre_dia}\n{d_obj.strftime('%d/%m')}"
                    except:
                        dia_lbl = dia
                    c = ws.cell(row=r, column=col_dias_start + di)
                    style_hdr(c, dia_lbl)

                # Total Lts
                c = ws.cell(row=r, column=col_total_lts)
                style_hdr(c, 'LITROS\nTOTAL')

                # Precio unit
                c = ws.cell(row=r, column=col_precio)
                style_hdr(c, 'PRECIO\nUNIT.')

                # Total $
                c = ws.cell(row=r, column=col_total_imp)
                style_hdr(c, 'TOTAL $')

                ws.row_dimensions[r].height = 28
                r += 1

                # Fila obras (encabezado de obra por día)
                obra_row = r
                ws.cell(row=r, column=6).border = thin_border()
                ws.cell(row=r, column=6).fill = fill(COL_OBRA_FILL)
                ws.cell(row=r, column=7, value='OBRA DESTINO').fill = fill(COL_OBRA_FILL)
                ws.cell(row=r, column=7).font = font(bold=True, size=8, color='1E3A5F')
                ws.cell(row=r, column=7).alignment = align('left', 'center')
                ws.cell(row=r, column=7).border = thin_border()
                ws.cell(row=r, column=8).fill = fill(COL_OBRA_FILL)
                ws.cell(row=r, column=8).border = thin_border()
                for di, dia in enumerate(dias):
                    obra_dia = obras_map.get(dia, '')
                    c = ws.cell(row=r, column=col_dias_start + di)
                    c.value = obra_dia
                    c.fill = fill(COL_OBRA_FILL)
                    c.font = font(size=7, color='1E3A5F')
                    c.alignment = align('center', 'center', wrap=True)
                    c.border = thin_border()
                for extra_col in [col_total_lts, col_precio, col_total_imp]:
                    ws.cell(row=r, column=extra_col).fill = fill(COL_OBRA_FILL)
                    ws.cell(row=r, column=extra_col).border = thin_border()
                ws.row_dimensions[r].height = 22
                r += 1

                # Filas de equipos
                tot_lts_semana = 0
                for eq_idx, eq in enumerate(equipos):
                    eq_consumos = consumos.get(eq, {})
                    bg = COL_ALT1 if eq_idx % 2 == 0 else COL_ALT2

                    # Col F - índice
                    c = ws.cell(row=r, column=6)
                    c.value = eq_idx + 1
                    c.fill = fill(bg)
                    c.font = font(size=8)
                    c.alignment = align('center', 'center')
                    c.border = thin_border()

                    # Col G - Equipo
                    c = ws.cell(row=r, column=7)
                    c.value = eq
                    c.fill = fill(bg)
                    c.font = font(size=8)
                    c.alignment = align('left', 'center', wrap=True)
                    c.border = thin_border()

                    # Col H - Litros semanales autorizados (solo primer equipo)
                    c = ws.cell(row=r, column=8)
                    if eq_idx == 0 and auto_sem:
                        c.value = auto_sem   # litros autorizados en la semana
                        c.font = font(bold=True, size=8)
                        c.number_format = '#,##0.00'
                    c.fill = fill(bg)
                    c.alignment = align('right', 'center')
                    c.border = thin_border()

                    # Litros por día
                    lts_total_eq = 0
                    for di, dia in enumerate(dias):
                        lts = eq_consumos.get(dia, 0)
                        lts_total_eq += lts
                        c = ws.cell(row=r, column=col_dias_start + di)
                        c.value = lts if lts else None
                        c.fill = fill(bg)
                        c.font = font(size=8)
                        c.alignment = align('center', 'center')
                        c.border = thin_border()

                    tot_lts_semana += lts_total_eq

                    # Total lts equipo
                    c = ws.cell(row=r, column=col_total_lts)
                    c.value = round(lts_total_eq, 2) if lts_total_eq else None
                    c.fill = fill(bg)
                    c.font = font(bold=True, size=8)
                    c.alignment = align('right', 'center')
                    c.border = thin_border()

                    # Precio unitario (con formato de moneda)
                    c = ws.cell(row=r, column=col_precio)
                    c.value = round(precio, 2)
                    c.fill = fill(bg)
                    c.font = font(size=8)
                    c.alignment = align('right', 'center')
                    c.border = thin_border()
                    c.number_format = '"$"#,##0.00'

                    # Total $ (con formato de moneda)
                    c = ws.cell(row=r, column=col_total_imp)
                    total_imp = round(lts_total_eq * precio, 2) if lts_total_eq else None
                    c.value = total_imp
                    c.fill = fill(bg)
                    c.font = font(bold=True, size=8)
                    c.alignment = align('right', 'center')
                    c.border = thin_border()
                    c.number_format = '"$"#,##0.00'

                    ws.row_dimensions[r].height = 18
                    r += 1

                # Fila: Total Litros
                ws.merge_cells(f'F{r}:{get_column_letter(col_dias_start-1)}{r}')
                c = ws.cell(row=r, column=6)
                c.value = 'TOTAL LITROS'
                c.fill = fill(COL_TOT_FILL)
                c.font = font(bold=True, color=WHITE, size=9)
                c.alignment = align('right', 'center')
                c.border = thin_border()
                for gi in range(7, col_dias_start):
                    ws.cell(row=r, column=gi).fill = fill(COL_TOT_FILL)
                    ws.cell(row=r, column=gi).border = thin_border()

                for di in range(num_dias):
                    dia = dias[di]
                    sum_dia = sum(consumos.get(eq, {}).get(dia, 0) for eq in equipos)
                    c = ws.cell(row=r, column=col_dias_start + di)
                    c.value = round(sum_dia, 2) if sum_dia else None
                    # Semáforo: verde si no superó autorizado diario, rojo si lo superó
                    if auto_dia > 0 and sum_dia > auto_dia:
                        sem_bg = 'FECACA'   # rojo claro
                        sem_fg = '991B1B'   # rojo oscuro
                    else:
                        sem_bg = 'BBF7D0'   # verde claro
                        sem_fg = '14532D'   # verde oscuro
                    c.fill = fill(sem_bg)
                    c.font = font(bold=True, color=sem_fg, size=9)
                    c.alignment = align('center', 'center')
                    c.border = thin_border()

                c = ws.cell(row=r, column=col_total_lts)
                c.value = round(tot_lts_semana, 2) if tot_lts_semana else None
                c.fill = fill(COL_TOT_FILL)
                c.font = font(bold=True, color=WHITE, size=9)
                c.alignment = align('right', 'center')
                c.border = thin_border()

                c = ws.cell(row=r, column=col_precio)
                c.fill = fill(COL_TOT_FILL)
                c.border = thin_border()

                c = ws.cell(row=r, column=col_total_imp)
                c.value = round(tot_lts_semana * precio, 2) if tot_lts_semana else None
                c.fill = fill(COL_TOT_FILL)
                c.font = font(bold=True, color=WHITE, size=9)
                c.alignment = align('right', 'center')
                c.border = thin_border()
                c.number_format = '"$"#,##0.00'

                ws.row_dimensions[r].height = 20
                r += 1

                # Fila: Importe Autorizado vs Real
                ws.merge_cells(f'F{r}:{get_column_letter(col_precio)}{r}')
                c = ws.cell(row=r, column=6)
                c.value = f'IMPORTE SEMANAL AUTORIZADO: ${auto_sem * precio:,.2f}  (Litros aut.: {auto_sem:,.2f} L)'
                c.fill = fill(COL_IMP_FILL)
                c.font = font(bold=True, color=WHITE, size=9)
                c.alignment = align('right', 'center')
                c.border = thin_border()
                for gi in range(7, col_total_imp):
                    ws.cell(row=r, column=gi).fill = fill(COL_IMP_FILL)
                    ws.cell(row=r, column=gi).border = thin_border()

                total_real = tot_lts_semana * precio
                c = ws.cell(row=r, column=col_total_imp)
                rem_bg = COL_VERDE if auto_sem * precio >= total_real else COL_ROJO
                rem_fg = COL_VERDE_FNT if auto_sem * precio >= total_real else COL_ROJO_FNT
                c.value = round(total_real, 2)
                c.fill = fill(rem_bg)
                c.font = font(bold=True, color=rem_fg, size=9)
                c.alignment = align('right', 'center')
                c.border = thin_border()
                c.number_format = '"$"#,##0.00'
                ws.row_dimensions[r].height = 20
                r += 1

                # Espacio entre ingenieros
                r += 2

            # ── TABLA NUEVA: FACTURADO POR OBRA Y DÍA (FOLIOS, MONTOS Y LITROS) ──────
            r += 2
            try:
                target_schema = 'gasolina' if modulo == 'gasolina' else 'diesel'
                facturas_rows = db.execute(f"""
                    SELECT folio_factura, 
                           fecha_factura::text as fecha_str, 
                           COALESCE(NULLIF(obra_destino, ''), 'SIN OBRA') as obra,
                           COALESCE(importe_total, 0) as monto,
                           COALESCE(litros_facturados, 0) as litros
                    FROM {target_schema}.facturas
                    WHERE semana = %s AND (estatus_revision IS NULL OR estatus_revision = 'APROBADO')
                    ORDER BY fecha_str, folio_factura
                """, (semana_str,)).fetchall()
            except Exception as ex_fact:
                facturas_rows = []

            fact_matrix = {}
            fact_obras_set = set()
            fact_fechas_dict = {}

            DIAS_ES_FACT = {'Mon':'Lun','Tue':'Mar','Wed':'Mié','Thu':'Jue','Fri':'Vie','Sat':'Sáb','Sun':'Dom'}
            MESES_ES_FACT = {1:'ene',2:'feb',3:'mar',4:'abr',5:'may',6:'jun',7:'jul',8:'ago',9:'sep',10:'oct',11:'nov',12:'dic'}

            for fr in facturas_rows:
                f_date_raw = fr['fecha_str'] or 'Sin Fecha'
                f_obra = fr['obra'] or 'SIN OBRA'
                f_folio = fr['folio_factura'] or 'S/F'
                f_monto = float(fr['monto'] or 0)
                f_litros = float(fr['litros'] or 0)
                
                try:
                    d_obj = dt_module.datetime.strptime(f_date_raw, '%Y-%m-%d')
                    nom_d = DIAS_ES_FACT.get(d_obj.strftime('%a'), d_obj.strftime('%a'))
                    nom_m = MESES_ES_FACT.get(d_obj.month, str(d_obj.month))
                    fecha_fmt = f"{nom_d} {d_obj.day:02d}-{nom_m}"
                except Exception:
                    fecha_fmt = f_date_raw

                fact_fechas_dict[f_date_raw] = fecha_fmt
                fact_obras_set.add(f_obra)
                
                key = (f_obra, f_date_raw)
                if key not in fact_matrix:
                    fact_matrix[key] = []
                fact_matrix[key].append({
                    'folio': f_folio,
                    'monto': f_monto,
                    'litros': f_litros
                })

            sorted_fact_obras = sorted(list(fact_obras_set))
            sorted_fact_fechas_raw = sorted(list(fact_fechas_dict.keys()))

            if sorted_fact_obras and sorted_fact_fechas_raw:
                num_dias = len(sorted_fact_fechas_raw)
                tot_cols_cnt = 1 + num_dias * 3 + 3
                end_col_i = 6 + tot_cols_cnt - 1
                end_col_letter = get_column_letter(end_col_i)
                
                # Título de la tabla
                ws.merge_cells(f'F{r}:{end_col_letter}{r}')
                tc = ws.cell(row=r, column=6)
                tc.value = f'▶ FACTURADO POR OBRA Y DÍA — {modulo.upper()} (FOLIOS, MONTOS CON IVA Y LITROS — SEMANA {semana_num})'
                tc.fill = fill('1E3A5F')
                tc.font = font(bold=True, color=WHITE, size=11)
                tc.alignment = align('left', 'center')
                tc.border = thin_border()
                ws.row_dimensions[r].height = 24
                r += 1

                # Encabezados Fila 1: OBRA / DESTINO, [Día 1 (3 cols)], [Día 2 (3 cols)]... [TOTALES (3 cols)]
                ws.merge_cells(start_row=r, start_column=6, end_row=r+1, end_column=6)
                c_obra_hdr = ws.cell(row=r, column=6, value='OBRA / DESTINO')
                style_hdr(c_obra_hdr)
                ws.cell(row=r+1, column=6).border = thin_border()
                ws.cell(row=r+1, column=6).fill = fill(COL_HDR_FILL)
                ws.column_dimensions['F'].width = 25

                for f_idx, f_raw in enumerate(sorted_fact_fechas_raw):
                    day_col_start = 7 + f_idx * 3
                    day_col_end = day_col_start + 2
                    ws.merge_cells(start_row=r, start_column=day_col_start, end_row=r, end_column=day_col_end)
                    f_label = fact_fechas_dict[f_raw]
                    c = ws.cell(row=r, column=day_col_start)
                    style_hdr(c, f_label.upper())
                    for c_idx in range(day_col_start, day_col_end + 1):
                        style_hdr(ws.cell(row=r, column=c_idx))

                # Sección Totales Header Fila 1
                tot_col_start = 7 + num_dias * 3
                tot_col_end = tot_col_start + 2
                ws.merge_cells(start_row=r, start_column=tot_col_start, end_row=r, end_column=tot_col_end)
                c = ws.cell(row=r, column=tot_col_start)
                style_hdr(c, 'TOTALES ACUMULADOS')
                for c_idx in range(tot_col_start, tot_col_end + 1):
                    style_hdr(ws.cell(row=r, column=c_idx))

                ws.row_dimensions[r].height = 20
                r += 1

                # Encabezados Fila 2 (Sub-encabezados): FACTURA | MONTO ($) | LITROS por cada día
                for f_idx, f_raw in enumerate(sorted_fact_fechas_raw):
                    day_col_start = 7 + f_idx * 3
                    c0 = ws.cell(row=r, column=day_col_start + 0, value='FACTURA'); style_hdr(c0)
                    c1 = ws.cell(row=r, column=day_col_start + 1, value='MONTO ($)'); style_hdr(c1)
                    c2 = ws.cell(row=r, column=day_col_start + 2, value='LITROS'); style_hdr(c2)
                    ws.column_dimensions[get_column_letter(day_col_start + 0)].width = 16
                    ws.column_dimensions[get_column_letter(day_col_start + 1)].width = 15
                    ws.column_dimensions[get_column_letter(day_col_start + 2)].width = 13

                # Sub-encabezados Totales
                c0 = ws.cell(row=r, column=tot_col_start + 0, value='TOTAL FACTURAS'); style_hdr(c0)
                c1 = ws.cell(row=r, column=tot_col_start + 1, value='TOTAL MONTO'); style_hdr(c1)
                c2 = ws.cell(row=r, column=tot_col_start + 2, value='TOTAL LITROS'); style_hdr(c2)
                ws.column_dimensions[get_column_letter(tot_col_start + 0)].width = 16
                ws.column_dimensions[get_column_letter(tot_col_start + 1)].width = 18
                ws.column_dimensions[get_column_letter(tot_col_start + 2)].width = 15

                ws.row_dimensions[r].height = 20
                r += 1

                # Filas por Obra
                for o_idx, obra_nom in enumerate(sorted_fact_obras):
                    bg_f = COL_ALT1 if o_idx % 2 == 0 else COL_ALT2

                    c = ws.cell(row=r, column=6, value=obra_nom)
                    c.fill = fill(bg_f)
                    c.font = font(bold=True, size=9)
                    c.alignment = align('left', 'center')
                    c.border = thin_border()

                    tot_obra_cnt = 0
                    tot_obra_monto = 0.0
                    tot_obra_litros = 0.0

                    for f_idx, f_raw in enumerate(sorted_fact_fechas_raw):
                        day_col_start = 7 + f_idx * 3
                        inv_items = fact_matrix.get((obra_nom, f_raw), [])

                        if inv_items:
                            folios_str = ', '.join([x['folio'] for x in inv_items])
                            d_monto = sum(x['monto'] for x in inv_items)
                            d_litros = sum(x['litros'] for x in inv_items)
                            tot_obra_cnt += len(inv_items)
                            tot_obra_monto += d_monto
                            tot_obra_litros += d_litros
                            bg_cell = 'E0F2FE'
                        else:
                            folios_str = '-'
                            d_monto = None
                            d_litros = None
                            bg_cell = bg_f

                        # Sub-col 0: Factura(s)
                        c0 = ws.cell(row=r, column=day_col_start + 0, value=folios_str)
                        c0.fill = fill(bg_cell)
                        c0.font = font(bold=bool(inv_items), color='0369A1' if inv_items else '94A3B8', size=9)
                        c0.alignment = align('center', 'center', wrap=True)
                        c0.border = thin_border()

                        # Sub-col 1: Monto con IVA ($)
                        c1 = ws.cell(row=r, column=day_col_start + 1, value=d_monto if d_monto is not None else '-')
                        c1.fill = fill(bg_cell)
                        c1.font = font(bold=bool(inv_items), color='0F172A' if inv_items else '94A3B8', size=9)
                        c1.alignment = align('right' if d_monto is not None else 'center', 'center')
                        c1.border = thin_border()
                        if d_monto is not None:
                            c1.number_format = '"$"#,##0.00'

                        # Sub-col 2: Litros
                        c2 = ws.cell(row=r, column=day_col_start + 2, value=d_litros if d_litros is not None else '-')
                        c2.fill = fill(bg_cell)
                        c2.font = font(bold=bool(inv_items), color='0F172A' if inv_items else '94A3B8', size=9)
                        c2.alignment = align('right' if d_litros is not None else 'center', 'center')
                        c2.border = thin_border()
                        if d_litros is not None:
                            c2.number_format = '#,##0.00'

                    # Celdas Total Obra
                    c0 = ws.cell(row=r, column=tot_col_start + 0, value=f"{tot_obra_cnt} Factura(s)" if tot_obra_cnt > 0 else '-')
                    c0.fill = fill(bg_f)
                    c0.font = font(bold=True, color='0F172A', size=9)
                    c0.alignment = align('center', 'center')
                    c0.border = thin_border()

                    c1 = ws.cell(row=r, column=tot_col_start + 1, value=tot_obra_monto if tot_obra_cnt > 0 else '-')
                    c1.fill = fill(bg_f)
                    c1.font = font(bold=True, color='0F172A', size=9)
                    c1.alignment = align('right' if tot_obra_cnt > 0 else 'center', 'center')
                    c1.border = thin_border()
                    if tot_obra_cnt > 0:
                        c1.number_format = '"$"#,##0.00'

                    c2 = ws.cell(row=r, column=tot_col_start + 2, value=tot_obra_litros if tot_obra_cnt > 0 else '-')
                    c2.fill = fill(bg_f)
                    c2.font = font(bold=True, color='0F172A', size=9)
                    c2.alignment = align('right' if tot_obra_cnt > 0 else 'center', 'center')
                    c2.border = thin_border()
                    if tot_obra_cnt > 0:
                        c2.number_format = '#,##0.00'

                    ws.row_dimensions[r].height = 20
                    r += 1

                # Fila resumen total por día
                c = ws.cell(row=r, column=6, value='TOTAL POR DÍA')
                c.fill = fill(COL_TOT_FILL)
                c.font = font(bold=True, color=WHITE, size=9)
                c.alignment = align('right', 'center')
                c.border = thin_border()

                tot_global_cnt = 0
                tot_global_monto = 0.0
                tot_global_litros = 0.0

                for f_idx, f_raw in enumerate(sorted_fact_fechas_raw):
                    day_col_start = 7 + f_idx * 3
                    day_tot_cnt = sum(len(fact_matrix.get((o_nom, f_raw), [])) for o_nom in sorted_fact_obras)
                    day_tot_monto = sum(sum(x['monto'] for x in fact_matrix.get((o_nom, f_raw), [])) for o_nom in sorted_fact_obras)
                    day_tot_litros = sum(sum(x['litros'] for x in fact_matrix.get((o_nom, f_raw), [])) for o_nom in sorted_fact_obras)

                    tot_global_cnt += day_tot_cnt
                    tot_global_monto += day_tot_monto
                    tot_global_litros += day_tot_litros

                    c0 = ws.cell(row=r, column=day_col_start + 0, value=f"{day_tot_cnt} Factura(s)" if day_tot_cnt > 0 else '-')
                    c0.fill = fill(COL_TOT_FILL)
                    c0.font = font(bold=True, color=WHITE, size=9)
                    c0.alignment = align('center', 'center')
                    c0.border = thin_border()

                    c1 = ws.cell(row=r, column=day_col_start + 1, value=day_tot_monto if day_tot_cnt > 0 else '-')
                    c1.fill = fill(COL_TOT_FILL)
                    c1.font = font(bold=True, color=WHITE, size=9)
                    c1.alignment = align('right' if day_tot_cnt > 0 else 'center', 'center')
                    c1.border = thin_border()
                    if day_tot_cnt > 0:
                        c1.number_format = '"$"#,##0.00'

                    c2 = ws.cell(row=r, column=day_col_start + 2, value=day_tot_litros if day_tot_cnt > 0 else '-')
                    c2.fill = fill(COL_TOT_FILL)
                    c2.font = font(bold=True, color=WHITE, size=9)
                    c2.alignment = align('right' if day_tot_cnt > 0 else 'center', 'center')
                    c2.border = thin_border()
                    if day_tot_cnt > 0:
                        c2.number_format = '#,##0.00'

                # Celdas Total Global
                c0 = ws.cell(row=r, column=tot_col_start + 0, value=f"{tot_global_cnt} Factura(s)")
                c0.fill = fill(COL_TOT_FILL)
                c0.font = font(bold=True, color=WHITE, size=9)
                c0.alignment = align('center', 'center')
                c0.border = thin_border()

                c1 = ws.cell(row=r, column=tot_col_start + 1, value=tot_global_monto)
                c1.fill = fill(COL_TOT_FILL)
                c1.font = font(bold=True, color=WHITE, size=9)
                c1.alignment = align('right', 'center')
                c1.border = thin_border()
                c1.number_format = '"$"#,##0.00'

                c2 = ws.cell(row=r, column=tot_col_start + 2, value=tot_global_litros)
                c2.fill = fill(COL_TOT_FILL)
                c2.font = font(bold=True, color=WHITE, size=9)
                c2.alignment = align('right', 'center')
                c2.border = thin_border()
                c2.number_format = '#,##0.00'

                ws.row_dimensions[r].height = 22
                r += 1

        db.close()

        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)

        hoy = dt_module.datetime.now().strftime('%Y%m%d')
        filename = f'Reporte_Diesel_Semanal_{hoy}.xlsx'

        from flask import send_file
        return send_file(
            buf,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# API: GENERADOR DE REPORTES PDF
# ═══════════════════════════════════════════════════════════════════════════════
@app.route('/api/admin/reporte/pdf')
def api_generar_reporte_pdf():
    try:
        from reportlab.lib.pagesizes import letter, landscape
        from reportlab.lib import colors
        from reportlab.lib.units import inch, cm
        from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle, Paragraph,
                                        Spacer, HRFlowable, Image, PageBreak, KeepTogether)
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
        from collections import defaultdict
        import datetime as dt_module
        import io

        semana_param = request.args.get('semana', 'TODOS')
        modulo = request.args.get('modulo', 'diesel')

        db = get_db()

        # ── Colores ────────────────────────────────────────────────────────────
        C_HDR       = colors.HexColor('#1E293B')   # encabezado oscuro
        C_ING       = colors.HexColor('#312E81')   # fila ingeniero
        C_TOT       = colors.HexColor('#1E3A5F')   # fila total litros
        C_IMP       = colors.HexColor('#2D1B69')   # fila importe
        C_VERDE     = colors.HexColor('#10B981')
        C_ROJO      = colors.HexColor('#EF4444')
        C_AMARILLO  = colors.HexColor('#F59E0B')
        C_AZUL_C    = colors.HexColor('#38BDF8')
        C_MORADO    = colors.HexColor('#A78BFA')
        C_ROSA      = colors.HexColor('#F472B6')
        C_GRIS1     = colors.HexColor('#F8FAFC')
        C_GRIS2     = colors.HexColor('#F1F5F9')
        C_GRIS_BRD  = colors.HexColor('#CBD5E1')
        C_TXT       = colors.HexColor('#0F172A')
        C_TXT_MED   = colors.HexColor('#64748B')

        # ── Estilos ─────────────────────────────────────────────────────────────
        st_seccion = ParagraphStyle('sec', fontName='Helvetica-Bold', fontSize=11,
                                    textColor=C_HDR, spaceBefore=14, spaceAfter=5)
        st_footer  = ParagraphStyle('ftr', fontName='Helvetica', fontSize=7.5,
                                    textColor=C_TXT_MED, alignment=TA_CENTER)
        def p(txt, bold=False, size=8, color=C_TXT, align=TA_LEFT):
            fn = 'Helvetica-Bold' if bold else 'Helvetica'
            return Paragraph(f'<font name="{fn}" size="{size}" color="{color}">{txt}</font>', 
                           ParagraphStyle('x', fontName=fn, fontSize=size, textColor=color,
                                          alignment=align, leading=size+2))

        def ph(txt, size=7.5, align=TA_CENTER):
            return p(f'<b>{txt}</b>', bold=True, size=size, color=colors.white, align=align)

        def fmt(n, decimals=2):
            if n is None or n == 0: return ''
            return f'{float(n):,.{decimals}f}'

        def fmt0(n):
            if n is None: return ''
            return f'{float(n):,.2f}' if float(n) != 0 else ''

        # ── Parámetros de semana ─────────────────────────────────────────────
        semana_num = None
        semana_limpia = ''
        if semana_param != 'TODOS':
            semana_limpia = str(semana_param).replace('Semana ', '').strip()
            try:
                semana_num = int(semana_limpia)
            except:
                pass
        semana_label = f'Semana {semana_limpia}' if semana_num else 'Histórico'
        modulo_label = 'Diésel' if modulo == 'diesel' else 'Gasolina'
        hoy = dt_module.datetime.now()

        # ── Autorizaciones ───────────────────────────────────────────────────
        auth_map = {}  # responsable -> litros_dia
        if modulo == 'diesel' and semana_num:
            try:
                auth_rows = db.execute(
                    "SELECT referencia, litros_autorizados FROM catalogos.autorizaciones WHERE tipo='DIESEL' AND semana=%s",
                    (semana_num,)
                ).fetchall()
                for ar in auth_rows:
                    auth_map[ar['referencia']] = float(ar['litros_autorizados'] or 0)
            except:
                pass

        # ── Query base ───────────────────────────────────────────────────────
        cond = "WHERE estatus_revision = 'APROBADO' AND (obra_destino IS NULL OR obra_destino NOT ILIKE %s)"
        params = ['%Tanque Pegaso%']
        if semana_num:
            cond += " AND semana = %s"
            params.append(str(semana_num))

        # ── Días trabajados (para columna semanal) ────────────────────────────
        try:
            dias_row = db.execute(
                f"SELECT COUNT(DISTINCT fecha) as dias FROM diesel.consumos {cond}",
                tuple(params)
            ).fetchone()
            dias_trabajados = int(dias_row['dias']) if dias_row and dias_row['dias'] else 7
            if dias_trabajados == 0: dias_trabajados = 7
        except:
            dias_trabajados = 7

        # ── Datos Tabla 4: pivot responsable -> obra -> litros ───────────────
        try:
            rows_pivot = db.execute(f"""
                SELECT COALESCE(NULLIF(NULLIF(responsable,'nan'),''),'S/R') as resp,
                       obra_destino,
                       SUM(litros) as litros
                FROM diesel.consumos
                {cond}
                GROUP BY COALESCE(NULLIF(NULLIF(responsable,'nan'),''),'S/R'), obra_destino
                ORDER BY resp, obra_destino
            """, tuple(params)).fetchall()
        except:
            rows_pivot = []

        # ── Datos Tabla 5: por responsable, fecha, equipo ─────────────────────
        try:
            rows_maq = db.execute(f"""
                SELECT COALESCE(NULLIF(NULLIF(responsable,'nan'),''),'S/R') as resp,
                       fecha::text as fecha_str,
                       obra_destino,
                       COALESCE(NULLIF(equipo,''),'SIN EQUIPO') as equipo,
                       SUM(litros) as litros,
                       AVG(costo_por_litro) as precio_unit
                FROM diesel.consumos
                {cond}
                GROUP BY COALESCE(NULLIF(NULLIF(responsable,'nan'),''),'S/R'),
                         fecha::text, obra_destino,
                         COALESCE(NULLIF(equipo,''),'SIN EQUIPO')
                ORDER BY resp, fecha::text, equipo
            """, tuple(params)).fetchall()
        except:
            rows_maq = []

        db.close()

        # ── Estructurar datos Tabla 5 ─────────────────────────────────────────
        # ing_data[resp] = {dias: set, equipos: set, consumos:{eq:{fecha:lts}}, obras:{fecha:obra}, precio:float}
        from collections import OrderedDict
        ing_data = OrderedDict()
        for r in rows_maq:
            resp = r['resp']
            if resp == 'S/R': continue
            fecha = r['fecha_str']
            eq = r['equipo']
            lts = float(r['litros'] or 0)
            if resp not in ing_data:
                ing_data[resp] = {'dias': set(), 'equipos': set(), 'consumos': {}, 'obras': {}, 'precio': 27.0}
            d = ing_data[resp]
            d['dias'].add(fecha)
            d['equipos'].add(eq)
            d['consumos'].setdefault(eq, {})[fecha] = d['consumos'].get(eq, {}).get(fecha, 0) + lts
            if fecha not in d['obras']:
                d['obras'][fecha] = r['obra_destino'] or ''
            if r['precio_unit']:
                d['precio'] = float(r['precio_unit'])

        # Sort
        for resp, d in ing_data.items():
            d['dias'] = sorted(d['dias'])
            d['equipos'] = sorted(d['equipos'])

        # ── DOCUMENTO ────────────────────────────────────────────────────────
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=landscape(letter),
                                leftMargin=1.2*cm, rightMargin=1.2*cm,
                                topMargin=1.5*cm, bottomMargin=1.8*cm)
        story = []

        # ── ENCABEZADO ────────────────────────────────────────────────────────
        logo_path = os.path.join(os.path.dirname(__file__), 'servidor', 'static', 'logo_empresa.png')
        logo_cell = Image(logo_path, width=3*cm, height=1.5*cm) if os.path.exists(logo_path) else p('GRUPO TRUJANO', bold=True, size=14)
        hdr_tbl = Table([[
            logo_cell,
            p('<b>GRUPO TRUJANO</b><br/>'
              f'<font size="11" color="#4F46E5">Reporte de Control de Combustible — {modulo_label}</font>',
              bold=True, size=15, color=C_HDR),
            p(f'<b>Periodo:</b> {semana_label}<br/>'
              f'<b>Generado:</b> {hoy.strftime("%d/%m/%Y %H:%M")}<br/>'
              f'<b>Días trabajados:</b> {dias_trabajados}',
              size=8.5, color=C_TXT_MED, align=TA_RIGHT)
        ]], colWidths=[4*cm, 15*cm, 6*cm])
        hdr_tbl.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LINEBELOW', (0,0), (-1,0), 1.5, colors.HexColor('#4F46E5')),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ]))
        story.append(hdr_tbl)
        story.append(Spacer(1, 0.3*cm))

        # ================================================================
        # TABLA 4: CONSUMO SEMANAL — INGENIEROS Y OBRAS
        # ================================================================
        story.append(p('Tabla 4 – Consumo Semanal por Ingeniero y Obra', bold=True, size=10.5, color=C_HDR))
        story.append(p(f'Autorizado Diario × {dias_trabajados} días trabajados = Columna Semanal. '
                       'Verde = dentro del límite · Rojo = excedido.', size=8, color=C_TXT_MED))
        story.append(Spacer(1, 0.2*cm))

        # Agrupar datos pivot
        resp_obras_dict = {}  # resp -> {obra -> litros}
        for r in rows_pivot:
            resp = r['resp']
            if resp not in resp_obras_dict:
                resp_obras_dict[resp] = {}
            resp_obras_dict[resp][r['obra_destino']] = float(r['litros'] or 0)

        todos_resps = sorted(set(list(resp_obras_dict.keys()) + list(auth_map.keys())))

        # Cargar dias_trabajados de la base de datos
        dias_map_pdf = {}
        try:
            r_db_pdf = db.execute("SELECT nombre, dias_trabajados FROM catalogos.responsables").fetchall()
            for r_item in r_db_pdf:
                if r_item['nombre']:
                    dias_map_pdf[r_item['nombre'].strip().upper()] = int(r_item['dias_trabajados'] or 6)
        except Exception as e:
            pass

        def get_dias_pdf(r_name):
            un = str(r_name or '').strip().upper()
            for k, v in dias_map_pdf.items():
                if k in un or un in k:
                    return v
            if any(x in un for x in ['DAYANNE', 'EDGAR', 'SAMUEL']):
                return 5
            return 6

        # Encabezados y estilos
        T4_HDR_BG = C_HDR
        COL_W4 = [4.2*cm, 5.5*cm, 2.8*cm, 2.8*cm, 2.8*cm, 3.2*cm, 3.2*cm]

        # Agrupar responsables por días
        resps_pdf_by_days = OrderedDict()
        for resp in todos_resps:
            if resp == 'S/R':
                continue
            d_val = get_dias_pdf(resp)
            resps_pdf_by_days.setdefault(d_val, []).append(resp)

        t4_data = []
        t4_styles = [
            ('GRID',       (0,0), (-1,-1), 0.3, C_GRIS_BRD),
            ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING',   (0,0), (-1,-1), 5),
        ]

        row_idx = 0
        tot_sem_gen = tot_con_gen = 0

        for d_val in sorted(resps_pdf_by_days.keys(), reverse=True):
            group_resps = resps_pdf_by_days[d_val]

            # Fila Encabezado de Sección por Días
            hdr_row = [
                ph('RESPONSABLE'), ph('OBRA'),
                ph('AUTORIZADO\nDIARIO'), ph(f'SEMANAL\n({d_val} DÍAS)'),
                ph('CONSUMO\nPOR OBRA'), ph('CONSUMO\nPOR INGENIERO'), ph('REMANENTE\nPOR INGENIERO')
            ]
            t4_data.append(hdr_row)
            t4_styles += [
                ('BACKGROUND', (0, row_idx), (-1, row_idx), T4_HDR_BG),
                ('TEXTCOLOR',  (0, row_idx), (-1, row_idx), colors.white),
                ('FONTNAME',   (0, row_idx), (-1, row_idx), 'Helvetica-Bold'),
                ('ALIGN',      (2, row_idx), (-1, row_idx), 'CENTER'),
            ]
            row_idx += 1

            tot_sem_sec = tot_con_sec = 0

            for resp in group_resps:
                auto_dia = auth_map.get(resp, 0)
                auto_sem = auto_dia * float(d_val)
                obras_d = resp_obras_dict.get(resp, {})
                obras_sorted = sorted(obras_d.keys()) if obras_d else ['SIN CONSUMOS']
                n = len(obras_sorted)
                con_ing = sum(obras_d.values())
                
                remanente = auto_sem - con_ing
                tot_sem_sec += auto_sem
                tot_con_sec += con_ing

                rem_c = C_ROJO if remanente < 0 else C_VERDE
                rem_txt = ('+' if remanente > 0 else '') + f'{remanente:,.2f}'

                ing_bg = colors.HexColor('#EEF2FF')

                if n > 1:
                    for col in [0, 2, 3, 5, 6]:
                        t4_styles.append(('SPAN', (col, row_idx), (col, row_idx + n - 1)))

                for i, obra in enumerate(obras_sorted):
                    lts_obra = obras_d.get(obra, 0)
                    row = [
                        p(f'<b>{resp}</b>', bold=True, size=8) if i == 0 else '',
                        p(obra, size=8, color=C_TXT_MED if i > 0 else C_TXT),
                        p(f'<b>{fmt(auto_dia) if auto_dia > 0 else ""}</b>', bold=True, size=8, align=TA_RIGHT) if i == 0 else '',
                        p(f'<b>{fmt(auto_sem) if auto_sem > 0 else ""}</b>', bold=True, size=8, color=C_AZUL_C, align=TA_RIGHT) if i == 0 else '',
                        p(f'{fmt(lts_obra) if lts_obra > 0 else ""}', size=8, align=TA_RIGHT),
                        p(f'<b>{fmt(con_ing) if con_ing > 0 else ""}</b>', bold=True, size=8, align=TA_RIGHT) if i == 0 else '',
                        p(f'<b>{rem_txt}</b>', bold=True, size=8, color=rem_c, align=TA_RIGHT) if i == 0 else '',
                    ]
                    t4_data.append(row)
                    if i == 0:
                        t4_styles.append(('BACKGROUND', (0, row_idx), (-1, row_idx), ing_bg))
                    row_idx += 1

            # Fila Subtotal por Sección de Días
            rem_sec = tot_sem_sec - tot_con_sec
            t4_data.append([
                ph(f'SUBTOTAL ({d_val} DÍAS):'), '', '',
                ph(f'{tot_sem_sec:,.2f}', size=8),
                ph(f'{tot_con_sec:,.2f}', size=8),
                ph(f'{tot_con_sec:,.2f}', size=8),
                Paragraph(f'<b><font color="{"#EF4444" if rem_sec < 0 else "#10B981"}" size="8">{("+") if rem_sec > 0 else ""}{rem_sec:,.2f}</font></b>', ParagraphStyle('x', alignment=TA_RIGHT)),
            ])
            t4_styles += [
                ('SPAN',       (0, row_idx), (2, row_idx)),
                ('BACKGROUND', (0, row_idx), (-1, row_idx), colors.HexColor('#312E81')),
                ('TEXTCOLOR',  (0, row_idx), (-1, row_idx), colors.white),
                ('FONTNAME',   (0, row_idx), (-1, row_idx), 'Helvetica-Bold'),
            ]
            row_idx += 1

            tot_sem_gen += tot_sem_sec
            tot_con_gen += tot_con_sec

        # Fila TOTAL GENERAL
        rem_tot_gen = tot_sem_gen - tot_con_gen
        t4_data.append([
            ph('TOTAL GENERAL:'), '', '',
            ph(f'{tot_sem_gen:,.2f}', size=8),
            ph(f'{tot_con_gen:,.2f}', size=8),
            ph(f'{tot_con_gen:,.2f}', size=8),
            Paragraph(f'<b><font color="{"#EF4444" if rem_tot_gen < 0 else "#10B981"}" size="8">{("+") if rem_tot_gen > 0 else ""}{rem_tot_gen:,.2f}</font></b>', ParagraphStyle('x', alignment=TA_RIGHT)),
        ])
        t4_styles += [
            ('SPAN',       (0, row_idx), (2, row_idx)),
            ('BACKGROUND', (0, row_idx), (-1, row_idx), C_HDR),
            ('TEXTCOLOR',  (0, row_idx), (-1, row_idx), colors.white),
            ('FONTNAME',   (0, row_idx), (-1, row_idx), 'Helvetica-Bold'),
        ]

        t4 = Table(t4_data, colWidths=COL_W4, repeatRows=1)
        t4.setStyle(TableStyle(t4_styles))
        story.append(t4)

        # ================================================================
        # TABLA 5: UNA TABLA POR INGENIERO — CONSUMO DIARIO POR MAQUINARIA
        # ================================================================
        story.append(PageBreak())
        story.append(p('Tabla 5 – Consumo Diario por Maquinaria (Detalle por Ingeniero)', bold=True, size=10.5, color=C_HDR))
        story.append(p('Una tabla por Ingeniero Responsable. Columnas = días trabajados en la semana. '
                       'Filas = Equipo / Maquinaria. Última fila = Importe ($precio/L × litros).',
                       size=8, color=C_TXT_MED))
        story.append(Spacer(1, 0.3*cm))

        DIAS_ABREV = {0:'LUN', 1:'MAR', 2:'MIE', 3:'JUE', 4:'VIE', 5:'SAB', 6:'DOM'}

        def fmt_fecha_col(f):
            try:
                fd = dt_module.datetime.strptime(f, '%Y-%m-%d').date()
                return f'{DIAS_ABREV.get(fd.weekday(),"")}\n{fd.strftime("%d/%m")}'
            except:
                return str(f)

        for resp, d in ing_data.items():
            dias = d['dias']
            equipos = d['equipos']
            consumos = d['consumos']
            obras_dia = d['obras']
            precio = d['precio']
            auto_dia = auth_map.get(resp, 0)
            auto_sem = auto_dia * len(dias)

            if not dias or not equipos:
                continue

            # Total por día y por equipo
            total_por_dia = {f: sum(consumos.get(eq, {}).get(f, 0) for eq in equipos) for f in dias}
            total_por_eq  = {eq: sum(consumos.get(eq, {}).values()) for eq in equipos}
            gran_total = sum(total_por_dia.values())
            costo_por_dia = {f: total_por_dia[f] * precio for f in dias}
            costo_total = gran_total * precio

            n_dias = len(dias)
            # Ancho dinámico: fija equipos col + imp.aut. col + días + total
            eq_col_w = 4.5*cm
            aut_col_w = 2.5*cm
            dia_col_w = min(max(1.8*cm, 16.0*cm / max(n_dias, 1)), 2.8*cm)
            tot_col_w = 2.5*cm
            total_w = eq_col_w + aut_col_w + dia_col_w * n_dias + tot_col_w

            col_ws = [eq_col_w, aut_col_w] + [dia_col_w] * n_dias + [tot_col_w]

            # Header bloque ingeniero
            rem = auto_sem - gran_total
            rem_c = C_ROJO if rem < 0 else C_VERDE
            rem_sign = '+' if rem > 0 else ''
            ing_header = Table([[
                p(f'<b>👷 {resp}</b>', bold=True, size=10, color=colors.white),
                p(f'<b>Aut/día:</b> {auto_dia:,.0f} L  |  '
                  f'<b>Aut. semanal:</b> {auto_sem:,.0f} L  |  '
                  f'<b>Consumido:</b> {gran_total:,.2f} L  |  '
                  f'<b>Remanente:</b> {rem_sign}{rem:,.2f} L  |  '
                  f'<b>Importe:</b> ${costo_total:,.2f}',
                  size=8.5, color=colors.HexColor('#CBD5E1'))
            ]], colWidths=[5*cm, total_w - 5*cm])
            ing_header.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), C_ING),
                ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('LEFTPADDING', (0,0), (-1,-1), 8),
                ('ROUNDEDCORNERS', [4, 4, 0, 0]),
            ]))
            story.append(ing_header)

            # --- Datos de la tabla ---
            t5_data = []
            t5_styles = [
                ('GRID',    (0,0), (-1,-1), 0.3, C_GRIS_BRD),
                ('VALIGN',  (0,0), (-1,-1), 'MIDDLE'),
                ('TOPPADDING',    (0,0), (-1,-1), 3),
                ('BOTTOMPADDING', (0,0), (-1,-1), 3),
                ('LEFTPADDING',   (0,0), (-1,-1), 4),
            ]

            # Fila 1 header: EQUIPO | IMP.SEM.AUT | Dia1 | Dia2 | ... | TOTAL
            hdr_row = [ph('EQUIPO / MAQUINARIA', size=7), ph(f'IMP. SEM.\nAUTORIZADO', size=7)]
            hdr_row += [ph(fmt_fecha_col(f), size=7) for f in dias]
            hdr_row += [ph('LITROS\nTOTAL', size=7)]
            t5_data.append(hdr_row)
            t5_styles.append(('BACKGROUND', (0,0), (-1,0), C_HDR))
            t5_styles.append(('TEXTCOLOR',  (0,0), (-1,0), colors.white))

            # Fila 2: OBRA por día
            obra_row = [p('OBRA', size=6.5, color=C_TXT_MED), '']
            obra_row += [p(obras_dia.get(f, ''), size=6.5, color=C_TXT_MED, align=TA_CENTER) for f in dias]
            obra_row += ['']
            t5_data.append(obra_row)
            t5_styles.append(('BACKGROUND', (0,1), (-1,1), colors.HexColor('#F8FAFC')))
            t5_styles.append(('FONTNAME',   (0,1), (-1,1), 'Helvetica-Oblique'))

            # Filas de equipos
            for eq_i, eq in enumerate(equipos):
                bg = C_GRIS1 if eq_i % 2 == 0 else colors.white
                eq_row = [p(eq, size=7.5), p(f'${auto_sem:,.0f}' if eq_i == 0 else '', size=7.5, color=C_AMARILLO, align=TA_CENTER)]
                for f in dias:
                    val = consumos.get(eq, {}).get(f, 0)
                    eq_row.append(p(f'<b>{val:,.2f}</b>' if val > 0 else '', size=8, align=TA_CENTER))
                eq_row.append(p(f'<b>{total_por_eq.get(eq,0):,.2f}</b>', bold=True, size=8, color=C_ROSA, align=TA_RIGHT))
                t5_data.append(eq_row)
                t5_styles.append(('BACKGROUND', (0, eq_i+2), (-1, eq_i+2), bg))

            n_eq = len(equipos)
            # Fila TOTAL LITROS
            tot_row = [p('<b>TOTAL LITROS</b>', bold=True, size=8, color=C_AZUL_C), '']
            tot_row += [p(f'<b>{total_por_dia[f]:,.2f}</b>', bold=True, size=8, color=C_AZUL_C, align=TA_CENTER) for f in dias]
            tot_row += [p(f'<b>{gran_total:,.2f}</b>', bold=True, size=8, color=C_AZUL_C, align=TA_RIGHT)]
            t5_data.append(tot_row)
            tot_row_idx = n_eq + 2
            t5_styles.append(('BACKGROUND', (0, tot_row_idx), (-1, tot_row_idx), colors.HexColor('#E0F2FE')))
            t5_styles.append(('FONTNAME',   (0, tot_row_idx), (-1, tot_row_idx), 'Helvetica-Bold'))
            t5_styles.append(('LINEABOVE',  (0, tot_row_idx), (-1, tot_row_idx), 1.5, C_AZUL_C))

            # Fila IMPORTE
            imp_row = [p(f'<b>IMPORTE (${precio:,.2f}/L)</b>', bold=True, size=8, color=C_MORADO),
                       p(f'<b>${costo_total:,.2f}</b>', bold=True, size=8, color=C_MORADO, align=TA_CENTER)]
            imp_row += [p(f'<b>${costo_por_dia[f]:,.2f}</b>', bold=True, size=8, color=C_MORADO, align=TA_CENTER) for f in dias]
            imp_row += [p(f'<b>${costo_total:,.2f}</b>', bold=True, size=8, color=C_MORADO, align=TA_RIGHT)]
            t5_data.append(imp_row)
            imp_row_idx = tot_row_idx + 1
            t5_styles.append(('BACKGROUND', (0, imp_row_idx), (-1, imp_row_idx), colors.HexColor('#EDE9FE')))
            t5_styles.append(('FONTNAME',   (0, imp_row_idx), (-1, imp_row_idx), 'Helvetica-Bold'))

            t5 = Table(t5_data, colWidths=col_ws, repeatRows=2)
            t5.setStyle(TableStyle(t5_styles))
            story.append(t5)
            story.append(Spacer(1, 0.5*cm))

        # ── FOOTER ───────────────────────────────────────────────────────────
        story.append(HRFlowable(width='100%', thickness=0.5, color=C_GRIS_BRD))
        story.append(Spacer(1, 0.15*cm))
        story.append(Paragraph(
            f'Reporte generado por Sistema Fénix 2.0 · Grupo Trujano · {hoy.strftime("%d/%m/%Y %H:%M")} · Documento de uso interno y confidencial.',
            st_footer))

        doc.build(story)
        buf.seek(0)
        from flask import send_file as flask_send_file
        return flask_send_file(buf, mimetype='application/pdf',
                               as_attachment=True,
                               download_name=f'Reporte_{modulo_label}_{semana_label.replace(" ","_")}_{hoy.strftime("%Y%m%d_%H%M")}.pdf')

    except Exception as e:
        import traceback
        return jsonify({'success': False, 'error': str(e), 'trace': traceback.format_exc()})

@app.route('/api/admin/resumen/conciliacion')
def api_resumen_conciliacion():
    db = get_db()
    modulo = request.args.get('modulo', 'diesel')
    semana = request.args.get('semana', 'TODOS')
    
    cond = "WHERE (obra_destino IS NULL OR (obra_destino NOT ILIKE %s AND obra_destino NOT ILIKE %s))"
    params_base = ['%Tanque Pegaso%', '%COSUM%']
    # Extract numeric week for autorizaciones (stored as integer)
    semana_num = None
    if semana != 'TODOS':
        semana_limpia = str(semana).replace('Semana ', '').strip()
        cond += " AND semana = %s"
        params_base.append(semana_limpia)
        try:
            semana_num = int(semana_limpia)
        except:
            semana_num = None
            
    params = params_base * 3
        
    if modulo == 'diesel':
        # Fetch authorizations separately (stored by numeric week)
        auth_map = {}
        if semana_num:
            try:
                auth_rows = db.execute(
                    "SELECT referencia, litros_autorizados FROM catalogos.autorizaciones WHERE tipo='DIESEL' AND semana=%s",
                    (semana_num,)
                ).fetchall()
                for ar in auth_rows:
                    auth_map[ar['referencia']] = float(ar['litros_autorizados'] or 0)
            except:
                pass

        query = f"""
        WITH sol AS (
            SELECT obra_destino, fecha::text as fecha, SUM(litros) as solicitado, STRING_AGG(DISTINCT folio_solicitud, ', ') as folios_sol
            FROM diesel.solicitudes
            {cond.replace('semana', 'semana')} AND (estatus_conciliacion IS NULL OR estatus_conciliacion != 'CANCELADA')
            GROUP BY obra_destino, fecha
        ),
        con AS (
            SELECT obra_destino, fecha::text as fecha, SUM(litros) as consumido, STRING_AGG(DISTINCT folio_conciliacion, ', ') as folios_con,
            json_agg(json_build_object('equipo', equipo, 'litros', litros, 'folio', folio_conciliacion)) as detalle_equipos
            FROM diesel.consumos
            {cond.replace('semana', 'semana')} AND (estatus_revision IS NULL OR estatus_revision != 'CANCELADA')
            GROUP BY obra_destino, fecha
        ),
        fac AS (
            SELECT obra_destino, fecha_factura::text as fecha, SUM(litros_facturados) as facturado, STRING_AGG(DISTINCT folio_factura, ', ') as folios_fac
            FROM diesel.facturas
            {cond.replace('semana', 'semana')} AND (estatus_revision IS NULL OR estatus_revision != 'CANCELADA')
            GROUP BY obra_destino, fecha_factura
        ),
        fechas_obras AS (
            SELECT obra_destino, fecha FROM sol
            UNION
            SELECT obra_destino, fecha FROM con
            UNION
            SELECT obra_destino, fecha FROM fac
        )
        SELECT 
            fo.obra_destino as obra,
            fo.fecha as fecha,
            COALESCE(s.solicitado, 0) as solicitado,
            s.folios_sol,
            COALESCE(c.consumido, 0) as consumido,
            c.folios_con,
            c.detalle_equipos,
            COALESCE(f.facturado, 0) as facturado,
            f.folios_fac
        FROM fechas_obras fo
        LEFT JOIN sol s ON fo.obra_destino = s.obra_destino AND (fo.fecha = s.fecha OR (fo.fecha IS NULL AND s.fecha IS NULL))
        LEFT JOIN con c ON fo.obra_destino = c.obra_destino AND (fo.fecha = c.fecha OR (fo.fecha IS NULL AND c.fecha IS NULL))
        LEFT JOIN fac f ON fo.obra_destino = f.obra_destino AND (fo.fecha = f.fecha OR (fo.fecha IS NULL AND f.fecha IS NULL))
        WHERE fo.obra_destino IS NOT NULL
        ORDER BY fo.obra_destino, fo.fecha DESC
        """
        try:
            rows = db.execute(query, tuple(params) if params else ()).fetchall()
            db.close()
            result = []
            for r in rows:
                d = dict(r)
                d['autorizado'] = auth_map.get(d['obra'], 0)
                result.append(d)
            return jsonify(result)
        except Exception as e:
            print("ERROR SQL DIESEL:", e)
            db.close()
            return jsonify([])
            
    elif modulo == 'gasolina':
        if params: params.pop() # only 2 queries for gasolina
        query = f"""
        WITH con AS (
            SELECT obra_destino, fecha::text as fecha, SUM(litros) as consumido, STRING_AGG(DISTINCT folio_conciliacion, ', ') as folios_con,
            json_agg(json_build_object('equipo', equipo, 'litros', litros, 'folio', folio_conciliacion)) as detalle_equipos
            FROM gasolina.consumos
            {cond.replace('semana', 'semana')} AND (estatus_revision IS NULL OR estatus_revision != 'CANCELADA')
            GROUP BY obra_destino, fecha
        ),
        fac AS (
            SELECT c.obra_destino, c.fecha::text as fecha, SUM(f.litros_facturados) as facturado, STRING_AGG(DISTINCT f.folio_factura, ', ') as folios_fac
            FROM gasolina.facturas f
            LEFT JOIN (SELECT DISTINCT folio_conciliacion, obra_destino, fecha FROM gasolina.consumos) c 
              ON f.folio_conciliacion = c.folio_conciliacion
            {cond.replace('semana', 'f.semana')} AND (f.estatus_revision IS NULL OR f.estatus_revision != 'CANCELADA')
            GROUP BY c.obra_destino, c.fecha
        ),
        fechas_obras AS (
            SELECT obra_destino, fecha FROM con
            UNION
            SELECT obra_destino, fecha FROM fac
        )
        SELECT 
            fo.obra_destino as obra,
            fo.fecha as fecha,
            0 as solicitado,
            '' as folios_sol,
            COALESCE(c.consumido, 0) as consumido,
            c.folios_con,
            c.detalle_equipos,
            COALESCE(f.facturado, 0) as facturado,
            f.folios_fac
        FROM fechas_obras fo
        LEFT JOIN con c ON fo.obra_destino = c.obra_destino AND (fo.fecha = c.fecha OR (fo.fecha IS NULL AND c.fecha IS NULL))
        LEFT JOIN fac f ON fo.obra_destino = f.obra_destino AND (fo.fecha = f.fecha OR (fo.fecha IS NULL AND f.fecha IS NULL))
        WHERE fo.obra_destino IS NOT NULL
        ORDER BY fo.obra_destino, fo.fecha DESC
        """
        try:
            rows = db.execute(query, tuple(params) if params else ()).fetchall()
            db.close()
            return jsonify([dict(r) for r in rows])
        except Exception as e:
            print("ERROR SQL GASOLINA:", e)
            db.close()
            return jsonify([])
    
    db.close()
    return jsonify([])

@app.route('/api/admin/resumen/por-dia')
def api_resumen_por_dia():
    """Returns daily totals of facturas, solicitudes (pedido) and consumos for the selected week."""
    db = get_db()
    modulo  = request.args.get('modulo', 'diesel')
    semana  = request.args.get('semana', 'TODOS')

    cond_base = "WHERE (obra_destino IS NULL OR obra_destino NOT ILIKE %s)"
    params_base = ['%Tanque Pegaso%']

    if semana != 'TODOS':
        semana_limpia = str(semana).replace('Semana ', '').strip()
        cond_base += " AND semana = %s"
        params_base.append(semana_limpia)

    try:
        if modulo == 'diesel':
            # solicitudes por dia — solo APROBADAS
            q_sol = f"""
                SELECT fecha::text as dia, SUM(litros) as litros,
                       STRING_AGG(DISTINCT folio_solicitud, ', ') as folios
                FROM diesel.solicitudes {cond_base} AND estatus_conciliacion = 'APROBADO'
                GROUP BY fecha ORDER BY fecha
            """
            # consumos por dia — solo APROBADOS
            q_con = f"""
                SELECT fecha::text as dia, SUM(litros) as litros,
                       STRING_AGG(DISTINCT folio_conciliacion, ', ') as folios
                FROM diesel.consumos {cond_base} AND estatus_revision = 'APROBADO'
                GROUP BY fecha ORDER BY fecha
            """
            # facturas por dia — solo APROBADAS
            q_fac = f"""
                SELECT fecha_factura::text as dia, SUM(litros_facturados) as litros,
                       STRING_AGG(DISTINCT folio_factura, ', ') as folios
                FROM diesel.facturas {cond_base} AND estatus_revision = 'APROBADO'
                GROUP BY fecha_factura ORDER BY fecha_factura
            """
            rows_sol = db.execute(q_sol, tuple(params_base)).fetchall()
            rows_con = db.execute(q_con, tuple(params_base)).fetchall()
            rows_fac = db.execute(q_fac, tuple(params_base)).fetchall()

        elif modulo == 'gasolina':
            q_sol = "SELECT NULL::text as dia, 0 as litros, '' as folios WHERE 1=0"
            q_con = f"""
                SELECT fecha::text as dia, SUM(litros) as litros,
                       STRING_AGG(DISTINCT folio_conciliacion, ', ') as folios
                FROM gasolina.consumos {cond_base}
                GROUP BY fecha ORDER BY fecha
            """
            q_fac = f"""
                SELECT f.fecha_factura::text as dia, SUM(f.litros_facturados) as litros,
                       STRING_AGG(DISTINCT f.folio_factura, ', ') as folios
                FROM gasolina.facturas f {cond_base.replace('obra_destino', 'f.obra_destino')}
                GROUP BY f.fecha_factura ORDER BY f.fecha_factura
            """
            rows_sol = []
            rows_con = db.execute(q_con, tuple(params_base)).fetchall()
            rows_fac = db.execute(q_fac, tuple(params_base)).fetchall()
        else:
            db.close()
            return jsonify([])

        # Merge by day
        dias = {}
        for r in rows_sol:
            d = r['dia'] or 'S/F'
            dias.setdefault(d, {'dia': d, 'pedido': 0, 'consumido': 0, 'facturado': 0,
                                 'folios_sol': '', 'folios_con': '', 'folios_fac': ''})
            dias[d]['pedido'] += float(r['litros'] or 0)
            dias[d]['folios_sol'] = r['folios'] or ''
        for r in rows_con:
            d = r['dia'] or 'S/F'
            dias.setdefault(d, {'dia': d, 'pedido': 0, 'consumido': 0, 'facturado': 0,
                                 'folios_sol': '', 'folios_con': '', 'folios_fac': ''})
            dias[d]['consumido'] += float(r['litros'] or 0)
            dias[d]['folios_con'] = r['folios'] or ''
        for r in rows_fac:
            d = r['dia'] or 'S/F'
            dias.setdefault(d, {'dia': d, 'pedido': 0, 'consumido': 0, 'facturado': 0,
                                 'folios_sol': '', 'folios_con': '', 'folios_fac': ''})
            dias[d]['facturado'] += float(r['litros'] or 0)
            dias[d]['folios_fac'] = r['folios'] or ''

        db.close()
        return jsonify(sorted(dias.values(), key=lambda x: x['dia']))
    except Exception as e:
        import traceback
        db.close()
        print("ERROR por-dia:", traceback.format_exc())
        return jsonify([])

@app.route('/api/admin/resumen/responsables')
def api_resumen_responsables():
    """Returns totals grouped by Responsable (autorizado vs consumido)."""
    db = get_db()
    modulo  = request.args.get('modulo', 'diesel')
    semana  = request.args.get('semana', 'TODOS')

    if modulo != 'diesel':
        db.close()
        return jsonify([])

    semana_num = None
    cond_con = "WHERE (estatus_revision IS NULL OR estatus_revision != 'RECHAZADO') AND (obra_destino IS NULL OR obra_destino NOT ILIKE %s)"
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
        STD_AUTHS = {
            'APOLINAR': 400.0,
            'DAYANNE': 0.0,
            'DIEGO CARREOLA': 900.0,
            'EDGAR': 0.0,
            'FRANCISCO JAVIER': 550.0,
            'JACK': 400.0,
            'LUIS': 400.0,
            'SAMUEL': 0.0
        }

        auth_map = {}
        if semana_num:
            auth_rows = db.execute(
                "SELECT referencia, litros_autorizados FROM catalogos.autorizaciones WHERE tipo='DIESEL' AND semana=%s",
                (semana_num,)
            ).fetchall()
            for ar in auth_rows:
                ref = ar['referencia']
                lts = float(ar['litros_autorizados'] or 0)
                if 'CARREOLA' in ref.upper() or 'DIEGO' in ref.upper():
                    auth_map['DIEGO CARREOLA'] = lts
                elif 'APOLINAR' in ref.upper(): auth_map['APOLINAR'] = lts
                elif 'DAYANNE' in ref.upper(): auth_map['DAYANNE'] = lts
                elif 'EDGAR' in ref.upper(): auth_map['EDGAR'] = lts
                elif 'FRANCISCO' in ref.upper() or 'JAVIER' in ref.upper(): auth_map['FRANCISCO JAVIER'] = lts
                elif 'JACK' in ref.upper(): auth_map['JACK'] = lts
                elif 'LUIS' in ref.upper(): auth_map['LUIS'] = lts
                elif 'SAMUEL' in ref.upper(): auth_map['SAMUEL'] = lts

        # Fallback to standard auths if empty or missing
        for k, v in STD_AUTHS.items():
            if k not in auth_map:
                auth_map[k] = v

        q_obras = f'''
            SELECT 
                responsable,
                obra_destino,
                litros
            FROM diesel.consumos
            {cond_con}
        '''
        rows = db.execute(q_obras, tuple(params_con)).fetchall()
        db.close()

        resp_piv = {}
        for r in rows:
            raw_resp = (r['responsable'] or '').strip().upper()
            if not raw_resp or raw_resp == 'NAN':
                continue
            if 'CARREOLA' in raw_resp or 'DIEGO' in raw_resp: nr = 'DIEGO CARREOLA'
            elif 'APOLINAR' in raw_resp: nr = 'APOLINAR'
            elif 'DAYANNE' in raw_resp: nr = 'DAYANNE'
            elif 'EDGAR' in raw_resp: nr = 'EDGAR'
            elif 'FRANCISCO' in raw_resp or 'JAVIER' in raw_resp: nr = 'FRANCISCO JAVIER'
            elif 'JACK' in raw_resp: nr = 'JACK'
            elif 'LUIS' in raw_resp: nr = 'LUIS'
            elif 'SAMUEL' in raw_resp: nr = 'SAMUEL'
            else: nr = raw_resp

            obra = r['obra_destino'] or 'GENERAL / SIN OBRA'
            lts = float(r['litros'] or 0)

            if nr not in resp_piv:
                resp_piv[nr] = {'obras': set(), 'consumido': 0.0}
            resp_piv[nr]['obras'].add(obra)
            resp_piv[nr]['consumido'] += lts

        all_resps = sorted(set(list(STD_AUTHS.keys()) + list(resp_piv.keys())))

        result = []
        for resp in all_resps:
            data = resp_piv.get(resp, {'obras': set(), 'consumido': 0.0})
            auto_dia = auth_map.get(resp, STD_AUTHS.get(resp, 0.0))
            auto_semanal = auto_dia * 7.0
            
            obras_str = ', '.join(sorted(data['obras'])) if data['obras'] else 'SIN CONSUMOS'

            result.append({
                'responsable': resp,
                'obras': obras_str,
                'autorizado': auto_semanal,
                'consumido': round(data['consumido'], 2)
            })
            
        return jsonify(result)
    except Exception as e:
        print("ERROR API RESPONSABLES:", e)
        db.close()
        return jsonify([])

@app.route('/api/admin/resumen/diario-ingeniero')
def api_resumen_diario_ingeniero():
    """
    Returns daily consumption broken down by machine (equipo) for a specific
    engineer (responsable) and week.
    Response structure:
    {
        "responsable": "...",
        "semana": 28,
        "autorizado_dia": 400.0,
        "dias": ["2026-07-07", ...],  // dates in ISO format, sorted
        "obras_por_dia": {"2026-07-07": "México - Toluca", ...},
        "equipos": ["MAQUINA A", "MAQUINA B", ...],
        "consumos": {
            "MAQUINA A": {"2026-07-07": 150.0, ...},
            ...
        },
        "total_por_dia": {"2026-07-07": 350.0, ...},
        "total_por_equipo": {"MAQUINA A": 600.0, ...},
        "gran_total": 1500.0,
        "costo_unitario": 27.0,
        "costo_por_dia": {"2026-07-07": 9450.0, ...},
        "costo_total": 40500.0
    }
    """
    db = get_db()
    responsable = request.args.get('responsable', '')
    semana = request.args.get('semana', '')

    if not responsable or not semana:
        db.close()
        return jsonify({'error': 'Se requiere responsable y semana'}), 400

    try:
        semana_num = int(str(semana).replace('Semana ', '').strip())
    except:
        db.close()
        return jsonify({'error': 'Semana inválida'}), 400

    try:
        # Get authorization
        auth_row = db.execute(
            "SELECT litros_autorizados FROM catalogos.autorizaciones WHERE tipo='DIESEL' AND semana=%s AND referencia=%s",
            (semana_num, responsable)
        ).fetchone()
        autorizado_dia = float(auth_row['litros_autorizados'] or 0) if auth_row else 0.0

        # Get all consumos for this engineer/week
        rows = db.execute("""
            SELECT fecha::text as fecha_str,
                   obra_destino,
                   COALESCE(NULLIF(equipo, ''), 'SIN EQUIPO') as equipo,
                   SUM(litros) as litros,
                   AVG(costo_por_litro) as precio_unit
            FROM diesel.consumos
            WHERE semana = %s
              AND LOWER(responsable) = LOWER(%s)
              AND estatus_revision = 'APROBADO'
              AND (obra_destino IS NULL OR obra_destino NOT ILIKE '%%Tanque Pegaso%%')
            GROUP BY fecha::text, obra_destino, COALESCE(NULLIF(equipo, ''), 'SIN EQUIPO')
            ORDER BY fecha::text, equipo
        """, (str(semana_num), responsable)).fetchall()
        db.close()

        # Build day-wise structures
        dias_set = sorted(set(r['fecha_str'] for r in rows))
        equipos_set = []
        seen_eq = set()
        for r in rows:
            eq = r['equipo']
            if eq not in seen_eq:
                equipos_set.append(eq)
                seen_eq.add(eq)
        equipos_set.sort()

        # consumos[equipo][fecha] = litros
        consumos = {eq: {} for eq in equipos_set}
        obras_por_dia = {}
        precio_unit = 0.0

        for r in rows:
            eq = r['equipo']
            fecha = r['fecha_str']
            litros = float(r['litros'] or 0)
            consumos[eq][fecha] = consumos[eq].get(fecha, 0) + litros
            if fecha not in obras_por_dia:
                obras_por_dia[fecha] = r['obra_destino']
            if r['precio_unit']:
                precio_unit = float(r['precio_unit'])

        if precio_unit == 0:
            precio_unit = 27.0  # default

        total_por_dia = {}
        for fecha in dias_set:
            total_por_dia[fecha] = sum(consumos[eq].get(fecha, 0) for eq in equipos_set)

        total_por_equipo = {}
        for eq in equipos_set:
            total_por_equipo[eq] = sum(consumos[eq].values())

        gran_total = sum(total_por_dia.values())
        costo_por_dia = {f: round(total_por_dia[f] * precio_unit, 2) for f in dias_set}
        costo_total = round(gran_total * precio_unit, 2)

        return jsonify({
            'responsable': responsable,
            'semana': semana_num,
            'autorizado_dia': autorizado_dia,
            'dias': dias_set,
            'obras_por_dia': obras_por_dia,
            'equipos': equipos_set,
            'consumos': consumos,
            'total_por_dia': total_por_dia,
            'total_por_equipo': total_por_equipo,
            'gran_total': gran_total,
            'costo_unitario': precio_unit,
            'costo_por_dia': costo_por_dia,
            'costo_total': costo_total
        })

    except Exception as e:
        print("ERROR API DIARIO INGENIERO:", e)
        import traceback; traceback.print_exc()
        db.close()
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/resumen/pivot')
def api_resumen_pivot():
    db = get_db()
    modulo  = request.args.get('modulo', 'diesel')
    semana  = request.args.get('semana', 'TODOS')

    if modulo != 'diesel':
        db.close()
        return jsonify([])

    cond_con = "WHERE estatus_revision = 'APROBADO' AND (obra_destino IS NULL OR obra_destino NOT ILIKE %s)"
    params_con = ['%Tanque Pegaso%']
    semana_num = None

    if semana != 'TODOS':
        semana_limpia = str(semana).replace('Semana ', '').strip()
        cond_con += " AND semana = %s"
        params_con.append(semana_limpia)
        try:
            semana_num = int(semana_limpia)
        except:
            pass

    auth_map = {}
    if semana_num:
        try:
            auth_rows = db.execute(
                "SELECT referencia, litros_autorizados FROM catalogos.autorizaciones WHERE tipo='DIESEL' AND semana=%s",
                (semana_num,)
            ).fetchall()
            for ar in auth_rows:
                auth_map[ar['referencia']] = float(ar['litros_autorizados'] or 0)
        except:
            pass

    try:
        q_diario = f'''
            SELECT fecha::text as fecha_str,
                obra_destino,
                COALESCE(NULLIF(NULLIF(responsable,'nan'),''),'S/R') as resp,
                SUM(litros) as consumido
            FROM diesel.consumos
            {cond_con}
            GROUP BY fecha::text, obra_destino, COALESCE(NULLIF(NULLIF(responsable,'nan'),''),'S/R')
        '''
        rows = db.execute(q_diario, tuple(params_con)).fetchall()
        db.close()

        result = {
            'auth_map': auth_map,
            'datos': []
        }
        for r in rows:
            result['datos'].append({
                'fecha': r['fecha_str'],
                'obra': r['obra_destino'] or 'Sin Obra',
                'resp': r['resp'],
                'consumido': float(r['consumido'] or 0)
            })

        return jsonify(result)
    except Exception as e:
        print("ERROR API PIVOT:", e)
        db.close()
        return jsonify([])

def recalcular_saldos_jalisco(db):
    try:
        rows = db.execute("SELECT id, tipo_movimiento, litros FROM diesel.jalisco_movimientos ORDER BY fecha ASC, id ASC").fetchall()
        running = 0.0
        for r in rows:
            t = r['tipo_movimiento']
            lts = float(r['litros'] or 0)
            if t == 'ENTRADA':
                running += lts
            elif t == 'SALIDA':
                running -= lts
            elif t == 'AJUSTE':
                running += lts
            db.execute("UPDATE diesel.jalisco_movimientos SET saldo_teorico = %s WHERE id = %s", (running, r['id']))
    except Exception as e:
        print("Error recalculando saldos jalisco:", e)

@app.route('/admin/jalisco')
def admin_jalisco():
    try:
        db = get_db()
        equipos = db.execute("SELECT numero_economico, descripcion FROM catalogos.equipos ORDER BY numero_economico").fetchall()
        db.close()
        return render_template('admin_jalisco.html', equipos=[dict(e) for e in equipos])
    except Exception as e:
        return render_template('admin_jalisco.html', equipos=[])

@app.route('/api/admin/jalisco/movimiento/editar', methods=['POST'])
def api_admin_jalisco_movimiento_editar():
    try:
        mov_id = int(request.form.get('id'))
        fecha = request.form.get('fecha')
        eq_val = request.form.get('equipo', '')
        litros = float(request.form.get('litros', 0))
        obs = request.form.get('observaciones', '')

        eq_eco = ''
        eq_desc = ''
        if '|' in eq_val:
            parts = eq_val.split('|')
            eq_eco = parts[0]
            eq_desc = parts[1]
        elif eq_val:
            eq_desc = eq_val

        # Calcular semana según la fecha
        import datetime
        semana = datetime.date.today().isocalendar()[1]
        if fecha:
            try:
                dt_obj = datetime.datetime.strptime(fecha, '%Y-%m-%d')
                semana = dt_obj.isocalendar()[1]
            except:
                pass

        db = get_db()
        
        # Consultar tipo movimiento
        r_mov = db.execute("SELECT tipo_movimiento FROM diesel.jalisco_movimientos WHERE id = %s", (mov_id,)).fetchone()
        tipo_mov = r_mov['tipo_movimiento'] if r_mov else 'SALIDA'
        
        is_gasolina = 'GASOLINA' in (str(eq_eco) + ' ' + str(eq_desc) + ' ' + str(obs)).upper()
        costo_unitario = 23.97 if is_gasolina else 27.00
        importe_total = (litros * costo_unitario) if tipo_mov == 'SALIDA' else 0.0

        foto = request.files.get('foto_evidencia')
        pdf = request.files.get('archivo_pdf')

        foto_blob = foto.read() if foto and foto.filename else None
        pdf_blob = pdf.read() if pdf and pdf.filename else None

        if foto_blob and pdf_blob:
            db.execute("""
                UPDATE diesel.jalisco_movimientos 
                SET fecha=%s, semana=%s, equipo_economico=%s, equipo=%s, litros=%s, 
                    costo_por_litro=%s, importe_total=%s, observaciones=%s, foto_evidencia=%s, archivo_pdf=%s
                WHERE id=%s
            """, (fecha, semana, eq_eco, eq_desc, litros, costo_unitario, importe_total, obs, psycopg2.Binary(foto_blob), psycopg2.Binary(pdf_blob), mov_id))
        elif foto_blob:
            db.execute("""
                UPDATE diesel.jalisco_movimientos 
                SET fecha=%s, semana=%s, equipo_economico=%s, equipo=%s, litros=%s, 
                    costo_por_litro=%s, importe_total=%s, observaciones=%s, foto_evidencia=%s
                WHERE id=%s
            """, (fecha, semana, eq_eco, eq_desc, litros, costo_unitario, importe_total, obs, psycopg2.Binary(foto_blob), mov_id))
        elif pdf_blob:
            db.execute("""
                UPDATE diesel.jalisco_movimientos 
                SET fecha=%s, semana=%s, equipo_economico=%s, equipo=%s, litros=%s, 
                    costo_por_litro=%s, importe_total=%s, observaciones=%s, archivo_pdf=%s
                WHERE id=%s
            """, (fecha, semana, eq_eco, eq_desc, litros, costo_unitario, importe_total, obs, psycopg2.Binary(pdf_blob), mov_id))
        else:
            db.execute("""
                UPDATE diesel.jalisco_movimientos 
                SET fecha=%s, semana=%s, equipo_economico=%s, equipo=%s, litros=%s, 
                    costo_por_litro=%s, importe_total=%s, observaciones=%s
                WHERE id=%s
            """, (fecha, semana, eq_eco, eq_desc, litros, costo_unitario, importe_total, obs, mov_id))

        recalcular_saldos_jalisco(db)
        db.close()
        return jsonify({'success': True})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/admin/jalisco/movimiento/eliminar', methods=['POST'])
def api_admin_jalisco_movimiento_eliminar():
    try:
        data = request.json or {}
        mov_id = int(data.get('id', 0) or request.form.get('id', 0))
        if not mov_id:
            return jsonify({'success': False, 'error': 'ID inválido'})

        db = get_db()
        db.execute("DELETE FROM diesel.jalisco_movimientos WHERE id = %s", (mov_id,))
        recalcular_saldos_jalisco(db)
        db.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/admin/jalisco/movimientos')
def api_admin_jalisco_movimientos():
    try:
        db = get_db()
        movs = db.execute("""
            SELECT id, fecha::text, semana, tipo_movimiento, equipo, equipo_economico, 
                   litros::float, 
                   COALESCE(costo_por_litro::float, 
                     CASE 
                       WHEN tipo_movimiento = 'SALIDA' AND (LOWER(COALESCE(equipo_economico,'')) LIKE '%%gasolina%%' OR LOWER(COALESCE(equipo,'')) LIKE '%%gasolina%%' OR LOWER(COALESCE(observaciones,'')) LIKE '%%gasolina%%') THEN 23.97 
                       WHEN tipo_movimiento = 'SALIDA' THEN 27.0 
                       ELSE NULL 
                     END) as costo_por_litro, 
                   COALESCE(importe_total::float, 
                     CASE 
                       WHEN tipo_movimiento = 'SALIDA' AND (LOWER(COALESCE(equipo_economico,'')) LIKE '%%gasolina%%' OR LOWER(COALESCE(equipo,'')) LIKE '%%gasolina%%' OR LOWER(COALESCE(observaciones,'')) LIKE '%%gasolina%%') THEN (litros::float * 23.97) 
                       WHEN tipo_movimiento = 'SALIDA' THEN (litros::float * 27.0) 
                       ELSE NULL 
                     END) as importe_total, 
                   saldo_teorico::float, observaciones,
                   (foto_evidencia IS NOT NULL) as has_foto,
                   (archivo_pdf IS NOT NULL) as has_pdf
            FROM diesel.jalisco_movimientos 
            ORDER BY id DESC
        """).fetchall()
        db.close()
        return jsonify({'success': True, 'movimientos': [dict(m) for m in movs]})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/admin/jalisco/evidencia/<int:mov_id>')
def api_admin_jalisco_evidencia(mov_id):
    tipo = request.args.get('tipo', 'foto')
    db = get_db()
    if tipo == 'pdf':
        row = db.execute("SELECT archivo_pdf FROM diesel.jalisco_movimientos WHERE id=%s", (mov_id,)).fetchone()
        db.close()
        if row and row['archivo_pdf']:
            import io
            return send_file(io.BytesIO(row['archivo_pdf']), mimetype='application/pdf')
    else:
        row = db.execute("SELECT foto_evidencia FROM diesel.jalisco_movimientos WHERE id=%s", (mov_id,)).fetchone()
        db.close()
        if row and row['foto_evidencia']:
            import io
            return send_file(io.BytesIO(row['foto_evidencia']), mimetype='image/jpeg')
    return "No disponible", 404

@app.route('/api/admin/jalisco/ajuste', methods=['POST'])
def api_admin_jalisco_ajuste():
    try:
        saldo_fisico = float(request.form.get('saldo_fisico', 0))
        obs = request.form.get('observaciones', 'Ajuste de inventario')
        
        import datetime
        fecha = datetime.date.today().strftime('%Y-%m-%d')
        # Utilizamos la semana calculada del sistema
        db = get_db()
        
        row = db.execute("SELECT num_semana FROM catalogos.semanas WHERE current_date BETWEEN fecha_inicio AND fecha_fin LIMIT 1").fetchone()
        semana = row['num_semana'] if row else int(datetime.date.today().strftime('%V'))
        
        last = db.execute("SELECT saldo_teorico FROM diesel.jalisco_movimientos ORDER BY id DESC LIMIT 1").fetchone()
        saldo_actual = float(last['saldo_teorico']) if last else 0.0
        
        diferencia = saldo_fisico - saldo_actual
        if diferencia == 0:
            db.close()
            return jsonify({'success': False, 'error': 'El saldo físico es igual al teórico. No hay ajuste necesario.'})
            
        db.execute("""
            INSERT INTO diesel.jalisco_movimientos 
            (fecha, semana, tipo_movimiento, litros, saldo_teorico, observaciones)
            VALUES (%s, %s, 'AJUSTE', %s, %s, %s)
        """, (fecha, semana, diferencia, saldo_fisico, obs))
        
        db.commit()
        db.close()
        return jsonify({'success': True, 'diferencia': diferencia})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})



@app.route('/admin/jalisco/subir')
def admin_jalisco_subir():
    return render_template('admin/admin_jalisco_subir.html')

@app.route('/api/admin/jalisco/preview_pdf', methods=['POST'])
def api_admin_jalisco_preview_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    try:
        import os
        import tempfile
        import base64
        from servidor.parser_jalisco import extraer_pdf_jalisco
        
        fd, temp_path = tempfile.mkstemp(suffix='.pdf')
        os.close(fd)
        file.save(temp_path)
        
        # Guardar en bytes para la base de datos (luego se lo pasamos al frontend o lo cacheamos, pero como no podemos mantener estado fcilmente, devolveremos base64 o le pediremos que vuelva a subir)
        # Una mejor forma es devolver un resumen, y cuando confirme, vuelve a enviar el archivo o el JSON
        
        datos = extraer_pdf_jalisco(temp_path)
        os.remove(temp_path)
        
        return jsonify({'success': True, 'data': datos})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/jalisco/confirm_upload', methods=['POST'])
def api_admin_jalisco_confirm_upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    try:
        import os
        import tempfile
        from servidor.parser_jalisco import extraer_pdf_jalisco
        
        fd, temp_path = tempfile.mkstemp(suffix='.pdf')
        os.close(fd)
        file.save(temp_path)
        
        with open(temp_path, 'rb') as f_pdf:
            pdf_bytes = f_pdf.read()
            
        datos = extraer_pdf_jalisco(temp_path)
        os.remove(temp_path)
        
        semana = datos.get('semana', 0)
        
        db = get_db()
        inserted = 0
        
        for c in datos['consumos']:
            fecha = c['fecha']
            equipo = c['equipo']
            litros = c['litros']
            costo = c['costo_por_litro']
            tipo = c['tipo_combustible']
            importe = litros * costo
            
            # Ver si ya existe para evitar duplicados
            exist = db.execute("SELECT id FROM diesel.jalisco_movimientos WHERE fecha=%s AND equipo=%s AND litros=%s AND tipo_movimiento='SALIDA'", (fecha, equipo, litros)).fetchone()
            if exist: continue
            
            # Obtener saldo_teorico anterior del mismo tipo de combustible
            last = db.execute("SELECT saldo_teorico FROM diesel.jalisco_movimientos WHERE tipo_combustible=%s ORDER BY id DESC LIMIT 1", (tipo,)).fetchone()
            saldo_anterior = float(last['saldo_teorico']) if last and last['saldo_teorico'] is not None else 0.0
            nuevo_saldo = saldo_anterior - litros
            
            db.execute('''
                INSERT INTO diesel.jalisco_movimientos 
                (fecha, semana, tipo_movimiento, equipo, litros, costo_por_litro, importe_total, saldo_teorico, tipo_combustible, archivo_pdf)
                VALUES (%s, %s, 'SALIDA', %s, %s, %s, %s, %s, %s, %s)
            ''', (fecha, semana, equipo, litros, costo, importe, nuevo_saldo, tipo, pdf_bytes))
            
            inserted += 1
            
        db.connection.commit()
        db.close()
        
        return jsonify({'success': True, 'message': f'Migración exitosa. Se guardaron {inserted} consumos nuevos.'})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# ─────────────────────────────────────────
# APIS PARA AUTOMATIZACIÓN CON n8n
# ─────────────────────────────────────────
@app.route('/api/n8n/conciliar_automatico', methods=['POST'])
def api_n8n_conciliar_automatico():
    """
    Endpoint invocado por workflows de n8n para conciliar automáticamente 
    consumos en campo contra facturas recibidas (XML/PDF).
    """
    try:
        data = request.json or {}
        modulo = data.get('modulo', 'diesel').lower()
        semana = str(data.get('semana', '')).replace('Semana ', '').strip()
        
        db = get_db()
        aprobados_auto = 0
        discrepancias = 0
        
        if modulo == 'gasolina':
            consumos = db.execute("SELECT id, obra_destino, vehiculo, litros, importe_total, estatus_revision FROM gasolina.consumos WHERE semana=%s AND estatus_revision='PENDIENTE'", (semana,)).fetchall()
            facturas = db.execute("SELECT id, uuid_cfdi, litros_facturados, importe_total FROM gasolina.facturas WHERE semana=%s", (semana,)).fetchall()
            
            for c in consumos:
                match = None
                for f in facturas:
                    if abs(float(c['litros']) - float(f['litros_facturados'])) < 0.01:
                        match = f
                        break
                if match:
                    db.execute("UPDATE gasolina.consumos SET estatus_revision='APROBADO' WHERE id=%s", (c['id'],))
                    aprobados_auto += 1
                else:
                    discrepancias += 1
        else:
            consumos = db.execute("SELECT id, obra_destino, litros, importe_total, estatus_revision FROM diesel.consumos WHERE semana=%s AND estatus_revision='PENDIENTE'", (semana,)).fetchall()
            facturas = db.execute("SELECT id, uuid_cfdi, litros_facturados, importe_total FROM diesel.facturas WHERE semana=%s", (semana,)).fetchall()
            
            for c in consumos:
                match = None
                for f in facturas:
                    if abs(float(c['litros']) - float(f['litros_facturados'])) < 0.01:
                        match = f
                        break
                if match:
                    db.execute("UPDATE diesel.consumos SET estatus_revision='APROBADO' WHERE id=%s", (c['id'],))
                    aprobados_auto += 1
                else:
                    discrepancias += 1
                    
        db.commit()
        db.close()
        return jsonify({
            'success': True,
            'modulo': modulo,
            'semana': semana,
            'aprobados_automaticos': aprobados_auto,
            'discrepancias_pendientes': discrepancias
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/n8n/resumen_semanal')
def api_n8n_resumen_semanal():
    """
    Endpoint invocado por n8n para obtener el resumen ejecutivo 
    y distribuirlo por Telegram / Email / WhatsApp o al Portal Directivos.
    """
    semana = request.args.get('semana', '26')
    try:
        db = get_db()
        semana_str = str(semana).replace('Semana ', '').strip()
        
        cur_diesel = db.execute("""
            SELECT SUM(litros) as total_litros, SUM(importe_total) as total_importe 
            FROM diesel.consumos WHERE semana=%s AND estatus_revision != 'RECHAZADO'
        """, (semana_str,)).fetchone()
        
        cur_gas = db.execute("""
            SELECT SUM(litros) as total_litros, SUM(importe_total) as total_importe 
            FROM gasolina.consumos WHERE semana=%s AND estatus_revision != 'RECHAZADO'
        """, (semana_str,)).fetchone()
        
        extras_gas = db.execute("""
            SELECT COUNT(*) as cnt FROM gasolina.consumos 
            WHERE semana=%s AND observaciones ILIKE '%%CARGA EXTRAORDINARIA%%'
        """, (semana_str,)).fetchone()
        
        db.close()
        return jsonify({
            'success': True,
            'semana': semana_str,
            'diesel': {
                'litros': float(cur_diesel['total_litros'] or 0) if cur_diesel else 0.0,
                'importe': float(cur_diesel['total_importe'] or 0) if cur_diesel else 0.0
            },
            'gasolina': {
                'litros': float(cur_gas['total_litros'] or 0) if cur_gas else 0.0,
                'importe': float(cur_gas['total_importe'] or 0) if cur_gas else 0.0,
                'cargas_extraordinarias': extras_gas['cnt'] if extras_gas else 0
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ─────────────────────────────────────────
# MÓDULO DE TAGS Y TELEPEAJE
# ─────────────────────────────────────────
@app.route('/admin/tags')
def admin_tags():
    return render_template('admin_tags.html')

@app.route('/api/admin/tags/movimientos')
def api_admin_tags_movimientos():
    semana = request.args.get('semana', '')
    obra = request.args.get('obra', '')
    empresa = request.args.get('empresa', '')
    busqueda = request.args.get('busqueda', '')
    
    db = get_db()
    
    query = "SELECT id, empresa, mes, semana, tag, no_economico, responsable, tipo_unidad, placas, obra_asignada, TO_CHAR(fecha, 'YYYY-MM-DD') as fecha_fmt, TO_CHAR(hora, 'HH24:MI:SS') as hora_fmt, caseta, importe, saldo FROM tags.movimientos WHERE 1=1"
    params = []
    
    if semana and semana != 'TODOS':
        query += " AND semana = %s"
        params.append(semana)
    if obra and obra != 'TODAS':
        query += " AND obra_asignada = %s"
        params.append(obra)
    if empresa and empresa != 'TODAS':
        query += " AND empresa = %s"
        params.append(empresa)
    if busqueda:
        query += " AND (tag ILIKE %s OR no_economico ILIKE %s OR responsable ILIKE %s OR caseta ILIKE %s)"
        b = f"%{busqueda}%"
        params.extend([b, b, b, b])
        
    query_kpi = "SELECT COUNT(*), COALESCE(SUM(importe), 0), COUNT(DISTINCT obra_asignada), COUNT(DISTINCT tag) FROM tags.movimientos WHERE 1=1"
    query_kpi += query.replace("SELECT id, empresa, mes, semana, tag, no_economico, responsable, tipo_unidad, placas, obra_asignada, TO_CHAR(fecha, 'YYYY-MM-DD') as fecha_fmt, TO_CHAR(hora, 'HH24:MI:SS') as hora_fmt, caseta, importe, saldo FROM tags.movimientos WHERE 1=1", "")
    
    kpi_row = db.execute(query_kpi, params).fetchone()
    
    query += " ORDER BY fecha DESC, hora DESC LIMIT 1000"
    movs = [dict(r) for r in db.execute(query, params).fetchall()]
    
    semanas = [r[0] for r in db.execute("SELECT DISTINCT semana FROM tags.movimientos WHERE semana IS NOT NULL AND semana != '' ORDER BY semana").fetchall()]
    obras = [r[0] for r in db.execute("SELECT DISTINCT obra_asignada FROM tags.movimientos WHERE obra_asignada IS NOT NULL AND obra_asignada != '' ORDER BY obra_asignada").fetchall()]
    
    db.close()
    
    return jsonify({
        'movimientos': movs,
        'kpis': {
            'total_pasadas': kpi_row[0] if kpi_row else 0,
            'total_importe': float(kpi_row[1] or 0) if kpi_row else 0.0,
            'total_obras': kpi_row[2] if kpi_row else 0,
            'total_tags': kpi_row[3] if kpi_row else 0
        },
        'semanas': semanas,
        'obras': obras
    })

@app.route('/api/admin/tags/resumen_obras')
def api_admin_tags_resumen_obras():
    semana = request.args.get('semana', '')
    db = get_db()
    
    query = """
        SELECT obra_asignada, 
               COUNT(*) as total_pasadas, 
               COALESCE(SUM(importe), 0) as total_importe,
               COUNT(DISTINCT tag) as total_tags,
               COUNT(DISTINCT responsable) as total_responsables
        FROM tags.movimientos
    """
    params = []
    if semana and semana != 'TODAS' and semana != 'TODOS':
        query += " WHERE semana = %s"
        params.append(semana)
        
    query += " GROUP BY obra_asignada ORDER BY SUM(importe) ASC"
    
    resumen = [dict(r) for r in db.execute(query, params).fetchall()]
    semanas = [r[0] for r in db.execute("SELECT DISTINCT semana FROM tags.movimientos WHERE semana IS NOT NULL AND semana != '' ORDER BY semana").fetchall()]
    
    db.close()
    return jsonify({'resumen_obras': resumen, 'semanas': semanas})

@app.route('/api/admin/tags/catalogo')
def api_admin_tags_catalogo():
    import openpyxl
    cat_file = r'c:\Users\JOSE\Desktop\Proyecto fenix\TAGS\CONTROL TAG.xlsx'
    data = []
    if os.path.exists(cat_file):
        wb = openpyxl.load_workbook(cat_file, read_only=True)
        ws = wb.active
        for r in range(2, ws.max_row + 1):
            t = ws.cell(r, 1).value
            resp = ws.cell(r, 2).value
            tipo = ws.cell(r, 3).value
            placa = ws.cell(r, 4).value
            obra = ws.cell(r, 5).value
            if t:
                data.append({
                    'tag': str(t).strip(),
                    'responsable': str(resp or '').strip(),
                    'tipo_unidad': str(tipo or '').strip(),
                    'placas': str(placa or '').strip(),
                    'obra': str(obra or '').strip()
                })
    return jsonify(data)

# ==============================================================================
# CAPTURA MASIVA Y CONCILIACIÓN DE GASOLINA DESDE EXCEL (LEVET / GASOLINERÍAS)
# ==============================================================================
def parse_gasolina_excel_data(file_stream_or_path, db):
    import openpyxl, datetime
    wb = openpyxl.load_workbook(file_stream_or_path, data_only=True)
    all_rows = []
    semanas_set = set()
    
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
            placa_val = ws.cell(r, hdr_map.get('placa', 4)).value
            conductor_val = ws.cell(r, hdr_map.get('conductor', 6)).value
            obra_val = ws.cell(r, hdr_map.get('obra', 7)).value
            litros_val = ws.cell(r, hdr_map.get('litros', 8)).value
            precio_val = ws.cell(r, hdr_map.get('precio', 9)).value
            importe_val = ws.cell(r, hdr_map.get('importe', 10)).value
            
            if not ticket_val or not fecha_val:
                continue
                
            ticket_str = str(ticket_val).strip()
            if not ticket_str or ticket_str.upper() in ('TICKET', 'TOTAL', 'TOTALES', 'NONE', 'NAN'):
                continue
                
            dt_obj = None
            if isinstance(fecha_val, (datetime.datetime, datetime.date)):
                dt_obj = fecha_val
                fecha_str = fecha_val.strftime('%Y-%m-%d')
            else:
                fecha_str = str(fecha_val)[:10].strip()
                try:
                    dt_obj = datetime.datetime.strptime(fecha_str, '%Y-%m-%d')
                except:
                    dt_obj = None
                    
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
            
            # Check DB match
            match = None
            if db:
                match = db.execute("""
                    SELECT id, conductor, vehiculo, litros, importe_total, fecha, obra_destino, folio_conciliacion
                    FROM gasolina.consumos
                    WHERE (folio_conciliacion ILIKE %s 
                       OR observaciones ILIKE %s 
                       OR (fecha = %s AND (placa ILIKE %s OR vehiculo ILIKE %s)))
                    LIMIT 1
                """, (f"%{ticket_str}%", f"%{ticket_str}%", fecha_str, f"%{placa}%", f"%{placa}%")).fetchone()
                
            estatus = 'DUPLICADO' if match else 'NUEVO'
            
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
                'id_match_bd': match['id'] if match else None,
                'match_info': f"ID BD: {match['id']} ({match['fecha']} - {match['conductor']} - {match['litros']}L)" if match else None
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
        inserted_count = 0
        
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
            
            db.execute("""
                INSERT INTO gasolina.consumos (
                    fecha, semana, conductor, vehiculo, placa, obra_destino,
                    litros, costo_por_litro, importe_total, gasolineria,
                    folio_conciliacion, estatus_revision, origen, observaciones
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'LEVET', %s, 'APROBADO', 'CAPTURA_MASIVA_EXCEL', %s)
            """, (
                fecha, semana, conductor, vehiculo_label, placa, obra,
                litros, precio, importe, ticket,
                f"Captura Masiva Excel Levet Ticket #{ticket}"
            ))
            inserted_count += 1
            
        db.commit()
        db.close()
        
        return jsonify({
            'success': True,
            'message': f"¡Se guardaron exitosamente {inserted_count} cargas en la base de datos de Gasolina!",
            'inserted_count': inserted_count
        })
    except Exception as e:
        print("ERROR EN GUARDAR CAPTURA MASIVA GASOLINA:", e)
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    import threading
    import webbrowser
    print("==================================================")
    print("  CENTRO DE MANDO FENIX (ADMIN)")
    print("  http://127.0.0.1:5002")
    print("==================================================")
    threading.Timer(1.2, lambda: webbrowser.open("http://127.0.0.1:5002")).start()
    app.run(host='0.0.0.0', port=5002, debug=True)
