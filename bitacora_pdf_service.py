import os, re, datetime
try:
    import pdfplumber
except ImportError:
    pdfplumber = None

def parse_bitacora_pdf(pdf_path):
    """
    Lee a fondo un archivo PDF de bitácora semanal (GC-COMB-006 u otros formatos de marimba/planta/obra)
    y extrae encabezados y todas las filas detalladas de consumo, con soporte para múltiples semanas por fecha.
    """
    resultado = {
        'semana': datetime.datetime.now().isocalendar()[1],
        'operador': '',
        'marimba': 'Marimba M-01',
        'obra_detectada': '',
        'responsable': '',
        'filas': []
    }
    
    if not pdfplumber:
        return resultado
        
    try:
        full_text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                full_text += text + "\n"
                
                # 1. Extraer por tablas estructuradas de pdfplumber
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        if not row or len(row) < 4:
                            continue
                            
                        row_clean = [str(cell or '').strip().replace('\n', ' ') for cell in row]
                        first_cell = row_clean[0].upper()
                        
                        if any(k in first_cell for k in ['FECHA', 'TOTAL', 'SUBTOTAL', 'REGISTRO', 'DESPACHO']) or not first_cell:
                            continue
                            
                        # Buscar patrón de fecha (DD/MM/YYYY o DD-MM-YYYY)
                        match_fecha = re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', row_clean[0])
                        if not match_fecha:
                            continue
                            
                        fecha_std = normalizar_fecha(row_clean[0])
                        
                        tipo_mov = row_clean[1] if len(row_clean) > 1 else 'Salida'
                        origen_obra = row_clean[2] if len(row_clean) > 2 else ''
                        equipo = row_clean[3] if len(row_clean) > 3 else ''
                        economico = row_clean[4] if len(row_clean) > 4 else ''
                        
                        # Extraer litros de salida (columna 6, 5, 4, 3)
                        salida_val = 0.0
                        for col_idx in [6, 5, 4, 3]:
                            if len(row_clean) > col_idx and row_clean[col_idx]:
                                try:
                                    v = float(str(row_clean[col_idx]).replace(',', '').strip())
                                    if v > 0:
                                        salida_val = v
                                        break
                                except ValueError: pass
                                
                        ticket_ref = row_clean[8] if len(row_clean) > 8 else ''
                        obs = row_clean[9] if len(row_clean) > 9 else ''

                        # Si no hay equipo, pero la celda o las observaciones tienen texto
                        if not equipo and not economico and obs:
                            if not any(k in obs.upper() for k in ['TOTAL', 'SUBTOTAL', 'SUMA', 'SALDO']):
                                equipo = obs

                        # Descartar filas de sumas o totales sin equipo
                        if not equipo and not economico:
                            continue
                            
                        if any(k in equipo.upper() for k in ['TOTAL', 'SUBTOTAL', 'SUMA', 'SALDO', 'INVENTARIO']):
                            continue
                        
                        # Calcular semana ISO de la fecha
                        try:
                            f_dt = datetime.datetime.strptime(fecha_std, '%Y-%m-%d').date()
                            row_semana = f_dt.isocalendar()[1]
                        except:
                            row_semana = resultado['semana']
                            
                        # Detectar si la observación contiene obra específica
                        row_obra = origen_obra
                        if 'ALFREDO DEL MAZO' in obs.upper() or 'ALFREDO DEL MAZO' in full_text.upper():
                            if not row_obra: row_obra = 'Alfredo del Mazo'
                        if 'AURELIO VENEGAS' in obs.upper():
                            row_obra = 'Alfredo del Mazo'

                        if salida_val > 0:
                            resultado['filas'].append({
                                'fecha': fecha_std,
                                'semana': row_semana,
                                'tipo_movimiento': tipo_mov or 'Salida',
                                'origen_obra': row_obra,
                                'obra': row_obra,
                                'equipo': equipo,
                                'economico': economico,
                                'salida': salida_val,
                                'litros': salida_val,
                                'ticket_ref': ticket_ref,
                                'observaciones': obs
                            })

            # 2. Parseo alternativo si no se extrajeron filas por tablas (Regex por líneas)
            if len(resultado['filas']) == 0 and full_text.strip():
                lines = full_text.split('\n')
                for line in lines:
                    line_s = line.strip()
                    m = re.match(
                        r'^(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s+(Salida|Entrada)?\s*([A-Za-z0-9áéíóúÁÉÍÓÚñÑ\-\s]+?)\s+([A-Za-z0-9áéíóúÁÉÍÓÚñÑ\-\s\(\)\.\/]+?)\s+(\d+(?:\.\d+)?)(?:\s+(.*))?$',
                        line_s, re.IGNORECASE
                    )
                    if m:
                        fecha_std = normalizar_fecha(m.group(1))
                        tipo_mov = m.group(2) or 'Salida'
                        obra_str = m.group(3).strip()
                        equipo_str = m.group(4).strip()
                        litros_val = float(m.group(5))
                        extra_obs = (m.group(6) or '').strip()
                        
                        try:
                            f_dt = datetime.datetime.strptime(fecha_std, '%Y-%m-%d').date()
                            row_semana = f_dt.isocalendar()[1]
                        except:
                            row_semana = resultado['semana']

                        if litros_val > 0 and not any(k in equipo_str.upper() for k in ['TOTAL', 'SUBTOTAL']):
                            resultado['filas'].append({
                                'fecha': fecha_std,
                                'semana': row_semana,
                                'tipo_movimiento': tipo_mov,
                                'origen_obra': obra_str,
                                'obra': obra_str,
                                'equipo': equipo_str,
                                'economico': '',
                                'salida': litros_val,
                                'litros': litros_val,
                                'ticket_ref': '',
                                'observaciones': extra_obs
                            })
                            
            # 3. Metadatos del encabezado
            sem_match = re.search(r'Semana\s*(?:No\.?)?:?\s*(\d+)', full_text, re.IGNORECASE)
            if sem_match:
                resultado['semana'] = int(sem_match.group(1))
                
            op_match = re.search(r'Operador\s*(?:Marimba|de\s*Marimba)?:?\s*([^\n\r]+)', full_text, re.IGNORECASE)
            if op_match:
                resultado['operador'] = op_match.group(1).strip()
                
            mar_match = re.search(r'Marimba:?\s*([^\n\r]+)', full_text, re.IGNORECASE)
            if mar_match:
                resultado['marimba'] = mar_match.group(1).strip()
                
            if 'APOLINAR' in full_text.upper():
                resultado['responsable'] = 'Apolinar'
            elif 'FRANCISCO JAVIER' in full_text.upper():
                resultado['responsable'] = 'Francisco Javier'
            elif 'CARREOLA' in full_text.upper() or 'DIEGO' in full_text.upper():
                resultado['responsable'] = 'Ing. Diego Carreola'

            # Detección de obra principal
            if 'ALFREDO DEL MAZO' in full_text.upper():
                resultado['obra_detectada'] = 'Alfredo del Mazo'
            elif 'MEXICO-TOLUCA' in full_text.upper() or 'MÉXICO-TOLUCA' in full_text.upper():
                resultado['obra_detectada'] = 'México - Toluca'
            elif 'BACHEO TOLUCA' in full_text.upper():
                resultado['obra_detectada'] = 'Bacheo Toluca'
            elif 'LERMA' in full_text.upper():
                resultado['obra_detectada'] = 'Lerma - Tres Marías'
            elif 'HUIXQUILUCAN' in full_text.upper():
                resultado['obra_detectada'] = 'Planta Huixquilucan'
            elif 'PEGASO' in full_text.upper():
                resultado['obra_detectada'] = 'Planta Pegaso'

    except Exception as e:
        print("Error en parse_bitacora_pdf:", e)
        
    return resultado

def validar_duplicados_semana(db_conn, semana, filas, obra_general_req=''):
    """
    Compara las filas extraídas del PDF contra los registros ya existentes en la base de datos,
    identificando posibles duplicados por coincidencia de Fecha, Equipo (económico o descripción), Litros y Obra.
    """
    if not filas or not db_conn:
        return filas, 0
        
    try:
        from psycopg2.extras import DictCursor
        cur = db_conn.cursor(cursor_factory=DictCursor)
        
        # Obtener todas las semanas presentes en las filas
        semanas_set = set()
        for f in filas:
            if f.get('semana'):
                semanas_set.add(str(f['semana']).strip())
        if semana:
            semanas_set.add(str(semana).replace('Semana ', '').replace('Semana', '').strip())
            
        cur.execute("""
            SELECT fecha, semana, equipo, equipo_economico, litros, obra_destino, origen, folio_conciliacion
            FROM diesel.consumos
            WHERE semana = ANY(%s) AND (estatus_revision IS NULL OR estatus_revision != 'RECHAZADO')
        """, (list(semanas_set),))
        existentes = cur.fetchall()
        cur.close()
        
        existing_list = []
        for row in existentes:
            f_str = str(row['fecha'] or '')
            eq_desc = str(row['equipo'] or '').upper().strip()
            eq_eco = str(row['equipo_economico'] or '').upper().strip()
            obra_str = str(row['obra_destino'] or '').strip()
            lts_val = float(row['litros'] or 0)
            existing_list.append({
                'fecha': f_str,
                'semana': str(row['semana']),
                'equipo_desc': eq_desc,
                'equipo_eco': eq_eco,
                'obra': obra_str,
                'litros': lts_val,
                'folio': row['folio_conciliacion']
            })
            
        duplicados_count = 0
        for fila in filas:
            f_fecha = str(fila.get('fecha', ''))
            f_eq_full = str(fila.get('equipo', '')).upper().strip()
            f_eco = str(fila.get('economico', '')).upper().strip()
            
            if ' - ' in f_eq_full:
                parts = f_eq_full.split(' - ')
                if not f_eco:
                    f_eco = parts[0].strip()
                    
            f_lts = float(fila.get('salida') or fila.get('litros') or 0)
            f_obra = str(fila.get('origen_obra') or fila.get('obra') or obra_general_req or '').strip()
            
            match_dup = None
            for ex in existing_list:
                # 1. Comparar Fecha y Litros
                if ex['fecha'] == f_fecha and abs(ex['litros'] - f_lts) < 0.01:
                    # 2. Comparar Equipo (por económico o por descripción)
                    eq_match = False
                    if f_eco and ex['equipo_eco'] and f_eco == ex['equipo_eco']:
                        eq_match = True
                    elif f_eco and f_eco in ex['equipo_desc']:
                        eq_match = True
                    elif ex['equipo_eco'] and ex['equipo_eco'] in f_eq_full:
                        eq_match = True
                    elif f_eq_full and ex['equipo_desc']:
                        if f_eq_full == ex['equipo_desc'] or f_eq_full in ex['equipo_desc'] or ex['equipo_desc'] in f_eq_full:
                            eq_match = True
                            
                    if eq_match:
                        match_dup = ex
                        break
                        
            if match_dup:
                fila['es_duplicado'] = True
                fila['folio_duplicado'] = match_dup['folio']
                obra_info = f" en obra '{match_dup['obra']}'" if match_dup['obra'] else ""
                fila['msj_duplicado'] = f"Ya registrado{obra_info} ({match_dup['folio']})"
                duplicados_count += 1
            else:
                fila['es_duplicado'] = False
                fila['folio_duplicado'] = ''
                fila['msj_duplicado'] = ''
                
        return filas, duplicados_count
    except Exception as e:
        print("Error en validar_duplicados_semana:", e)
        return filas, 0

def normalizar_fecha(fecha_str):
    try:
        m = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})', str(fecha_str))
        if m:
            day, month, year_str = int(m.group(1)), int(m.group(2)), m.group(3)
            year = int(year_str)
            if year < 100:
                year += 2000
            return f"{year:04d}-{month:02d}-{day:02d}"
    except Exception:
        pass
    return datetime.date.today().strftime('%Y-%m-%d')

