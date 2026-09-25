"""
Motor de Extracción, Ingesta y Balance Semanal de Transportes (Tanque Pegaso)
Proyecto Fénix - Transportes
"""

import io
import re
import datetime
from decimal import Decimal
import openpyxl

COSTO_DIESEL_DEFAULT = 27.00

def normalizar_equipo(eq_raw):
    """
    Normaliza el identificador del equipo para Transportes.
    Ej: 'ECO 3' -> 'ECO 03', 'ECO 14' -> 'ECO 14', 'PIPA BLANCA' -> 'PIPA BLANCA'
    """
    if not eq_raw:
        return 'SIN ASIGNAR'
    eq = str(eq_raw).strip().upper()
    # Mapear ECO X a ECO 0X
    m = re.match(r'^ECO\s*0?(\d+)$', eq)
    if m:
        num = int(m.group(1))
        return f"ECO {num:02d}"
    return eq

def _exec_db(db, sql, params=None):
    """
    Ejecuta SQL de forma transparente tanto en DbProxy como en conexión nativa psycopg2.
    """
    if hasattr(db, 'cursor'):
        cur = db.cursor()
        cur.execute(sql, params or ())
        return cur
    return db.execute(sql, params or ())

def extraer_bitacora_transportes_excel(file_source, filename=None, sheet_name=None):
    """
    Extrae los datos de la bitácora semanal de Transportes (Tanque Pegaso).
    Soporta ruta de archivo o bytes (io.BytesIO).
    Retorna un diccionario estructurado por semana con balances y partidas.
    """
    if isinstance(file_source, (bytes, bytearray)):
        wb = openpyxl.load_workbook(io.BytesIO(file_source), data_only=True)
    elif hasattr(file_source, 'read'):
        wb = openpyxl.load_workbook(file_source, data_only=True)
    else:
        wb = openpyxl.load_workbook(file_source, data_only=True)

    # Identificar hojas a procesar
    sheets_to_process = []
    if sheet_name and sheet_name in wb.sheetnames:
        sheets_to_process.append(sheet_name)
    else:
        # Buscar hojas con formato SEM XX o SEMANA XX
        for name in wb.sheetnames:
            s_upper = name.strip().upper()
            if re.match(r'^(SEM|SEMANA)\s*\d+', s_upper):
                sheets_to_process.append(name)
        # Si no encontró ninguna con nombre SEM, revisar si alguna hoja contiene 'DIESEL INICIAL'
        if not sheets_to_process:
            for name in wb.sheetnames:
                ws = wb[name]
                for r in range(1, min(15, ws.max_row + 1)):
                    row_txt = ' '.join(str(ws.cell(r, c).value or '').upper() for c in range(1, min(14, ws.max_column + 1)))
                    if 'DIESEL INICIAL' in row_txt or 'TANQUE PEGASO' in row_txt:
                        sheets_to_process.append(name)
                        break

    if not sheets_to_process and wb.sheetnames:
        sheets_to_process = [wb.sheetnames[0]]

    resultados = []

    for s_name in sheets_to_process:
        ws = wb[s_name]
        parsed = _procesar_hoja_transportes(ws, s_name, filename)
        if parsed and parsed.get('partidas'):
            resultados.append(parsed)

    return {
        'success': True,
        'archivo': filename,
        'total_hojas_procesadas': len(resultados),
        'hojas': resultados
    }

def _procesar_hoja_transportes(ws, sheet_name, filename=None):
    """
    Parsea una hoja individual de la bitácora.
    """
    semana = None
    empresa = 'JDJ'
    periodo = None
    diesel_inicial = 0.0
    diesel_final = 0.0

    # Extraer semana del nombre de la hoja si es posible
    m_sem = re.search(r'\d+', sheet_name)
    if m_sem:
        semana = m_sem.group(0)

    # 1. Escaneo de Metadatos en filas 1 a 9
    for r in range(1, min(10, ws.max_row + 1)):
        for c in range(1, min(14, ws.max_column + 1)):
            val = ws.cell(r, c).value
            if val is None:
                continue
            sval = str(val).strip().upper()

            # Semana
            if 'SEMANA' in sval and not semana:
                for dc in range(1, 6):
                    nxt = ws.cell(r, c + dc).value
                    if nxt is not None and str(nxt).strip().isdigit():
                        semana = str(nxt).strip()
                        break

            # Empresa
            if any(emp_kw in sval for emp_kw in ['TRITURADORA', 'J D J', 'JDJ', 'ROCA DURA']):
                empresa = str(val).strip()

            # Periodo
            if 'PERIODO' in sval and not periodo:
                for dc in range(1, 4):
                    nxt = ws.cell(r, c + dc).value
                    if nxt and len(str(nxt).strip()) > 3:
                        periodo = str(nxt).strip()
                        break

            # Diésel Inicial Semanal
            if 'DIESEL INICIAL' in sval and diesel_inicial == 0.0:
                for dc in range(1, 5):
                    nxt = ws.cell(r, c + dc).value
                    if isinstance(nxt, (int, float)) and nxt > 0:
                        diesel_inicial = float(nxt)
                        break

            # Diésel Final Semanal
            if 'DIESEL FINAL' in sval and diesel_final == 0.0:
                for dc in range(1, 5):
                    nxt = ws.cell(r, c + dc).value
                    if isinstance(nxt, (int, float)) and nxt > 0:
                        diesel_final = float(nxt)
                        break

    # Si no se encontró semana en celdas, verificar si se extrajo de la pestaña
    if not semana:
        semana = '37' # Fallback preventivo

    # 2. Localizar Fila de Encabezados
    header_row = None
    col_map = {}
    for r in range(5, min(14, ws.max_row + 1)):
        row_vals = {c: str(ws.cell(r, c).value or '').strip().upper() for c in range(1, min(15, ws.max_column + 1))}
        text_concat = ' '.join(row_vals.values())
        if 'FECHA' in text_concat and 'EQUIPO' in text_concat and 'LITROS' in text_concat:
            header_row = r
            for c, htext in row_vals.items():
                if 'FECHA' in htext: col_map['fecha'] = c
                elif 'EQUIPO' in htext: col_map['equipo'] = c
                elif 'OPERADOR' in htext: col_map['operador'] = c
                elif htext == 'CT' or 'CENTRO' in htext: col_map['ct'] = c
                elif htext == 'LITROS': col_map['litros'] = c
                elif 'INICIAL' in htext: col_map['cuenta_ini'] = c
                elif 'FINAL' in htext: col_map['cuenta_fin'] = c
                elif 'ESCANER' in htext: col_map['escaner'] = c
                elif htext == 'KM': col_map['km'] = c
                elif 'RECORRIDO' in htext: col_map['km_rec'] = c
                elif 'RENDIMIENTO' in htext: col_map['rendimiento'] = c
                elif 'VIEJO' in htext: col_map['flejes_viejos'] = c
                elif 'NUEVO' in htext: col_map['flejes_nuevos'] = c
            break

    if not header_row:
        # Fallback de columnas estándar
        header_row = 9
        col_map = {
            'fecha': 1, 'equipo': 2, 'operador': 3, 'ct': 4, 'litros': 5,
            'cuenta_ini': 6, 'cuenta_fin': 7, 'escaner': 8, 'km': 9,
            'km_rec': 10, 'rendimiento': 11, 'flejes_viejos': 12, 'flejes_nuevos': 13
        }

    # 3. Procesar Filas de Carga
    partidas = []
    modo_despacho_actual = 'TANQUE_PEGASO'
    factura_directa_actual = None

    for r in range(header_row + 1, ws.max_row + 1):
        vals = [ws.cell(r, c).value for c in range(1, min(15, ws.max_column + 1))]
        row_str = ' '.join(str(v).strip().upper() for v in vals if v is not None)
        if not row_str:
            continue

        # Detectar fin de tabla principal
        if any(stop_kw in row_str for stop_kw in ['TOTAL:', 'TOTAL ', 'LITROS SOBRANTES', 'ENTRADA DE COMBUSTIBLE']):
            # Si es fila de total o sección de entradas, detener procesamiento de consumos
            break

        # Detectar sección de cargas directas en gasolinera externa
        if any(dir_kw in row_str for dir_kw in ['CARGAS DIRECTAS', 'GASOLINAERA', 'GASOLINERA']):
            modo_despacho_actual = 'DESPACHO_DIRECTO'
            # Buscar si incluye folio de factura en la misma fila (ej: A-11292)
            for v in vals:
                v_s = str(v).strip()
                if re.search(r'[A-Z0-9]+-\d+', v_s):
                    factura_directa_actual = v_s
            continue

        # Obtener valores según mapeo
        fecha_val = ws.cell(r, col_map.get('fecha', 1)).value
        equipo_val = ws.cell(r, col_map.get('equipo', 2)).value
        operador_val = ws.cell(r, col_map.get('operador', 3)).value
        ct_val = ws.cell(r, col_map.get('ct', 4)).value
        litros_val = ws.cell(r, col_map.get('litros', 5)).value
        ini_val = ws.cell(r, col_map.get('cuenta_ini', 6)).value
        fin_val = ws.cell(r, col_map.get('cuenta_fin', 7)).value
        km_val = ws.cell(r, col_map.get('km', 9)).value
        km_rec_val = ws.cell(r, col_map.get('km_rec', 10)).value
        rend_val = ws.cell(r, col_map.get('rendimiento', 11)).value
        fleje_v_val = ws.cell(r, col_map.get('flejes_viejos', 12)).value
        fleje_n_val = ws.cell(r, col_map.get('flejes_nuevos', 13)).value

        # Fila vacía o sin equipo/litros
        if equipo_val is None and litros_val is None:
            continue

        try:
            litros_num = float(litros_val)
            if litros_num <= 0:
                continue
        except (ValueError, TypeError):
            continue

        # Formatear Fecha
        fecha_str = ''
        if isinstance(fecha_val, (datetime.datetime, datetime.date)):
            fecha_str = fecha_val.strftime('%Y-%m-%d')
        elif fecha_val:
            fecha_str = str(fecha_val).strip()[:10]

        # Determinar tipo de despacho
        tipo_despacho = modo_despacho_actual
        cuenta_ini_f = None
        cuenta_fin_f = None
        if ini_val is not None:
            try: cuenta_ini_f = float(ini_val)
            except: pass
        if fin_val is not None:
            try: cuenta_fin_f = float(fin_val)
            except: pass

        # Si tiene cuentalitros con diferencia coherente, es Tanque Pegaso
        if cuenta_ini_f is not None and cuenta_fin_f is not None and cuenta_fin_f > cuenta_ini_f:
            tipo_despacho = 'TANQUE_PEGASO'
        elif tipo_despacho == 'TANQUE_PEGASO' and (cuenta_ini_f is None or cuenta_fin_f is None):
            # Si no tiene cuentalitros y no estamos en sección directa, revisar si es despacho directo
            pass

        # KM y Rendimiento numéricos
        odometro = None
        if km_val is not None:
            try: odometro = float(km_val)
            except: pass

        km_rec = None
        if km_rec_val is not None:
            try: km_rec = float(km_rec_val)
            except: pass

        rendimiento = None
        if rend_val is not None:
            try: rendimiento = float(rend_val)
            except: pass

        eq_norm = normalizar_equipo(equipo_val)

        partidas.append({
            'fila_excel': r,
            'fecha': fecha_str,
            'semana': semana,
            'equipo_raw': str(equipo_val).strip() if equipo_val else '',
            'equipo_economico': eq_norm,
            'operador': str(operador_val).strip() if operador_val else '',
            'centro_trabajo': str(ct_val).strip() if ct_val else 'FLOTILLA TRANSPORTES',
            'litros': round(litros_num, 3),
            'costo_por_litro': COSTO_DIESEL_DEFAULT,
            'importe_total': round(litros_num * COSTO_DIESEL_DEFAULT, 2),
            'cuentalitros_inicial': cuenta_ini_f,
            'cuentalitros_final': cuenta_fin_f,
            'odometro_km': odometro,
            'km_recorridos': km_rec,
            'rendimiento_km_l': rendimiento,
            'flejes_viejos': str(fleje_v_val).strip() if fleje_v_val is not None else None,
            'flejes_nuevos': str(fleje_n_val).strip() if fleje_n_val is not None else None,
            'tipo_despacho': tipo_despacho,
            'factura_referencia': factura_directa_actual if tipo_despacho == 'DESPACHO_DIRECTO' else None
        })

    # 4. Cálculo de Balances e Indicadores del Tanque Pegaso
    cargas_tanque = [p for p in partidas if p['tipo_despacho'] == 'TANQUE_PEGASO']
    cargas_directas = [p for p in partidas if p['tipo_despacho'] == 'DESPACHO_DIRECTO']

    litros_tanque = sum(p['litros'] for p in cargas_tanque)
    litros_directo = sum(p['litros'] for p in cargas_directas)
    litros_totales = litros_tanque + litros_directo

    cuentalitros_min = None
    cuentalitros_max = None
    if cargas_tanque:
        inis = [p['cuentalitros_inicial'] for p in cargas_tanque if p['cuentalitros_inicial'] is not None and p['cuentalitros_inicial'] > 0]
        fins = [p['cuentalitros_final'] for p in cargas_tanque if p['cuentalitros_final'] is not None and p['cuentalitros_final'] > 0]
        if inis: cuentalitros_min = min(inis)
        if fins: cuentalitros_max = max(fins)

    # Si diesel final no vino en cabecera o dio 0, calcularlo matemáticamente
    if diesel_final == 0.0 and diesel_inicial > 0:
        diesel_final = round(diesel_inicial - litros_tanque, 4)

    # 5. Agrupación por Vehículo (Consumo semanal)
    vehiculos_resumen = {}
    for p in partidas:
        eq = p['equipo_economico']
        if eq not in vehiculos_resumen:
            vehiculos_resumen[eq] = {
                'equipo': eq,
                'cargas_count': 0,
                'litros_tanque': 0.0,
                'litros_directo': 0.0,
                'litros_totales': 0.0,
                'importe_total': 0.0,
                'operadores': set(),
                'odometro_max': 0.0,
                'km_recorridos_total': 0.0
            }
        v = vehiculos_resumen[eq]
        v['cargas_count'] += 1
        if p['tipo_despacho'] == 'TANQUE_PEGASO':
            v['litros_tanque'] += p['litros']
        else:
            v['litros_directo'] += p['litros']
        v['litros_totales'] += p['litros']
        v['importe_total'] += p['importe_total']
        if p['operador']:
            v['operadores'].add(p['operador'])
        if p['odometro_km'] and p['odometro_km'] > v['odometro_max']:
            v['odometro_max'] = p['odometro_km']
        if p['km_recorridos']:
            v['km_recorridos_total'] += p['km_recorridos']

    # Convertir sets a listas para JSON serializable
    lista_vehiculos = []
    for k, v in vehiculos_resumen.items():
        v['litros_tanque'] = round(v['litros_tanque'], 2)
        v['litros_directo'] = round(v['litros_directo'], 2)
        v['litros_totales'] = round(v['litros_totales'], 2)
        v['importe_total'] = round(v['importe_total'], 2)
        v['operadores'] = list(v['operadores'])
        lista_vehiculos.append(v)

    # Ordenar por mayor consumo
    lista_vehiculos.sort(key=lambda x: x['litros_totales'], reverse=True)

    consumo_tanque_neto = round(litros_tanque, 2)
    delta_cuentalitros = round(cuentalitros_max - cuentalitros_min, 2) if (cuentalitros_min and cuentalitros_max) else round(litros_tanque, 2)
    dif_tanque_bomba = round(abs(consumo_tanque_neto - delta_cuentalitros), 2)
    cuadra_100 = dif_tanque_bomba < 0.1
    factura_ref = cargas_directas[0].get('factura_directa', '') if cargas_directas else ''

    balance = {
        'semana': str(semana),
        'empresa': empresa,
        'periodo': periodo,
        'diesel_inicial': round(diesel_inicial, 2),
        'diesel_final': round(diesel_final, 2),
        'diesel_inicial_tanque': round(diesel_inicial, 2),
        'diesel_final_tanque': round(diesel_final, 2),
        'consumo_tanque_neto': consumo_tanque_neto,
        'litros_salida_tanque': consumo_tanque_neto,
        'cuenta_litros_inicial': cuentalitros_min,
        'cuenta_litros_final': cuentalitros_max,
        'cuentalitros_inicial': cuentalitros_min,
        'cuentalitros_final': cuentalitros_max,
        'delta_cuentalitros': delta_cuentalitros,
        'salida_bomba_registrada': delta_cuentalitros,
        'litros_bomba_cuentalitros': delta_cuentalitros,
        'diferencia_tanque_vs_bomba': dif_tanque_bomba,
        'cuadra_100': cuadra_100,
        'despacho_directo_litros': round(litros_directo, 2),
        'litros_despacho_directo': round(litros_directo, 2),
        'despacho_directo_cargas': len(cargas_directas),
        'total_cargas_directas': len(cargas_directas),
        'factura_directa_ref': factura_ref,
        'factura_despacho_directo': factura_ref,
        'total_litros_semana': round(litros_totales, 2),
        'litros_totales_cargados': round(litros_totales, 2),
        'costo_promedio_litro': COSTO_DIESEL_DEFAULT,
        'costo_total': round(litros_totales * COSTO_DIESEL_DEFAULT, 2),
        'costo_total_semana': round(litros_totales * COSTO_DIESEL_DEFAULT, 2),
        'total_partidas': len(partidas),
        'total_vehiculos': len(lista_vehiculos)
    }

    return {
        'hoja': sheet_name,
        'sheet_name': sheet_name,
        'nombre_hoja': sheet_name,
        'balance': balance,
        'partidas': partidas,
        'resumen_vehiculos': lista_vehiculos
    }

def generar_propuesta_autorizaciones(db, semana_actual, resumen_vehiculos):
    """
    Calcula el histórico de consumos por vehículo en semanas previas
    y formula una propuesta matemática de autorización semanal recomendada.
    """
    propuestas = []

    for v in resumen_vehiculos:
        eq = v['equipo']
        litros_actual = v['litros_totales']

        # Consultar histórico en transportes.consumos_diesel
        cur = _exec_db(db, '''
            SELECT semana, SUM(litros) as total_litros, COUNT(*) as cargas
            FROM transportes.consumos_diesel
            WHERE (equipo_economico = %s OR equipo = %s)
              AND semana != %s
            GROUP BY semana
            ORDER BY semana DESC
            LIMIT 8;
        ''', (eq, eq, str(semana_actual)))

        historico_filas = cur.fetchall()
        semanas_registradas = len(historico_filas)
        total_historico_lts = sum(float(r[1]) for r in historico_filas)
        promedio_historico = round(total_historico_lts / semanas_registradas, 2) if semanas_registradas > 0 else round(litros_actual, 2)

        # Regla de propuesta de autorización:
        # Se sugiere un tope basado en el promedio histórico con un margen del 10%
        # redondeado al múltiplo de 50 litros superior para holgura operativa.
        base_sugerida = promedio_historico if promedio_historico > 0 else litros_actual
        margen = base_sugerida * 1.10
        # Redondear a múltiplo de 50 litros (mínimo 100 L)
        tope_propuesto = max(100.0, round(margen / 50.0) * 50.0)

        # Semáforo de comparación de la semana actual contra el histórico
        if promedio_historico > 0:
            delta_pct = round(((litros_actual - promedio_historico) / promedio_historico) * 100.0, 1)
        else:
            delta_pct = 0.0

        if delta_pct > 25.0:
            semaforo = 'ROJO'
            recomendacion = f'Consumo excedió el promedio por +{delta_pct}%. Auditar recorridos y flejes.'
        elif delta_pct > 10.0:
            semaforo = 'AMARILLO'
            recomendacion = f'Consumo ligeramente superior (+{delta_pct}%). Revisar rutas adicionales.'
        else:
            semaforo = 'VERDE'
            recomendacion = 'Consumo dentro de parámetros operativos habituales.'

        propuestas.append({
            'semana': semana_actual,
            'equipo': eq,
            'vehiculo': eq,
            'litros_semana_actual': litros_actual,
            'consumo_semana_litros': litros_actual,
            'promedio_historico_litros': promedio_historico,
            'semanas_historial': semanas_registradas,
            'delta_pct': delta_pct,
            'variacion_pct': delta_pct,
            'tope_propuesto_litros': tope_propuesto,
            'litros_autorizados_propuestos': tope_propuesto,
            'costo_propuesto_mxn': round(tope_propuesto * COSTO_DIESEL_DEFAULT, 2),
            'semaforo': semaforo,
            'recomendacion': recomendacion,
            'observacion': recomendacion,
            'operadores': ', '.join(v.get('operadores', [])) if isinstance(v.get('operadores'), (list, set)) else str(v.get('operadores', '')),
            'odometro_max': v.get('odometro_max', 0)
        })

    # Ordenar por tope propuesto descendente
    propuestas.sort(key=lambda x: x['tope_propuesto_litros'], reverse=True)
    return propuestas

def inyectar_bitacora_transportes_bd(db, datos_hoja, usuario='admin'):
    """
    Inyecta el balance semanal y las partidas de diésel en la base de datos PostgreSQL.
    Garantiza idempotencia total: no genera duplicados gracias a la clave única.
    """
    balance = datos_hoja['balance']
    partidas = datos_hoja['partidas']
    resumen_vehiculos = datos_hoja['resumen_vehiculos']
    propuestas = datos_hoja.get('propuesta_autorizaciones') or generar_propuesta_autorizaciones(db, balance['semana'], resumen_vehiculos)

    # 1. Guardar o actualizar balance semanal en transportes.balance_tanque_semanal
    import json
    resumen_json = json.dumps(resumen_vehiculos)
    propuesta_json = json.dumps(propuestas)

    cur = _exec_db(db, '''
        INSERT INTO transportes.balance_tanque_semanal (
            empresa, semana, periodo, diesel_inicial, diesel_final,
            cuentalitros_inicial, cuentalitros_final, litros_tanque,
            litros_despacho_directo, litros_totales, costo_por_litro,
            costo_total, archivo_origen, detalles_vehiculos,
            propuesta_autorizaciones, usuario_registro, updated_at
        ) VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s,
            %s, %s, NOW()
        )
        ON CONFLICT (semana, empresa) DO UPDATE SET
            periodo = EXCLUDED.periodo,
            diesel_inicial = EXCLUDED.diesel_inicial,
            diesel_final = EXCLUDED.diesel_final,
            cuentalitros_inicial = EXCLUDED.cuentalitros_inicial,
            cuentalitros_final = EXCLUDED.cuentalitros_final,
            litros_tanque = EXCLUDED.litros_tanque,
            litros_despacho_directo = EXCLUDED.litros_despacho_directo,
            litros_totales = EXCLUDED.litros_totales,
            costo_total = EXCLUDED.costo_total,
            detalles_vehiculos = EXCLUDED.detalles_vehiculos,
            propuesta_autorizaciones = EXCLUDED.propuesta_autorizaciones,
            updated_at = NOW()
        RETURNING id;
    ''', (
        balance['empresa'], str(balance['semana']), balance['periodo'],
        balance['diesel_inicial_tanque'], balance['diesel_final_tanque'],
        balance['cuentalitros_inicial'], balance['cuentalitros_final'],
        balance['litros_salida_tanque'], balance['litros_despacho_directo'],
        balance['litros_totales_cargados'], balance['costo_promedio_litro'],
        balance['costo_total'], balance.get('archivo_origen', ''),
        resumen_json, propuesta_json, usuario
    ))
    row_bal = cur.fetchone()
    balance_id = row_bal[0] if row_bal else None

    # 2. Inyectar partidas individuales en transportes.consumos_diesel
    insertados = 0
    actualizados = 0

    for idx, p in enumerate(partidas, start=1):
        folio = f"CP-S{balance['semana']}-{idx:03d}"
        origen = 'Tanque Pegaso' if p['tipo_despacho'] == 'TANQUE_PEGASO' else 'Gasolinera Directa'
        obs = f"Fila {p['fila_excel']} Bitácora Tanque Pegaso S{balance['semana']}"
        if p['equipo_raw'] and p['equipo_raw'] != p['equipo_economico']:
            obs += f" | Original: {p['equipo_raw']}"

        cur_ins = _exec_db(db, '''
            INSERT INTO transportes.consumos_diesel (
                folio_conciliacion, fecha, semana, origen, obra_destino,
                responsable_unidad, equipo, equipo_economico, litros,
                costo_por_litro, importe_total, odometro_km,
                tipo_despacho, cuentalitros_inicial, cuentalitros_final,
                flejes_viejos, flejes_nuevos, factura_referencia,
                km_recorridos, rendimiento_km_l, observaciones,
                usuario_captura, estatus_revision, created_at
            ) VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, 'APROBADO', NOW()
            )
            ON CONFLICT (folio_conciliacion) DO UPDATE SET
                fecha = EXCLUDED.fecha,
                semana = EXCLUDED.semana,
                origen = EXCLUDED.origen,
                obra_destino = EXCLUDED.obra_destino,
                responsable_unidad = EXCLUDED.responsable_unidad,
                equipo = EXCLUDED.equipo,
                equipo_economico = EXCLUDED.equipo_economico,
                litros = EXCLUDED.litros,
                costo_por_litro = EXCLUDED.costo_por_litro,
                importe_total = EXCLUDED.importe_total,
                odometro_km = EXCLUDED.odometro_km,
                tipo_despacho = EXCLUDED.tipo_despacho,
                cuentalitros_inicial = EXCLUDED.cuentalitros_inicial,
                cuentalitros_final = EXCLUDED.cuentalitros_final,
                flejes_viejos = EXCLUDED.flejes_viejos,
                flejes_nuevos = EXCLUDED.flejes_nuevos,
                factura_referencia = EXCLUDED.factura_referencia,
                km_recorridos = EXCLUDED.km_recorridos,
                rendimiento_km_l = EXCLUDED.rendimiento_km_l,
                observaciones = EXCLUDED.observaciones
            RETURNING (xmax = 0) AS es_nuevo;
        ''', (
            folio, p['fecha'], str(balance['semana']), origen, p['centro_trabajo'],
            p['operador'], p['equipo_economico'], p['equipo_economico'], p['litros'],
            p['costo_por_litro'], p['importe_total'], p['odometro_km'],
            p['tipo_despacho'], p['cuentalitros_inicial'], p['cuentalitros_final'],
            p['flejes_viejos'], p['flejes_nuevos'], p['factura_referencia'],
            p['km_recorridos'], p['rendimiento_km_l'], obs,
            usuario
        ))
        res = cur_ins.fetchone()
        if res and res[0]:
            insertados += 1
        else:
            actualizados += 1

    db.commit()

    return {
        'balance_id': balance_id,
        'semana': balance['semana'],
        'total_partidas': len(partidas),
        'insertados': insertados,
        'actualizados': actualizados,
        'total_vehiculos': len(resumen_vehiculos)
    }
