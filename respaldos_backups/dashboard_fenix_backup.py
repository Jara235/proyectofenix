# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import sqlite3, os, webbrowser, threading
from flask import Flask, render_template, jsonify, request, send_file
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "fenix.db")
TMPL_DIR = os.path.join(BASE_DIR, "servidor", "templates")
STAT_DIR = os.path.join(BASE_DIR, "servidor", "static")

app = Flask(__name__, template_folder=TMPL_DIR, static_folder=STAT_DIR)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def semana_param():
    s = request.args.get('semana', '')
    return s if s and s != 'todas' else None

# ─────────────────────────────────────────────────
#  UTILS
# ─────────────────────────────────────────────────
def q_filter(sql, col, sem, has_where=True):
    if not sem: return sql, []
    op = "AND" if has_where else "WHERE"
    return f"{sql} {op} {col} = ?", [sem]

# ─────────────────────────────────────────────────
#  SEMANAS DISPONIBLES
# ─────────────────────────────────────────────────
@app.route("/api/semanas_disponibles")
def api_semanas():
    db = get_db(); cur = db.cursor()
    cur.execute("SELECT DISTINCT semana FROM fenix_movimientos_combustible WHERE semana IS NOT NULL ORDER BY semana DESC")
    semanas = [r[0] for r in cur.fetchall()]
    db.close()
    return jsonify(semanas)

# ─────────────────────────────────────────────────
#  KPIs GENERALES
# ─────────────────────────────────────────────────
@app.route("/api/kpis")
def api_kpis():
    db = get_db(); cur = db.cursor()
    sem = semana_param()

    def count_q(base, col): return q_filter(base, col, sem)
    def count_qf(base, col): return q_filter(base, col, sem, False)

    sql, p = count_q("SELECT COALESCE(SUM(litros),0) FROM fenix_movimientos_combustible WHERE tipo_movimiento='CONSUMO' AND tipo_combustible='Diesel'", "semana")
    cur.execute(sql, p); litros_diesel = round(cur.fetchone()[0], 1)

    sql, p = count_q("SELECT COALESCE(SUM(litros),0) FROM fenix_movimientos_combustible WHERE tipo_movimiento='CONSUMO' AND tipo_combustible='Gasolina'", "semana")
    cur.execute(sql, p); litros_gasolina = round(cur.fetchone()[0], 1)

    sql, p = count_qf("SELECT COALESCE(SUM(total),0) FROM fenix_viajes_acarreo", "semana")
    cur.execute(sql, p); total_acarreos = round(cur.fetchone()[0], 2)

    sql, p = count_qf("SELECT COUNT(*) FROM fenix_viajes_acarreo", "semana")
    cur.execute(sql, p); total_viajes = cur.fetchone()[0]

    cur.execute("SELECT COUNT(DISTINCT numero_economico) FROM fenix_equipos WHERE activo=1")
    total_equipos = cur.fetchone()[0]

    sql, p = count_q("SELECT COUNT(*) FROM v_rendimiento_maquinaria WHERE semaforo LIKE 'ROJO%' AND litros_consumidos > 0", "semana_num")
    cur.execute(sql, p); alertas_rojas = cur.fetchone()[0]

    sql, p = count_q("SELECT COUNT(*) FROM v_rendimiento_maquinaria WHERE semaforo LIKE 'AMARILLO%' AND litros_consumidos > 0", "semana_num")
    cur.execute(sql, p); alertas_amarillas = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM fenix_facturas_documentos WHERE estatus_validacion='PENDIENTE'")
    facturas_pendientes = cur.fetchone()[0]

    db.close()
    return jsonify({
        "litros_diesel":       litros_diesel,
        "litros_gasolina":     litros_gasolina,
        "total_litros":        round(litros_diesel + litros_gasolina, 1),
        "total_acarreos":      total_acarreos,
        "total_viajes":        total_viajes,
        "total_equipos":       total_equipos,
        "alertas_rojas":       alertas_rojas,
        "alertas_amarillas":   alertas_amarillas,
        "facturas_pendientes": facturas_pendientes,
        "generado":            datetime.now().strftime("%d/%m/%Y %H:%M")
    })

# ─────────────────────────────────────────────────
#  DIESEL
# ─────────────────────────────────────────────────
@app.route("/api/diesel/consumo_por_obra")
def api_diesel_obras():
    db = get_db(); cur = db.cursor()
    sem = semana_param()
    sql = """SELECT COALESCE(o.nombre,'Sin asignar') AS obra,
                    ROUND(SUM(m.litros),1) AS litros, COUNT(*) AS registros
             FROM fenix_movimientos_combustible m
             LEFT JOIN fenix_obras o ON o.id = m.obra_id
             WHERE m.tipo_movimiento='CONSUMO' AND m.tipo_combustible='Diesel'"""
    sql, p = q_filter(sql, "m.semana", sem)
    cur.execute(sql + " GROUP BY m.obra_id ORDER BY litros DESC", p)
    rows = [dict(r) for r in cur.fetchall()]
    db.close(); return jsonify(rows)

@app.route("/api/diesel/tendencia")
def api_diesel_tendencia():
    db = get_db(); cur = db.cursor()
    cur.execute("""SELECT semana, ROUND(SUM(litros),1) AS litros
                   FROM fenix_movimientos_combustible
                   WHERE tipo_movimiento='CONSUMO' AND tipo_combustible='Diesel' AND semana IS NOT NULL
                   GROUP BY semana ORDER BY semana""")
    rows = [dict(r) for r in cur.fetchall()]
    db.close(); return jsonify(rows)

@app.route("/api/diesel/facturas")
def api_diesel_facturas():
    db = get_db(); cur = db.cursor()
    cur.execute("""
        SELECT id, folio, fecha_emision, emisor_nombre,
               ROUND(litros_totales,1) as litros, total, estatus_validacion,
               COALESCE(destino_suministro,'—') as destino_suministro,
               COALESCE(nota_leyenda,'') as nota_leyenda,
               COALESCE(confianza_clasif,'?') as confianza_clasif,
               (archivo_pdf IS NOT NULL) as tiene_pdf
        FROM fenix_facturas_documentos
        WHERE tipo_combustible='Diesel'
        ORDER BY fecha_emision DESC""")
    rows = [dict(r) for r in cur.fetchall()]

    cur.execute("""
        SELECT
          COUNT(*) as total_facturas,
          SUM(CASE WHEN estatus_validacion='VALIDADA'  THEN 1 ELSE 0 END) as validadas,
          SUM(CASE WHEN estatus_validacion='RECHAZADA' THEN 1 ELSE 0 END) as rechazadas,
          SUM(CASE WHEN estatus_validacion='PENDIENTE' THEN 1 ELSE 0 END) as pendientes,
          ROUND(SUM(CASE WHEN estatus_validacion='VALIDADA' THEN litros_totales ELSE 0 END),1) as litros_validados,
          ROUND(SUM(CASE WHEN estatus_validacion='VALIDADA' THEN total           ELSE 0 END),2) as monto_validado
        FROM fenix_facturas_documentos WHERE tipo_combustible='Diesel'""")
    kpi = dict(cur.fetchone())
    db.close()
    return jsonify({"facturas": rows, "kpi": kpi})

# ─────────────────────────────────────────────────
#  GASOLINA (Modelo Matriz)
# ─────────────────────────────────────────────────
@app.route("/api/gasolina/kpis")
def api_gasolina_kpis():
    db = get_db(); cur = db.cursor()
    sem = semana_param()
    
    # Presupuesto Autorizado Total
    sql_aut = "SELECT ROUND(SUM(monto_autorizado),2) as importe_aut FROM fenix_gas_presupuestos"
    sql_aut, p_aut = q_filter(sql_aut, "semana", sem, False)
    cur.execute(sql_aut, p_aut)
    aut = dict(cur.fetchone())
    
    # Consumo Reportado (Matriz Excel)
    sql_rep = "SELECT ROUND(SUM(monto_reportado),2) as importe_rep FROM fenix_gas_reportes_diarios r JOIN fenix_gas_presupuestos p ON r.presupuesto_id = p.id"
    sql_rep, p_rep = q_filter(sql_rep, "p.semana", sem, False)
    cur.execute(sql_rep, p_rep)
    rep = dict(cur.fetchone())
    
    # Consumo Real (Tickets Gasolinera)
    sql_real = "SELECT ROUND(SUM(litros),1) as lts_real, ROUND(SUM(importe),2) as importe_real FROM fenix_gas_tickets_reales"
    sql_real, p_real = q_filter(sql_real, "semana", sem, False)
    cur.execute(sql_real, p_real)
    real = dict(cur.fetchone())
    
    db.close()
    return jsonify({
        "importe_autorizado": aut["importe_aut"] or 0,
        "importe_reportado": rep["importe_rep"] or 0,
        "litros_real": real["lts_real"] or 0,
        "importe_real": real["importe_real"] or 0
    })

@app.route("/api/gasolina/matriz")
def api_gasolina_matriz():
    db = get_db(); cur = db.cursor()
    sem = semana_param()
    
    # Traer todos los presupuestos
    sql_p = "SELECT id, responsable, obra, unidad, placa, ROUND(monto_autorizado,2) as autorizado FROM fenix_gas_presupuestos"
    sql_p, p_p = q_filter(sql_p, "semana", sem, False)
    cur.execute(sql_p, p_p)
    presupuestos = [dict(r) for r in cur.fetchall()]
    
    # Traer todos los reportes diarios
    sql_r = "SELECT r.presupuesto_id, r.fecha, r.proveedor, ROUND(r.monto_reportado,2) as monto FROM fenix_gas_reportes_diarios r JOIN fenix_gas_presupuestos p ON p.id = r.presupuesto_id"
    sql_r, p_r = q_filter(sql_r, "p.semana", sem, False)
    cur.execute(sql_r + " ORDER BY r.fecha", p_r)
    reportes = [dict(r) for r in cur.fetchall()]
    
    # Agrupar reportes en presupuestos
    # Estructura: presupuesto -> fecha -> proveedor -> monto
    from collections import defaultdict
    fechas_unicas = set()
    for p in presupuestos:
        p["dias"] = defaultdict(lambda: {"LEVET": 0, "MOBILE": 0, "SIVALE": 0})
    
    # Crear un diccionario para busqueda rápida
    p_dict = {p["id"]: p for p in presupuestos}
    
    for r in reportes:
        pid = r["presupuesto_id"]
        fecha = r["fecha"]
        prov = r["proveedor"]
        fechas_unicas.add(fecha)
        if pid in p_dict:
            p_dict[pid]["dias"][fecha][prov] += r["monto"]
            
    # Formatear la matriz
    fechas_ordenadas = sorted(list(fechas_unicas))
    
    # Agrupar por responsable
    matriz_final = []
    
    # Sort presupuestos by responsable
    presupuestos.sort(key=lambda x: str(x["responsable"]))
    
    for p in presupuestos:
        dias_list = []
        for f in fechas_ordenadas:
            dias_list.append({
                "fecha": f,
                "levet": p["dias"][f]["LEVET"],
                "mobile": p["dias"][f]["MOBILE"],
                "sivale": p["dias"][f]["SIVALE"]
            })
        p["dias"] = dias_list
        matriz_final.append(p)
        
    db.close()
    return jsonify({
        "fechas": fechas_ordenadas,
        "filas": matriz_final
    })

@app.route("/api/gasolina/conciliacion")
def api_gasolina_conciliacion():
    # Compara Matriz Excel vs Tickets Gasolinera
    db = get_db(); cur = db.cursor()
    sem = semana_param()
    
    # Agrupar Excel por Fecha y Proveedor y Placa
    sql_excel = """
    SELECT r.fecha, r.proveedor, p.placa, ROUND(SUM(r.monto_reportado),2) as monto_excel
    FROM fenix_gas_reportes_diarios r
    JOIN fenix_gas_presupuestos p ON p.id = r.presupuesto_id
    WHERE (p.semana = ? OR ? IS NULL) AND p.placa IS NOT NULL AND p.placa != ''
    GROUP BY r.fecha, r.proveedor, p.placa
    """
    cur.execute(sql_excel, (sem, sem))
    excel_data = [dict(r) for r in cur.fetchall()]
    
    # Agrupar Tickets por Fecha, Proveedor y Placa
    sql_tickets = """
    SELECT fecha, gasolinera as proveedor, placa, ROUND(SUM(importe),2) as monto_ticket
    FROM fenix_gas_tickets_reales
    WHERE (semana = ? OR ? IS NULL) AND placa IS NOT NULL AND placa != ''
    GROUP BY fecha, gasolinera, placa
    """
    cur.execute(sql_tickets, (sem, sem))
    ticket_data = [dict(r) for r in cur.fetchall()]
    
    # Cruzar datos
    from collections import defaultdict
    cross = defaultdict(lambda: {"monto_excel": 0, "monto_ticket": 0})
    
    for e in excel_data:
        key = f"{e['fecha']}|{e['proveedor']}|{e['placa']}"
        cross[key]["monto_excel"] += e["monto_excel"]
        
    for t in ticket_data:
        key = f"{t['fecha']}|{t['proveedor']}|{t['placa']}"
        cross[key]["monto_ticket"] += t["monto_ticket"]
        
    alertas = []
    for key, val in cross.items():
        diff = val["monto_ticket"] - val["monto_excel"]
        if abs(diff) > 10:  # Margen de 10 pesos
            f, prov, pl = key.split("|")
            alertas.append({
                "fecha": f,
                "proveedor": prov,
                "placa": pl,
                "monto_excel": val["monto_excel"],
                "monto_ticket": val["monto_ticket"],
                "diferencia": diff
            })
            
    # Ordenar por diferencia absoluta descendente
    alertas.sort(key=lambda x: abs(x["diferencia"]), reverse=True)
    db.close()
    
    return jsonify(alertas)

# ─────────────────────────────────────────────────
#  ACARREOS / SINDICATOS
# ─────────────────────────────────────────────────
@app.route("/api/acarreos/resumen_sindicatos")
def api_resumen_sindicatos():
    db = get_db(); cur = db.cursor()
    sem = semana_param()
    sql = """SELECT s.nombre, COUNT(*) as viajes,
                    ROUND(SUM(v.subtotal),2) as subtotal,
                    ROUND(SUM(v.total),2) as total
             FROM fenix_viajes_acarreo v
             JOIN fenix_sindicatos s ON s.id = v.sindicato_id"""
    sql, p = q_filter(sql, "v.semana", sem, False)
    cur.execute(sql + " GROUP BY s.id ORDER BY total DESC", p)
    rows = [dict(r) for r in cur.fetchall()]
    db.close(); return jsonify(rows)

@app.route("/api/acarreos/detalle")
def api_acarreos_detalle():
    db = get_db(); cur = db.cursor()
    sem = semana_param()
    sql = """SELECT sindicato, obra, semana, categoria, total_viajes, total_a_pagar
             FROM v_estimacion_pagos_sindicatos"""
    sql, p = q_filter(sql, "semana", sem, False)
    cur.execute(sql + " ORDER BY total_a_pagar DESC LIMIT 40", p)
    rows = [dict(r) for r in cur.fetchall()]
    db.close(); return jsonify(rows)

@app.route("/api/acarreos/anomalias")
def api_anomalias():
    db = get_db(); cur = db.cursor()
    sem = semana_param()
    sql = """SELECT placa, fecha, COUNT(*) as viajes_dia, ROUND(SUM(subtotal),2) as monto_dia
             FROM fenix_viajes_acarreo"""
    sql, p = q_filter(sql, "semana", sem, False)
    cur.execute(sql + " GROUP BY placa, fecha HAVING viajes_dia >= 8 ORDER BY viajes_dia DESC LIMIT 20", p)
    anomalias = [dict(r) for r in cur.fetchall()]
    db.close()
    return jsonify(anomalias)

# ─────────────────────────────────────────────────
#  RENDIMIENTO
# ─────────────────────────────────────────────────
@app.route("/api/rendimiento")
def api_rendimiento():
    db = get_db(); cur = db.cursor()
    sem = semana_param()
    sql = """SELECT numero_economico, descripcion, obra, semana_num,
                    ROUND(horas_totales,1) as horas,
                    ROUND(litros_consumidos,1) as litros,
                    ROUND(rendimiento_real_lh,2) as real_lh,
                    ROUND(rendimiento_base_lh,2) as base_lh,
                    ROUND(desviacion_pct,1) as desviacion,
                    semaforo
             FROM v_rendimiento_maquinaria WHERE horas_totales > 0"""
    sql, p = q_filter(sql, "semana_num", sem)
    cur.execute(sql + " ORDER BY CASE semaforo WHEN 'ROJO - Anomalia' THEN 1 WHEN 'AMARILLO - Revisar' THEN 2 ELSE 3 END, desviacion DESC LIMIT 60", p)
    rows = [dict(r) for r in cur.fetchall()]
    db.close(); return jsonify(rows)

@app.route("/api/horas_maquinaria")
def api_horas():
    db = get_db(); cur = db.cursor()
    sem = semana_param()
    sql = """SELECT e.numero_economico, e.descripcion,
                    ROUND(SUM(h.horas_trabajadas),1) as total_horas,
                    COUNT(*) as dias_trabajados
             FROM fenix_horas_trabajo h
             JOIN fenix_equipos e ON e.id = h.equipo_id"""
    sql, p = q_filter(sql, "h.semana", sem, False)
    cur.execute(sql + " GROUP BY e.id ORDER BY total_horas DESC LIMIT 20", p)
    rows = [dict(r) for r in cur.fetchall()]
    db.close(); return jsonify(rows)

# ─────────────────────────────────────────────────
#  TOTALES / CONSOLIDADO
# ─────────────────────────────────────────────────
@app.route("/api/totales")
def api_totales():
    db = get_db(); cur = db.cursor()
    sem = semana_param()

    # 1. Diesel por semana
    cur.execute("""SELECT semana,
                          ROUND(SUM(CASE WHEN tipo_combustible='Diesel' THEN litros ELSE 0 END),1) as diesel
                   FROM fenix_movimientos_combustible
                   WHERE tipo_movimiento='CONSUMO' AND semana IS NOT NULL
                   GROUP BY semana ORDER BY semana""")
    consumos_semana_diesel = {r['semana']: dict(r) for r in cur.fetchall()}

    # 2. Gasolina por semana (Ahora desde fenix_gas_tickets_reales)
    cur.execute("""SELECT semana, ROUND(SUM(litros),1) as gasolina, ROUND(SUM(importe),2) as gasto_gasolina
                   FROM fenix_gas_tickets_reales
                   WHERE semana IS NOT NULL
                   GROUP BY semana ORDER BY semana""")
    consumos_semana_gasolina = {r['semana']: dict(r) for r in cur.fetchall()}

    all_weeks = sorted(list(set(list(consumos_semana_diesel.keys()) + list(consumos_semana_gasolina.keys()))))
    consumos_semana = []
    for w in all_weeks:
        d = consumos_semana_diesel.get(w, {'diesel': 0})
        g = consumos_semana_gasolina.get(w, {'gasolina': 0, 'gasto_gasolina': 0})
        consumos_semana.append({
            'semana': w,
            'diesel': d.get('diesel', 0),
            'gasolina': g.get('gasolina', 0),
            'gasto_gasolina': g.get('gasto_gasolina', 0)
        })

    # Acarreos por semana
    cur.execute("""SELECT semana, ROUND(SUM(total),2) as acarreos, COUNT(*) as viajes
                   FROM fenix_viajes_acarreo WHERE semana IS NOT NULL
                   GROUP BY semana ORDER BY semana""")
    acarreos_semana = [dict(r) for r in cur.fetchall()]

    # Facturas validadas totales
    cur.execute("""SELECT tipo_combustible,
                          COUNT(*) as facturas,
                          ROUND(SUM(litros_totales),1) as litros,
                          ROUND(SUM(total),2) as monto
                   FROM fenix_facturas_documentos
                   WHERE estatus_validacion='VALIDADA'
                   GROUP BY tipo_combustible""")
    facturas_resumen = [dict(r) for r in cur.fetchall()]

    db.close()
    return jsonify({
        "consumos_por_semana": consumos_semana,
        "acarreos_por_semana": acarreos_semana,
        "facturas_resumen": facturas_resumen
    })




# ─────────────────────────────────────────────────
#  RUTAS DE CAPTURA / FORMULARIOS
# ─────────────────────────────────────────────────
import os as _os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "facturas Disel")
ALLOWED_EXT = {'pdf', 'xml'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXT

@app.route("/captura")
def captura_page():
    return render_template("captura.html")

@app.route("/api/obras")
def api_obras():
    db = get_db(); cur = db.cursor()
    cur.execute("SELECT id, nombre FROM fenix_obras ORDER BY nombre")
    rows = [dict(r) for r in cur.fetchall()]
    db.close(); return jsonify(rows)

@app.route("/api/sindicatos")
def api_sindicatos():
    db = get_db(); cur = db.cursor()
    cur.execute("SELECT id, nombre FROM fenix_sindicatos ORDER BY nombre")
    rows = [dict(r) for r in cur.fetchall()]
    db.close(); return jsonify(rows)


@app.route("/api/equipos/diesel")
def api_equipos_diesel():
    db = get_db(); cur = db.cursor()
    cur.execute("""
        SELECT id, numero_economico, descripcion, tipo_combustible, obra_id
        FROM fenix_equipos
        WHERE activo=1 AND tipo_combustible='Diesel'
        ORDER BY descripcion
    """)
    rows = [dict(r) for r in cur.fetchall()]
    db.close(); return jsonify(rows)

@app.route("/api/captura/upload_reporte", methods=["POST"])
def upload_reporte():
    if "file" not in request.files: return jsonify({"error": "No se recibió archivo"}), 400
    file = request.files["file"]
    if not file.filename: return jsonify({"error": "Nombre vacío"}), 400
    
    tipo_reporte = request.form.get("tipo_reporte", "general")
    semana = request.form.get("semana", "")
    obra_id = request.form.get("obra_id", "")
    
    # Crear carpeta de reportes si no existe
    import os as _os
    reportes_dir = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "reportes_campo")
    sub_dir = _os.path.join(reportes_dir, tipo_reporte)
    _os.makedirs(sub_dir, exist_ok=True)
    
    from werkzeug.utils import secure_filename
    filename = secure_filename(file.filename)
    save_path = _os.path.join(sub_dir, filename)
    file.save(save_path)
    
    # Contar registros si es Excel
    registros = None
    mensaje = f"Reporte '{filename}' guardado correctamente"
    
    ext = filename.lower().rsplit('.', 1)[-1]
    if ext in ['xlsx', 'xls']:
        try:
            import openpyxl
            wb = openpyxl.load_workbook(save_path, data_only=True)
            ws = wb.active
            # Contar filas con datos (excluyendo header)
            rows_with_data = sum(1 for row in ws.iter_rows(min_row=2, values_only=True) if any(v for v in row))
            registros = rows_with_data
            mensaje = f"Excel cargado: {filename} — {registros} registros detectados. Semana {semana}."
        except Exception as e:
            mensaje = f"Archivo guardado: {filename} (no se pudo analizar: {str(e)[:40]})"
    elif ext == 'pdf':
        mensaje = f"PDF guardado: {filename}. Semana {semana}."
    
    # Registrar en DB
    db = get_db(); cur = db.cursor()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS fenix_reportes_campo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_archivo TEXT,
                tipo_reporte TEXT,
                semana INTEGER,
                obra_id INTEGER,
                ruta_archivo TEXT,
                registros_detectados INTEGER,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        cur.execute("""
            INSERT INTO fenix_reportes_campo 
            (nombre_archivo, tipo_reporte, semana, obra_id, ruta_archivo, registros_detectados)
            VALUES (?,?,?,?,?,?)
        """, (filename, tipo_reporte, semana or None, obra_id or None, save_path, registros))
        db.commit()
    except: pass
    db.close()
    
    return jsonify({"mensaje": mensaje, "registros": registros})

@app.route("/api/captura/diesel", methods=["POST"])
def captura_diesel():
    data = request.get_json() or {}
    required = ["semana", "fecha", "litros"]
    for field in required:
        if not data.get(field): return jsonify({"error": f"Campo requerido: {field}"}), 400
    db = get_db(); cur = db.cursor()
    try:
        # Resolver numero_economico desde equipo_id
        numero_eco = ""
        equipo_id = data.get("equipo_id")
        if equipo_id:
            db2 = get_db(); cur2 = db2.cursor()
            cur2.execute("SELECT numero_economico FROM fenix_equipos WHERE id=?", (equipo_id,))
            row2 = cur2.fetchone()
            if row2: numero_eco = row2["numero_economico"]
            db2.close()
        
        folio = data.get("folio_auto") or f"DSL-{data.get('semana','')}-{numero_eco or 'X'}"
        
        cur.execute("""
            INSERT INTO fenix_movimientos_combustible
            (semana, fecha, tipo_movimiento, tipo_combustible, numero_economico, obra_id, litros, folio_vale, observaciones)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (
            int(data["semana"]),
            data["fecha"],
            data.get("tipo_movimiento","CONSUMO"),
            "Diesel",
            numero_eco,
            data.get("obra_id") or None,
            float(data["litros"]),
            folio,
            data.get("observaciones","")
        ))
        db.commit(); db.close()
        return jsonify({"mensaje": f"Registro de Diesel guardado. {data['litros']} L"})
    except Exception as e:
        db.close(); return jsonify({"error": str(e)}), 500

@app.route("/api/captura/gasolina", methods=["POST"])
def captura_gasolina():
    data = request.get_json() or {}
    required = ["semana","fecha","litros"]
    for field in required:
        if not data.get(field): return jsonify({"error": f"Campo requerido: {field}"}), 400
    db = get_db(); cur = db.cursor()
    try:
        import re as _re
        placa = _re.sub(r"[\s\-_]+",'', str(data.get("placa","")).upper().strip()) or None
        semana_val = int(data["semana"])
        folio = f"MAN-{semana_val}-{placa or 'SIN'}-{data['fecha']}"
        cur.execute("""
            INSERT OR IGNORE INTO fenix_gas_tickets_reales
            (folio, ticket, fecha, semana, placa, conductor, responsable, obra, unidad, litros, precio_litro, importe, gasolinera)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            folio,
            data.get("ticket",""),
            data["fecha"],
            semana_val,
            placa,
            data.get("conductor",""),
            data.get("responsable",""),
            data.get("obra",""),
            data.get("unidad",""),
            float(data["litros"]),
            float(data.get("precio_litro") or 0),
            float(data.get("importe") or 0),
            data.get("gasolinera","LEVET")
        ))
        db.commit(); db.close()
        return jsonify({"mensaje": f"Ticket de Gasolina guardado: {data['litros']} L"})
    except Exception as e:
        db.close(); return jsonify({"error": str(e)}), 500

@app.route("/api/captura/acarreos", methods=["POST"])
def captura_acarreos():
    data = request.get_json() or {}
    required = ["semana","fecha","placa","total_viajes"]
    for field in required:
        if not data.get(field): return jsonify({"error": f"Campo requerido: {field}"}), 400
    db = get_db(); cur = db.cursor()
    try:
        viajes = int(data["total_viajes"])
        tarifa = float(data.get("tarifa") or 0)
        total = viajes * tarifa
        cur.execute("""
            INSERT INTO fenix_viajes_acarreo
            (semana, fecha, placa, sindicato_id, obra_id, categoria, total_viajes, subtotal, total)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (
            int(data["semana"]),
            data["fecha"],
            str(data["placa"]).upper().strip(),
            data.get("sindicato_id") or None,
            data.get("obra_id") or None,
            data.get("categoria","Volteo"),
            viajes,
            total,
            total
        ))
        db.commit(); db.close()
        return jsonify({"mensaje": f"Viaje guardado: {viajes} viajes / ${total:.2f}"})
    except Exception as e:
        db.close(); return jsonify({"error": str(e)}), 500

@app.route("/api/captura/equipo", methods=["POST"])
def captura_equipo():
    data = request.get_json() or {}
    if not data.get("numero_economico"): return jsonify({"error": "Número económico requerido"}), 400
    db = get_db(); cur = db.cursor()
    try:
        cur.execute("""
            INSERT OR REPLACE INTO fenix_equipos
            (numero_economico, descripcion, tipo, tipo_combustible, rendimiento_base_lh, obra_id, placa, activo)
            VALUES (?,?,?,?,?,?,?,1)
        """, (
            data["numero_economico"],
            data.get("descripcion",""),
            data.get("tipo","Maquinaria"),
            data.get("tipo_combustible","Diesel"),
            float(data.get("rendimiento_base_lh") or 0),
            data.get("obra_id") or None,
            str(data.get("placa","")).upper().strip() or None
        ))
        db.commit(); db.close()
        return jsonify({"mensaje": f"Equipo {data['numero_economico']} guardado"})
    except Exception as e:
        db.close(); return jsonify({"error": str(e)}), 500

@app.route("/api/captura/upload_factura", methods=["POST"])
def upload_factura():
    if "file" not in request.files: return jsonify({"error": "No se recibió archivo"}), 400
    file = request.files["file"]
    if not file.filename: return jsonify({"error": "Nombre de archivo vacío"}), 400
    if not allowed_file(file.filename): return jsonify({"error": "Tipo de archivo no permitido"}), 400
    
    filename = secure_filename(file.filename)
    save_path = _os.path.join(UPLOAD_FOLDER, filename)
    file.save(save_path)
    
    # Si es PDF, intentar clasificarlo
    if filename.lower().endswith(".pdf"):
        try:
            import pdfplumber
            with pdfplumber.open(save_path) as pdf:
                text = " ".join(page.extract_text() or "" for page in pdf.pages[:2]).upper()
            # Clasificacion basica
            tipo = "Diesel" if any(x in text for x in ["DIESEL","DISEL","PEMEX"]) else "Gasolina"
            return jsonify({"mensaje": f"PDF guardado como {filename} ({tipo} detectado)"})
        except Exception as e:
            return jsonify({"mensaje": f"PDF guardado: {filename} (sin clasificar)"})
    
    return jsonify({"mensaje": f"Archivo {filename} guardado correctamente"})

@app.route("/api/captura/recientes/diesel")
def recientes_diesel():
    db = get_db(); cur = db.cursor()
    cur.execute("""SELECT numero_economico, semana, fecha, tipo_movimiento, litros 
                   FROM fenix_movimientos_combustible 
                   WHERE tipo_combustible='Diesel'
                   ORDER BY id DESC LIMIT 10""")
    rows = [dict(r) for r in cur.fetchall()]
    db.close(); return jsonify(rows)

@app.route("/api/captura/recientes/gasolina")
def recientes_gasolina():
    db = get_db(); cur = db.cursor()
    cur.execute("""SELECT placa, conductor, fecha, litros, importe, gasolinera 
                   FROM fenix_gas_tickets_reales
                   ORDER BY id DESC LIMIT 10""")
    rows = [dict(r) for r in cur.fetchall()]
    db.close(); return jsonify(rows)

@app.route("/api/facturas_documentos")
def api_facturas_documentos():
    db = get_db(); cur = db.cursor()
    cur.execute("""SELECT folio, fecha_emision, emisor_nombre, litros_totales, total, 
                          estatus_validacion, tipo_combustible
                   FROM fenix_facturas_documentos ORDER BY fecha_emision DESC LIMIT 30""")
    rows = [dict(r) for r in cur.fetchall()]
    db.close(); return jsonify(rows)

@app.route("/")
def index():
    from flask import make_response
    resp = make_response(render_template("index.html"))
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp

if __name__ == "__main__":
    app.run(debug=True, port=5000, host="0.0.0.0")
