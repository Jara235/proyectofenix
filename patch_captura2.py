"""
Agrega al dashboard_fenix.py:
1. /api/equipos/diesel  - lista equipos de diesel para dropdown
2. /api/captura/upload_reporte - recibe reportes de ingenieros/marimba/gasolinera
3. Modificar /api/captura/diesel para usar equipo_id en lugar de numero_economico manual
   y guardar el folio auto-generado
"""
import re

with open('dashboard_fenix.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_endpoints = '''
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
'''

# Insertar antes del route de captura/diesel que ya existe
insert_after = '@app.route("/api/captura/diesel", methods=["POST"])'
if insert_after in content:
    content = content.replace(insert_after, new_endpoints + '\n' + insert_after)
else:
    # Insertar antes del route /
    content = content.replace('@app.route("/")\ndef index():', new_endpoints + '\n@app.route("/")\ndef index():')

# Modificar captura_diesel para usar equipo_id y folio_auto
old_diesel = '''        cur.execute("""
            INSERT INTO fenix_movimientos_combustible
            (semana, fecha, tipo_movimiento, tipo_combustible, numero_economico, obra_id, litros, horas_trabajadas, folio_vale, observaciones)
            VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (
            int(data["semana"]),
            data["fecha"],
            data.get("tipo_movimiento","CONSUMO"),
            "Diesel",
            data.get("numero_economico",""),
            data.get("obra_id") or None,
            float(data["litros"]),
            float(data.get("horas_trabajadas") or 0),
            data.get("folio_vale",""),
            data.get("observaciones","")
        ))'''

new_diesel = '''        # Resolver numero_economico desde equipo_id
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
        ))'''

if old_diesel in content:
    content = content.replace(old_diesel, new_diesel)
    print("Modificación de captura_diesel aplicada OK")
else:
    print("No se encontró el bloque de INSERT diesel, se dejó como estaba")

with open('dashboard_fenix.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Backend actualizado OK")
