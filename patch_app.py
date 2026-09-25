import re

with open('app_captura.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Imports and get_db
content = content.replace(
"""import sqlite3, os, datetime, re, json
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
try:
    import pdfplumber
except ImportError:
    pdfplumber = None
from flask import Flask, render_template, request, jsonify, redirect, url_for

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'fenix_v2.db')
TMPL_DIR = os.path.join(BASE_DIR, 'servidor', 'templates', 'captura_v2')
STAT_DIR = os.path.join(BASE_DIR, 'servidor', 'static', 'captura_v2')

app = Flask(__name__, template_folder=TMPL_DIR, static_folder=STAT_DIR, static_url_path='/static')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn""",
"""import os, datetime, re, json
import psycopg2
from psycopg2.extras import DictCursor
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
try:
    import pdfplumber
except ImportError:
    pdfplumber = None
from flask import Flask, render_template, request, jsonify, redirect, url_for

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TMPL_DIR = os.path.join(BASE_DIR, 'servidor', 'templates', 'captura_v2')
STAT_DIR = os.path.join(BASE_DIR, 'servidor', 'static', 'captura_v2')

app = Flask(__name__, template_folder=TMPL_DIR, static_folder=STAT_DIR, static_url_path='/static')

def get_db():
    conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
    return conn"""
)

# 2. Update table names
table_mapping = {
    'gasolina_consumos': 'gasolina.consumos',
    'gasolina_facturas': 'gasolina.facturas',
    'diesel_consumos': 'diesel.consumos',
    'diesel_facturas': 'diesel.facturas',
    'catalogos_obras': 'catalogos.obras',
    'catalogos_equipos': 'catalogos.equipos',
    'catalogos_operadores': 'catalogos.operadores',
    'catalogos_operaciones': 'catalogos.operaciones'
}

for old, new in table_mapping.items():
    content = content.replace(old, new)

# 3. Handle parameter placeholders "?" -> "%s"
content = re.sub(r"LIKE '\?%'", r"LIKE %s", content) # not existing actually
content = content.replace("=?", "=%s")
content = content.replace("LIKE ?", "LIKE %s")

# Fix LIKE 'GAS-%' to 'GAS-%%'
content = content.replace("LIKE 'GAS-%'", "LIKE 'GAS-%%'")
content = content.replace("LIKE 'FA-%'", "LIKE 'FA-%%'")
content = content.replace("LIKE 'FAC-%'", "LIKE 'FAC-%%'")

content = content.replace("f\"{tipo_op}-%\"", "f\"{tipo_op}-%%\"")

# For parameter substitution in INSERT statements
content = content.replace("VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
content = content.replace("VALUES (?, ?, ?, ?, ?, ?, ?, ?)", "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
content = content.replace("VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
content = content.replace("VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
content = content.replace("VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
content = content.replace("VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

# Replace sqlite == with pg =
content = content.replace("origen == 'FACTURA'", "origen = 'FACTURA'")

# 4. Handle db.execute -> cur.execute
content = content.replace('db.execute(', 'cur.execute(')

# Helper function to inject cursor setup before cur.execute
# but it's simpler to do simple string replacements for the exact lines.

content = content.replace("    obras = cur.execute('SELECT nombre FROM catalogos.obras ORDER BY nombre').fetchall()",
                          "    cur = db.cursor(cursor_factory=DictCursor)\n    cur.execute('SELECT nombre FROM catalogos.obras ORDER BY nombre')\n    obras = cur.fetchall()")

content = content.replace("    operaciones = cur.execute('SELECT tipo_operacion FROM catalogos.operaciones ORDER BY id').fetchall()",
                          "    cur.execute('SELECT tipo_operacion FROM catalogos.operaciones ORDER BY id')\n    operaciones = cur.fetchall()")

content = content.replace("    equipos = cur.execute('SELECT numero_economico, descripcion FROM catalogos.equipos ORDER BY numero_economico').fetchall()",
                          "    cur.execute('SELECT numero_economico, descripcion FROM catalogos.equipos ORDER BY numero_economico')\n    equipos = cur.fetchall()")

content = content.replace("    operadores = cur.execute('SELECT nombre FROM catalogos.operadores ORDER BY nombre').fetchall()",
                          "    cur.execute('SELECT nombre FROM catalogos.operadores ORDER BY nombre')\n    operadores = cur.fetchall()")

content = content.replace("    operaciones = cur.execute('SELECT tipo_operacion, codigo_operacion FROM catalogos.operaciones ORDER BY id').fetchall()",
                          "    cur.execute('SELECT tipo_operacion, codigo_operacion FROM catalogos.operaciones ORDER BY id')\n    operaciones = cur.fetchall()")

content = content.replace("    historial_consumos = cur.execute(\"SELECT folio_conciliacion, fecha, obra_destino, equipo_economico, litros FROM diesel.consumos WHERE origen != 'FACTURA' ORDER BY id DESC LIMIT 5\").fetchall()",
                          "    cur.execute(\"SELECT folio_conciliacion, fecha, obra_destino, equipo_economico, litros FROM diesel.consumos WHERE origen != 'FACTURA' ORDER BY id DESC LIMIT 5\")\n    historial_consumos = cur.fetchall()")

content = content.replace("    historial_facturas_raw = cur.execute(\"SELECT observaciones, fecha as fecha_factura, litros as litros_facturados, importe_total FROM diesel.consumos WHERE origen='FACTURA' ORDER BY id DESC LIMIT 5\").fetchall()",
                          "    cur.execute(\"SELECT observaciones, fecha as fecha_factura, litros as litros_facturados, importe_total FROM diesel.consumos WHERE origen='FACTURA' ORDER BY id DESC LIMIT 5\")\n    historial_facturas_raw = cur.fetchall()")

content = content.replace("    historial_consumos = cur.execute('SELECT folio_conciliacion, fecha, obra_destino, vehiculo, litros FROM gasolina.consumos ORDER BY id DESC LIMIT 5').fetchall()",
                          "    cur.execute('SELECT folio_conciliacion, fecha, obra_destino, vehiculo, litros FROM gasolina.consumos ORDER BY id DESC LIMIT 5')\n    historial_consumos = cur.fetchall()")

content = content.replace("        historial_facturas_raw = cur.execute('SELECT uuid_cfdi, fecha_factura, litros_facturados, importe_total FROM gasolina.facturas ORDER BY id DESC LIMIT 5').fetchall()",
                          "        cur.execute('SELECT uuid_cfdi, fecha_factura, litros_facturados, importe_total FROM gasolina.facturas ORDER BY id DESC LIMIT 5')\n        historial_facturas_raw = cur.fetchall()")

content = content.replace("    obras = cur.execute('SELECT * FROM catalogos.obras').fetchall()",
                          "    cur = db.cursor(cursor_factory=DictCursor)\n    cur.execute('SELECT * FROM catalogos.obras')\n    obras = cur.fetchall()")

content = content.replace("    equipos = cur.execute('SELECT * FROM catalogos.equipos').fetchall()",
                          "    cur.execute('SELECT * FROM catalogos.equipos')\n    equipos = cur.fetchall()")

content = content.replace("    operadores = cur.execute('SELECT * FROM catalogos.operadores').fetchall()",
                          "    cur.execute('SELECT * FROM catalogos.operadores')\n    operadores = cur.fetchall()")

content = content.replace("    res = cur.execute('SELECT responsable_default FROM catalogos.obras WHERE nombre=%s', (obra_nombre,)).fetchone()",
                          "    cur = db.cursor(cursor_factory=DictCursor)\n    cur.execute('SELECT responsable_default FROM catalogos.obras WHERE nombre=%s', (obra_nombre,))\n    res = cur.fetchone()")

content = content.replace("    res = cur.execute('SELECT operador_default FROM catalogos.equipos WHERE numero_economico=%s', (equipo_eco,)).fetchone()",
                          "    cur = db.cursor(cursor_factory=DictCursor)\n    cur.execute('SELECT operador_default FROM catalogos.equipos WHERE numero_economico=%s', (equipo_eco,))\n    res = cur.fetchone()")

content = content.replace("        obras = cur.execute(\"SELECT nombre, codigo FROM catalogos.obras\").fetchall()",
                          "        cur = db.cursor(cursor_factory=DictCursor)\n        cur.execute(\"SELECT nombre, codigo FROM catalogos.obras\")\n        obras = cur.fetchall()")

content = content.replace("        obra_row = cur.execute('SELECT codigo FROM catalogos.obras WHERE nombre=%s', (data.get('obra_destino'),)).fetchone()",
                          "        cur = db.cursor(cursor_factory=DictCursor)\n        cur.execute('SELECT codigo FROM catalogos.obras WHERE nombre=%s', (data.get('obra_destino'),))\n        obra_row = cur.fetchone()")

content = content.replace("        folios = cur.execute(\"SELECT folio_conciliacion FROM gasolina.consumos WHERE semana=%s AND folio_conciliacion LIKE 'GAS-%%'\", (semana,)).fetchall()",
                          "        cur.execute(\"SELECT folio_conciliacion FROM gasolina.consumos WHERE semana=%s AND folio_conciliacion LIKE 'GAS-%%'\", (semana,))\n        folios = cur.fetchall()")

content = content.replace("        obra_row = cur.execute('SELECT codigo FROM catalogos.obras WHERE nombre=%s', (obra_nombre,)).fetchone()",
                          "        cur = db.cursor(cursor_factory=DictCursor)\n        cur.execute('SELECT codigo FROM catalogos.obras WHERE nombre=%s', (obra_nombre,))\n        obra_row = cur.fetchone()")

content = content.replace("        folios = cur.execute(\"SELECT folio_conciliacion FROM gasolina.facturas WHERE semana=%s AND folio_conciliacion LIKE 'FA-%%'\", (semana,)).fetchall()",
                          "        cur.execute(\"SELECT folio_conciliacion FROM gasolina.facturas WHERE semana=%s AND folio_conciliacion LIKE 'FA-%%'\", (semana,))\n        folios = cur.fetchall()")

content = content.replace("        db_folios = [row['folio_conciliacion'] for row in cur.execute('SELECT folio_conciliacion FROM diesel.consumos').fetchall()]",
                          "        cur = db.cursor(cursor_factory=DictCursor)\n        cur.execute('SELECT folio_conciliacion FROM diesel.consumos')\n        db_folios = [row['folio_conciliacion'] for row in cur.fetchall()]")

content = content.replace("        folios = cur.execute(\"SELECT folio_conciliacion FROM diesel.facturas WHERE semana=%s AND folio_conciliacion LIKE 'FAC-%%'\", (semana,)).fetchall()",
                          "        cur.execute(\"SELECT folio_conciliacion FROM diesel.facturas WHERE semana=%s AND folio_conciliacion LIKE 'FAC-%%'\", (semana,))\n        folios = cur.fetchall()")

content = content.replace("        eq_row = cur.execute('SELECT descripcion FROM catalogos.equipos WHERE numero_economico=%s', (data.get('equipo_economico'),)).fetchone()",
                          "        cur = db.cursor(cursor_factory=DictCursor)\n        cur.execute('SELECT descripcion FROM catalogos.equipos WHERE numero_economico=%s', (data.get('equipo_economico'),))\n        eq_row = cur.fetchone()")

content = content.replace("        obra_row = cur.execute('SELECT codigo FROM catalogos.obras WHERE nombre=%s', (data.get('obra_destino'),)).fetchone()",
                          "        cur.execute('SELECT codigo FROM catalogos.obras WHERE nombre=%s', (data.get('obra_destino'),))\n        obra_row = cur.fetchone()")

content = content.replace("        folios = cur.execute(\"SELECT folio_conciliacion FROM diesel.consumos WHERE semana=%s AND folio_conciliacion LIKE %s\", (semana, f\"{tipo_op}-%%\")).fetchall()",
                          "        cur.execute(\"SELECT folio_conciliacion FROM diesel.consumos WHERE semana=%s AND folio_conciliacion LIKE %s\", (semana, f\"{tipo_op}-%%\"))\n        folios = cur.fetchall()")

content = content.replace("        diesel_lts = cur.execute(\"SELECT COALESCE(SUM(litros),0) FROM diesel.consumos WHERE origen != 'FACTURA'\").fetchone()[0]",
                          "        cur = db.cursor(cursor_factory=DictCursor)\n        cur.execute(\"SELECT COALESCE(SUM(litros),0) FROM diesel.consumos WHERE origen != 'FACTURA'\")\n        diesel_lts = cur.fetchone()[0]")

content = content.replace("        diesel_imp = cur.execute(\"SELECT COALESCE(SUM(importe_total),0) FROM diesel.consumos WHERE origen != 'FACTURA'\").fetchone()[0]",
                          "        cur.execute(\"SELECT COALESCE(SUM(importe_total),0) FROM diesel.consumos WHERE origen != 'FACTURA'\")\n        diesel_imp = cur.fetchone()[0]")

content = content.replace("        diesel_reg = cur.execute(\"SELECT COUNT(*) FROM diesel.consumos WHERE origen != 'FACTURA'\").fetchone()[0]",
                          "        cur.execute(\"SELECT COUNT(*) FROM diesel.consumos WHERE origen != 'FACTURA'\")\n        diesel_reg = cur.fetchone()[0]")

content = content.replace("        fac_total = cur.execute(\"SELECT COUNT(*) FROM diesel.consumos WHERE origen = 'FACTURA'\").fetchone()[0]",
                          "        cur.execute(\"SELECT COUNT(*) FROM diesel.consumos WHERE origen = 'FACTURA'\")\n        fac_total = cur.fetchone()[0]")

content = content.replace("        fac_imp = cur.execute(\"SELECT COALESCE(SUM(importe_total),0) FROM diesel.consumos WHERE origen = 'FACTURA'\").fetchone()[0]",
                          "        cur.execute(\"SELECT COALESCE(SUM(importe_total),0) FROM diesel.consumos WHERE origen = 'FACTURA'\")\n        fac_imp = cur.fetchone()[0]")

content = content.replace("        rows = cur.execute(query, params).fetchall()",
                          "        cur = db.cursor(cursor_factory=DictCursor)\n        cur.execute(query, params)\n        rows = cur.fetchall()")

content = content.replace("        cur.execute('''INSERT INTO diesel.facturas", "        cur = db.cursor(cursor_factory=DictCursor)\n        cur.execute('''INSERT INTO diesel.facturas")

with open('app_captura_postgres.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Patch script created successfully.")
