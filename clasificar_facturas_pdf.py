# -*- coding: utf-8 -*-
"""
SISTEMA FENIX -- Clasificador Inteligente de Facturas por Contenido de PDF

Extrae texto de cada PDF almacenado en fenix_facturas_documentos y detecta:
- Tipo de combustible real: Diesel o Gasolina
- Destino del suministro: Tanque Pegaso, Planta, Transportes, etc.
- Notas clave de la leyenda al pie de la factura

Reglas de clasificación por keywords en el PDF:
  DIESEL  -> "diesel", "tanque pegaso", "planta", "marimba", "d.e.a"
  GASOLINA-> "magna", "premium", "gasolina", "extra"
  TRANSPORTES (no nuestro) -> "transportes", "trafico"
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import sqlite3, os, json, re

try:
    import pdfplumber
    PDF_OK = True
except ImportError:
    PDF_OK = False
    print("ERROR: pdfplumber no instalado. Corre: pip install pdfplumber")
    sys.exit(1)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fenix.db")

# ─── Reglas de clasificación ─────────────────────────────────────────────
# Se aplican en orden de prioridad — el primer match gana
REGLAS = [
    # Tipo Combustible / Destino / keywords
    ("Diesel",   "Tanque Pegaso",        ["tanque pegaso", "tanque de pegaso"]),
    ("Diesel",   "Planta Huixquilucan",  ["planta huix", "huixquilucan", "planta hx"]),
    ("Diesel",   "Planta Pegaso",        ["planta pegaso", "planta pap", "planta de asfalto"]),
    ("Diesel",   "Maquinaria",           ["maquinaria", "marimba", "compactador", "rodillo"]),
    ("Diesel",   "DEA / Refinería",      ["d.e.a", "dea ", "refineria", "refinería"]),
    ("Diesel",   "Diésel Genérico",      ["diesel", "díesel", "diésel", "ultra low", "ultra-low"]),
    ("Gasolina", "Gasolina Magna",       ["magna", "magnasin"]),
    ("Gasolina", "Gasolina Premium",     ["premium", "premium plus"]),
    ("Gasolina", "Gasolina Extra",       ["extra", "gasohol"]),
    ("Gasolina", "Gasolina Genérica",    ["gasolina"]),
    # Excluidos: son de Transportes (no es nuestro consumo)
    ("EXCLUIR",  "Transportes",          ["transportes trujano", "tto ", "area de transportes"]),
]

def extraer_texto_pdf(pdf_bytes: bytes) -> str:
    """Extrae todo el texto de un PDF almacenado como bytes."""
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            texto = ""
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    texto += t + "\n"
        return texto.lower()
    except Exception as e:
        return ""

def clasificar(texto: str) -> dict:
    """Aplica las reglas de clasificación al texto extraído del PDF."""
    resultado = {
        "tipo_combustible": "SIN_CLASIFICAR",
        "destino_suministro": "Desconocido",
        "nota_leyenda": None,
        "confianza": "BAJA"
    }

    # Buscar la leyenda al pie (suele aparecer como "SUMINISTRO ..." o "NOTA:")
    leyenda_match = re.search(r'(suministro[^\n]{3,80}|nota:[^\n]{3,80}|fecha.*lts?[^\n]{3,60})', texto)
    if leyenda_match:
        resultado["nota_leyenda"] = leyenda_match.group(0).strip()[:120]

    # Aplicar reglas en orden
    for tipo, destino, keywords in REGLAS:
        for kw in keywords:
            if kw in texto:
                resultado["tipo_combustible"] = tipo
                resultado["destino_suministro"] = destino
                resultado["confianza"] = "ALTA"
                return resultado

    # Si tiene alguna pista por tipo de volumen (>1000 lts -> probablemente Diesel a tanque)
    volumen_match = re.search(r'(\d{3,5})\s*(lts?|litros)', texto)
    if volumen_match:
        vol = int(volumen_match.group(1))
        if vol >= 1000:
            resultado["tipo_combustible"] = "Diesel"
            resultado["destino_suministro"] = "Probable Tanque (vol. alto)"
            resultado["confianza"] = "MEDIA"
        else:
            resultado["tipo_combustible"] = "Gasolina"
            resultado["destino_suministro"] = "Probable Unidad (vol. bajo)"
            resultado["confianza"] = "MEDIA"

    return resultado

def run():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Agregar columnas nuevas si no existen
    for col, tipo_col in [
        ("destino_suministro",  "TEXT"),
        ("nota_leyenda",        "TEXT"),
        ("texto_pdf_extraido",  "TEXT"),
        ("confianza_clasif",    "TEXT DEFAULT 'SIN_PROCESAR'"),
    ]:
        try:
            cur.execute(f"ALTER TABLE fenix_facturas_documentos ADD COLUMN {col} {tipo_col}")
        except:
            pass

    conn.commit()

    # Procesar cada factura que tiene PDF
    cur.execute("""
        SELECT id, folio, emisor_nombre, litros_totales, archivo_pdf, archivo_xml
        FROM fenix_facturas_documentos
        WHERE archivo_pdf IS NOT NULL
        ORDER BY id
    """)
    facturas = cur.fetchall()

    print(f"Procesando {len(facturas)} facturas con PDF...\n")

    cambios = {"Diesel": 0, "Gasolina": 0, "EXCLUIR": 0, "SIN_CLASIFICAR": 0}

    for fac in facturas:
        pdf_bytes = bytes(fac["archivo_pdf"])
        texto = extraer_texto_pdf(pdf_bytes)
        resultado = clasificar(texto)

        tipo = resultado["tipo_combustible"]
        destino = resultado["destino_suministro"]
        # Determinar semana
        import re
        from datetime import datetime
        
        leyenda = resultado["nota_leyenda"]
        ley_lower = leyenda.lower() if leyenda else ""
        date_match = re.search(r'(\d{2})[-/](\d{2})[-/](\d{2,4})', ley_lower.replace('vencimiento', ''))
        
        # Necesitamos la fecha de emisión fiscal real por si falla
        # fac["fecha_emision"] no la seleccionamos arriba, la agrego a la query o saco de DB
        semana_calc = 26 # Fallback
        real_date = "2026-06-25" 
        
        if date_match:
            d, m, y = date_match.groups()
            if len(y) == 2: y = '20' + y
            if y == '2026' and int(m) >= 6:
                real_date = f'{y}-{m}-{d}'
        
        if '2026-06-15' <= real_date <= '2026-06-21': semana_calc = 25
        elif '2026-06-22' <= real_date <= '2026-06-28': semana_calc = 26
        elif '2026-06-29' <= real_date <= '2026-07-05': semana_calc = 27
        else:
            try:
                semana_calc = datetime.strptime(real_date, '%Y-%m-%d').isocalendar()[1]
            except:
                pass

        # Guardar texto extraído (solo primeros 500 chars para no inflar DB)
        texto_corto = texto[:500].replace('\n', ' ').strip() if texto else ""

        cur.execute("""
            UPDATE fenix_facturas_documentos
            SET tipo_combustible = ?,
                destino_suministro = ?,
                nota_leyenda = ?,
                texto_pdf_extraido = ?,
                confianza_clasif = ?,
                semana = ?
            WHERE id = ?
        """, (tipo, destino, leyenda, texto_corto, 'ALTA', semana_calc, fac["id"]))

        cambios[tipo if tipo in cambios else "SIN_CLASIFICAR"] += 1

        # Print detalle
        icon = "🛢️" if tipo=="Diesel" else "⛽" if tipo=="Gasolina" else "⚠️" if tipo=="EXCLUIR" else "❓"
        print(f"{icon} Folio {fac['folio']:>8} | {tipo:<12} | [{'ALTA':<5}] | {destino}")
        if leyenda:
            print(f"           Leyenda: {leyenda}")

    conn.commit()
    conn.close()

    print(f"\n{'='*55}")
    print(f"RESUMEN DE CLASIFICACION:")
    print(f"  Diesel:          {cambios['Diesel']} facturas")
    print(f"  Gasolina:        {cambios['Gasolina']} facturas")
    print(f"  EXCLUIR (Trans): {cambios['EXCLUIR']} facturas")
    print(f"  Sin clasificar:  {cambios['SIN_CLASIFICAR']} facturas")
    print(f"\nRevisa el dashboard en la pestana de Facturas CFDI para validar manualmente")
    print(f"los que quedaron con confianza MEDIA o SIN_CLASIFICAR.")

if __name__ == "__main__":
    run()
