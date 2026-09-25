import pdfplumber
import openpyxl
import re
import os
from datetime import datetime

MESES = {
    'ENERO': 1, 'FEBRERO': 2, 'MARZO': 3, 'ABRIL': 4,
    'MAYO': 5, 'JUNIO': 6, 'JULIO': 7, 'AGOSTO': 8,
    'SEPTIEMBRE': 9, 'OCTUBRE': 10, 'NOVIEMBRE': 11, 'DICIEMBRE': 12
}

def clean_float(val):
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).replace('$', '').replace(' ', '').strip()
    if not s or s == '-' or s == '0':
        return 0.0
    # Handle PDF formatting quirk where 23.195 Lts is printed as 23,195
    if ',' in s and '.' not in s:
        parts = s.split(',')
        if len(parts) == 2 and len(parts[1]) == 3:
            s = parts[0] + '.' + parts[1]
        else:
            s = s.replace(',', '')
    else:
        s = s.replace(',', '')
    try:
        return float(s)
    except Exception:
        return 0.0

def extraer_jalisco_documento(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return extraer_pdf_jalisco(file_path)
    elif ext in ['.xlsx', '.xls']:
        return extraer_excel_jalisco(file_path)
    else:
        raise ValueError(f"Formato no soportado: {ext}")

def extraer_pdf_jalisco(pdf_path):
    data = {
        'semana': None,
        'rango_fechas': '',
        'precio_diesel': 27.0,
        'precio_gasolina_magna': 23.97,
        'precio_gasolina_premium': 29.29,
        'consumos': []
    }
    
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        tables = page.extract_tables()
        
        # 1. Buscar Header (Semana, Fechas, Precios)
        header_text = ""
        for t in tables:
            for row in t:
                for cell in row:
                    if cell:
                        c_str = str(cell).upper().replace('\n', ' ')
                        header_text += " " + c_str
                        if 'PRECIO LT DIESEL' in c_str:
                            m_p = re.search(r'(\d+\.?\d*)', c_str)
                            if m_p: data['precio_diesel'] = float(m_p.group(1))
                        elif 'MAGNA' in c_str:
                            m_p = re.search(r'(\d+\.?\d*)', c_str)
                            if m_p: data['precio_gasolina_magna'] = float(m_p.group(1))
                        elif 'PREMIUM' in c_str:
                            m_p = re.search(r'(\d+\.?\d*)', c_str)
                            if m_p: data['precio_gasolina_premium'] = float(m_p.group(1))
                            
        m_sem = re.search(r'SEM\s*#?\s*(\d+)', header_text)
        if m_sem:
            data['semana'] = int(m_sem.group(1))
            
        m_year = re.search(r'DEL\s+.*?(\d{4})', header_text)
        year = int(m_year.group(1)) if m_year else datetime.now().year
        
        meses_encontrados = []
        for word in header_text.split():
            clean_word = word.strip(',.').upper()
            if clean_word in MESES:
                meses_encontrados.append(MESES[clean_word])
                
        # 2. Parsear Tabla Principal de Consumos
        tabla_principal = None
        for t in tables:
            for r in t:
                r_str = " ".join(str(c) for c in r if c).upper()
                if 'REGISTRO DE CONSUMOS' in r_str or 'REGISTRO CONSUMOS' in r_str:
                    tabla_principal = t
                    break
            if tabla_principal: break
            
        if not tabla_principal:
            # Fallback: buscar tabla con headers EQUIPO o CAMIONETA
            for t in tables:
                for r in t:
                    if r and r[0] and str(r[0]).strip().upper() in ['EQUIPO', 'CAMIONETA']:
                        tabla_principal = t
                        break
                if tabla_principal: break

        if not tabla_principal:
            return data

        modo_actual = None
        dias_headers = []
        
        for row in tabla_principal:
            if not row or not any(row): continue
            cell0 = str(row[0] or '').strip().upper()
            
            if 'REGISTRO DE CONSUMOS DIESEL' in cell0 or 'CONSUMOS DIESEL' in cell0:
                modo_actual = 'DIESEL'
                continue
            elif 'REGISTRO CONSUMOS GASOLINA' in cell0 or 'CONSUMOS GASOLINA' in cell0:
                modo_actual = 'GASOLINA'
                continue
                
            if cell0 in ['EQUIPO', 'CAMIONETA', 'MAQUINARIA']:
                dias_headers = []
                for i in range(1, len(row)):
                    col_header = str(row[i] or '').strip().upper().replace('\n', ' ')
                    m_dia = re.search(r'([A-ZÁÉÍÓÚ]+)\s+(\d+)', col_header)
                    if m_dia:
                        dia_nom = m_dia.group(1)
                        dia_num = int(m_dia.group(2))
                        mes_elegido = meses_encontrados[0] if meses_encontrados else datetime.now().month
                        if len(meses_encontrados) > 1 and dia_num < 10:
                            mes_elegido = meses_encontrados[-1]
                        
                        try:
                            fecha_str = f"{year}-{mes_elegido:02d}-{dia_num:02d}"
                            dias_headers.append((i, fecha_str, dia_nom))
                        except ValueError: pass
                continue
                
            if cell0 in ['SUMA', 'LIMPIEZAS', 'OTROS', 'TOTAL', 'TOTALES']:
                continue
                
            equipo = str(row[0] or '').replace('\n', ' ').strip()
            if not equipo or equipo.upper() in ['SUMA', 'LIMPIEZAS', 'OTROS']:
                continue

            if modo_actual:
                for idx_col, fecha_str, dia_nom in dias_headers:
                    if idx_col < len(row):
                        lts = clean_float(row[idx_col])
                        if lts > 0:
                            costo = data['precio_diesel'] if modo_actual == 'DIESEL' else data['precio_gasolina_magna']
                            data['consumos'].append({
                                'fecha': fecha_str,
                                'dia': dia_nom,
                                'equipo': equipo,
                                'litros': lts,
                                'costo_por_litro': costo,
                                'importe_total': round(lts * costo, 2),
                                'tipo_combustible': modo_actual,
                                'semana': data['semana']
                            })
                            
    return data

def extraer_excel_jalisco(xlsx_path):
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    
    data = {
        'semana': None,
        'rango_fechas': '',
        'precio_diesel': 27.0,
        'precio_gasolina_magna': 23.97,
        'precio_gasolina_premium': 29.29,
        'consumos': []
    }
    
    # Procesar la última hoja o la hoja con más semana
    sheets_to_process = wb.sheetnames
    
    for sname in sheets_to_process:
        sheet = wb[sname]
        m_sem = re.search(r'SEMANA\s*(\d+)', sname.upper())
        sheet_sem = int(m_sem.group(1)) if m_sem else None
        
        # Parsear header de la hoja
        header_txt = ""
        for r in range(1, 10):
            for c in range(1, 10):
                v = sheet.cell(r, c).value
                if v: header_txt += " " + str(v).upper()
                
        sem = sheet_sem
        m_sem_txt = re.search(r'SEM\s*#?\s*(\d+)', header_txt)
        if m_sem_txt: sem = int(m_sem_txt.group(1))
        
        m_year = re.search(r'DEL\s+.*?(\d{4})', header_txt)
        year = int(m_year.group(1)) if m_year else datetime.now().year
        
        meses_encontrados = []
        for word in header_txt.split():
            clean_word = word.strip(',.').upper()
            if clean_word in MESES:
                meses_encontrados.append(MESES[clean_word])

        p_diesel = 27.0
        p_gas = 23.97
        for r in range(1, 15):
            for c in range(1, 8):
                v = str(sheet.cell(r, c).value or '').upper()
                if 'PRECIO LT DIESEL' in v:
                    val_c = sheet.cell(r, c+1).value or sheet.cell(r, c+2).value
                    if val_c: p_diesel = clean_float(val_c) or 27.0
                elif 'MAGNA' in v:
                    val_c = sheet.cell(r, c+1).value or sheet.cell(r, c+2).value
                    if val_c: p_gas = clean_float(val_c) or 23.97

        modo_actual = None
        dias_headers = []

        for r in range(1, sheet.max_row + 1):
            cell0 = str(sheet.cell(r, 1).value or '').strip().upper()
            
            if 'REGISTRO DE CONSUMOS DIESEL' in cell0:
                modo_actual = 'DIESEL'
                continue
            elif 'REGISTRO CONSUMOS GASOLINA' in cell0:
                modo_actual = 'GASOLINA'
                continue
                
            if cell0 in ['EQUIPO', 'CAMIONETA', 'MAQUINARIA']:
                dias_headers = []
                for c in range(2, 10):
                    col_header = str(sheet.cell(r, c).value or '').strip().upper()
                    m_dia = re.search(r'([A-ZÁÉÍÓÚ]+)\s+(\d+)', col_header)
                    if m_dia:
                        dia_nom = m_dia.group(1)
                        dia_num = int(m_dia.group(2))
                        mes_elegido = meses_encontrados[0] if meses_encontrados else datetime.now().month
                        if len(meses_encontrados) > 1 and dia_num < 10:
                            mes_elegido = meses_encontrados[-1]
                        
                        try:
                            fecha_str = f"{year}-{mes_elegido:02d}-{dia_num:02d}"
                            dias_headers.append((c, fecha_str, dia_nom))
                        except ValueError: pass
                continue

            if cell0 in ['SUMA', 'LIMPIEZAS', 'OTROS', 'TOTAL', 'TOTALES', '']:
                continue

            equipo = str(sheet.cell(r, 1).value or '').strip()
            if not equipo or equipo.upper() in ['SUMA', 'LIMPIEZAS', 'OTROS']:
                continue

            if modo_actual and sem:
                for idx_col, fecha_str, dia_nom in dias_headers:
                    val = sheet.cell(r, idx_col).value
                    lts = clean_float(val)
                    if lts > 0:
                        costo = p_diesel if modo_actual == 'DIESEL' else p_gas
                        data['consumos'].append({
                            'fecha': fecha_str,
                            'dia': dia_nom,
                            'equipo': equipo,
                            'litros': lts,
                            'costo_por_litro': costo,
                            'importe_total': round(lts * costo, 2),
                            'tipo_combustible': modo_actual,
                            'semana': sem
                        })
                        if not data['semana']: data['semana'] = sem
                        
    return data

if __name__ == '__main__':
    import sys
    import json
    if len(sys.argv) > 1:
        res = extraer_jalisco_documento(sys.argv[1])
        print(f"Semana: {res['semana']} | Consumos extraídos: {len(res['consumos'])}")
        print(json.dumps(res['consumos'][:5], indent=2, ensure_ascii=False))
