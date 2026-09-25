"""Patch: Agregar los endpoints de captura de datos al dashboard_fenix.py"""
import re

with open('dashboard_fenix.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Asegurarse de que flask.request y werkzeug esten importados
if 'from flask import' in content and 'request' not in content.split('from flask import')[1].split('\n')[0]:
    content = content.replace('from flask import jsonify, Flask, render_template', 
                               'from flask import jsonify, Flask, render_template, request')

captura_routes = '''
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

@app.route("/api/captura/diesel", methods=["POST"])
def captura_diesel():
    data = request.get_json() or {}
    required = ["semana", "fecha", "litros"]
    for field in required:
        if not data.get(field): return jsonify({"error": f"Campo requerido: {field}"}), 400
    db = get_db(); cur = db.cursor()
    try:
        cur.execute("""
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
        placa = _re.sub(r"[\\s\\-_]+",'', str(data.get("placa","")).upper().strip()) or None
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
'''

# Insertar antes de la ruta @app.route("/")
insert_before = '@app.route("/")\ndef index():'
if insert_before in content:
    content = content.replace(insert_before, captura_routes + '\n' + insert_before)
else:
    # Si no existe, agregar al final antes de if __name__
    content = content.replace('if __name__ == "__main__":', captura_routes + '\nif __name__ == "__main__":')

with open('dashboard_fenix.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Captura endpoints agregados exitosamente")
