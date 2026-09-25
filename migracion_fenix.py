# -*- coding: utf-8 -*-
"""
SISTEMA FENIX -- Script de Migracion ETL v1.0
==============================================
Lee los archivos Excel de la empresa y los inyecta en fenix.db
Orden: Catalogos -> Horas -> Diesel -> Gasolina -> Acarreos

Uso: python migracion_fenix.py
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import sqlite3
import pandas as pd
import numpy as np
import os
import re
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "fenix.db")

# === Archivos Fuente ===
DIESEL_MASTER   = os.path.join(BASE_DIR, "GC-COMB-3.1_Excel_Maestro_Control_Combustible_Grupo_Trujano_FINAL_V2.xlsx")
GAS_CONSUMOS    = os.path.join(BASE_DIR, "gasolina", "CONSUMOS  DE GASOLINA SEMANALES GT.xlsx")
GAS_PROVISIONAL = os.path.join(BASE_DIR, "gasolina", "CONTROL JDJ PROVISIONAL semana 27.xlsx")
ACARREOS_MASTER = os.path.join(BASE_DIR, "acarreos y Fresado", "GC-MAT-1.0_Maestro_Consolidado_V12.xlsx")

VERDE = "\033[92m"; ROJO = "\033[91m"; CYAN = "\033[96m"; BOLD = "\033[1m"; RESET = "\033[0m"
def ok(m):   print(f"  {VERDE}+ {m}{RESET}")
def err(m):  print(f"  {ROJO}! {m}{RESET}")
def info(m): print(f"  {CYAN}> {m}{RESET}")

# =============================================================================
# HELPERS
# =============================================================================
def get_or_create(cur, table, name_col, name_val, extra=None):
    """Obtiene el ID de un registro por nombre, o lo crea si no existe."""
    cur.execute(f"SELECT id FROM {table} WHERE {name_col} = ?", (str(name_val).strip(),))
    row = cur.fetchone()
    if row:
        return row[0]
    if extra:
        cols = ", ".join([name_col] + list(extra.keys()))
        vals = [str(name_val).strip()] + list(extra.values())
        ph   = ", ".join(["?"] * len(vals))
        cur.execute(f"INSERT INTO {table} ({cols}) VALUES ({ph})", vals)
    else:
        cur.execute(f"INSERT INTO {table} ({name_col}) VALUES (?)", (str(name_val).strip(),))
    return cur.lastrowid

def clean(val):
    """Limpia un valor de pandas para guardarlo en SQLite."""
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return None
    if isinstance(val, pd.Timestamp):
        return val.strftime('%Y-%m-%d')
    return str(val).strip()

def to_num(val):
    """Convierte a numero, devuelve None si no es posible."""
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return None
    try:
        return float(str(val).replace(',','').replace('$','').strip())
    except:
        return None

def iso_week(fecha_str):
    """Retorna el numero de semana ISO de una fecha string YYYY-MM-DD."""
    try:
        return datetime.strptime(fecha_str[:10], '%Y-%m-%d').isocalendar()[1]
    except:
        return None

# =============================================================================
# FASE 1A: Catalogos de Diesel (Maquinaria_Inventario + Catalogos)
# =============================================================================
def migrar_catalogos_diesel(conn):
    info("Leyendo Maquinaria_Inventario...")
    df_inv = pd.read_excel(DIESEL_MASTER, sheet_name='Maquinaria_Inventario')

    # Columnas: Numero, Unidad, Dueno, Marca, Modelo, Anio, No.Serie,
    #           Rendimiento Nuevo, Unidad de Medida, Edad, Rendimiento Ajustado, Economico
    df_inv.columns = [str(c).strip() for c in df_inv.columns]

    info("Leyendo tabla de asignacion Obra/Operador desde Catalogos...")
    # La tabla de asignacion esta en columnas V-Y (indices 21-24) a partir de fila 2
    df_cat = pd.read_excel(DIESEL_MASTER, sheet_name='Catalogos', header=None, usecols="V:Z")
    # Renombrar con la fila 2 como header
    df_cat.columns = ['tipo_equipo','num_eco','obra_asignada','operador','obra_folio']
    df_cat = df_cat.iloc[2:].reset_index(drop=True)  # Saltar encabezados
    df_cat = df_cat.dropna(subset=['num_eco'])
    df_cat['num_eco'] = df_cat['num_eco'].astype(str).str.strip()

    cur = conn.cursor()
    insertados = 0; actualizados = 0

    for _, row in df_inv.iterrows():
        eco       = clean(row.get('Económico') or row.get('Economico'))
        if not eco or eco == 'None': continue

        descripcion    = clean(row.get('Unidad', ''))
        marca          = clean(row.get('Marca', ''))
        modelo         = clean(row.get('Modelo', ''))
        tipo_equipo    = descripcion  # El tipo viene del nombre
        rend_nuevo     = to_num(row.get('Rendimiento Nuevo'))
        unidad_medida  = clean(row.get('Unidad de Medida', 'L/h'))

        tipo_rend = 'horas'
        if unidad_medida and 'km' in str(unidad_medida).lower():
            tipo_rend = 'kilometros'

        desc_completa = f"{descripcion} {marca} {modelo}".strip()

        # Buscar obra asignada desde Catalogos
        match = df_cat[df_cat['num_eco'] == eco]
        obra_nombre = None
        operador_asig = None
        if not match.empty:
            obra_nombre   = clean(match.iloc[0].get('obra_asignada'))
            operador_asig = clean(match.iloc[0].get('operador'))

        # Obtener obra_id si existe
        obra_id = None
        if obra_nombre and obra_nombre not in ('None', 'nan', 'NaN'):
            cur.execute("SELECT id FROM fenix_obras WHERE nombre = ?", (obra_nombre,))
            r = cur.fetchone()
            if r:
                obra_id = r[0]
            else:
                # Crear obra si no existe
                cur.execute("INSERT OR IGNORE INTO fenix_obras (codigo, nombre) VALUES (?,?)",
                            (obra_nombre[:3].upper().replace(' ',''), obra_nombre))
                cur.execute("SELECT id FROM fenix_obras WHERE nombre = ?", (obra_nombre,))
                r = cur.fetchone()
                if r: obra_id = r[0]

        # Insertar o actualizar equipo
        cur.execute("SELECT id FROM fenix_equipos WHERE numero_economico = ?", (eco,))
        existing = cur.fetchone()
        if existing:
            cur.execute("""UPDATE fenix_equipos
                           SET descripcion=?, tipo_equipo=?, rendimiento_base=?, obra_id=?
                           WHERE numero_economico=?""",
                        (desc_completa, tipo_equipo, rend_nuevo, obra_id, eco))
            actualizados += 1
        else:
            cur.execute("""INSERT INTO fenix_equipos
                           (numero_economico, descripcion, tipo_equipo, tipo_combustible, tipo_rendimiento, rendimiento_base, obra_id)
                           VALUES (?,?,?,?,?,?,?)""",
                        (eco, desc_completa, tipo_equipo, 'Diesel', tipo_rend, rend_nuevo, obra_id))
            insertados += 1

    conn.commit()
    ok(f"Equipos Diesel: {insertados} nuevos, {actualizados} actualizados con obra y rendimiento base.")
    return True

# =============================================================================
# FASE 1B: Catalogos de Gasolina (placas + centros de trabajo)
# =============================================================================
def migrar_catalogos_gasolina(conn):
    cur = conn.cursor()
    insertados = 0

    # Leer hoja UT del archivo de consumos (Huixquilucan)
    info("Leyendo catalogo de vehiculos Gasolina (CONSUMOS GT - Hoja UT)...")
    df_gas = pd.read_excel(GAS_CONSUMOS, sheet_name='UT', header=None)
    # Fila 2 tiene: RESPONSABLE | UNIDAD | PLACAS | CENTRO DE TRABAJO | IMPORTE...
    # Datos desde fila 3
    df_data = df_gas.iloc[2:].reset_index(drop=True)
    df_data.columns = range(len(df_data.columns))

    for _, row in df_data.iterrows():
        placa       = clean(row.get(2))   # Col C: PLACAS
        unidad_desc = clean(row.get(1))   # Col B: UNIDAD
        centro      = clean(row.get(3))   # Col D: CENTRO DE TRABAJO
        responsable = clean(row.get(0))   # Col A: RESPONSABLE

        if not placa or placa in ('None','nan','PLACAS','PLACA'):
            continue
        if not re.match(r'[A-Z0-9]{3,10}', placa.replace('-','').replace(' ','')):
            continue

        # Buscar o crear centro de trabajo como obra
        obra_id = None
        if centro and centro not in ('None','nan'):
            centro_limpio = centro.strip().upper()
            cur.execute("SELECT id FROM fenix_obras WHERE upper(nombre) = ?", (centro_limpio,))
            r = cur.fetchone()
            if r:
                obra_id = r[0]
            else:
                codigo = re.sub(r'[^A-Z]', '', centro_limpio)[:4]
                cur.execute("INSERT OR IGNORE INTO fenix_obras (codigo, nombre) VALUES (?,?)",
                            (codigo, centro.strip()))
                cur.execute("SELECT id FROM fenix_obras WHERE upper(nombre) = ?", (centro_limpio,))
                r = cur.fetchone()
                if r: obra_id = r[0]

        cur.execute("SELECT id FROM fenix_equipos WHERE numero_economico = ?", (placa,))
        if not cur.fetchone():
            desc = f"{unidad_desc or 'Vehiculo'} {placa}"
            cur.execute("""INSERT OR IGNORE INTO fenix_equipos
                           (numero_economico, descripcion, tipo_equipo, tipo_combustible, tipo_rendimiento, obra_id)
                           VALUES (?,?,?,?,?,?)""",
                        (placa, desc, unidad_desc or 'Vehiculo', 'Gasolina', 'kilometros', obra_id))
            insertados += 1
        elif obra_id:
            cur.execute("UPDATE fenix_equipos SET obra_id=? WHERE numero_economico=? AND obra_id IS NULL",
                        (obra_id, placa))

    conn.commit()
    ok(f"Vehiculos Gasolina (Huixquilucan): {insertados} nuevos.")

    # Leer el provisional JDJ (Levet) para agregar placas adicionales
    info("Leyendo catalogo adicional de vehiculos Gasolina (JDJ Provisional - Levet)...")
    df_prov = pd.read_excel(GAS_PROVISIONAL, sheet_name='JUNIO 2026', header=None)
    # Fila 3: TICKET | FECHA | UNID. | KM | CONDUCTOR | OBRA | LTS | PRECIO | IMPORTE
    df_prov_data = df_prov.iloc[3:].reset_index(drop=True)
    df_prov_data.columns = range(len(df_prov_data.columns))

    nuevos_levet = 0
    for _, row in df_prov_data.iterrows():
        placa = clean(row.get(3))   # Col D: UNID.
        obra_n= clean(row.get(6))   # Col G: OBRA
        cond  = clean(row.get(5))   # Col F: CONDUCTOR

        if not placa or placa in ('None','nan','UNID.'):
            continue

        obra_id = None
        if obra_n and obra_n not in ('None','nan'):
            cur.execute("SELECT id FROM fenix_obras WHERE upper(nombre) = ?", (obra_n.strip().upper(),))
            r = cur.fetchone()
            if r: obra_id = r[0]

        cur.execute("SELECT id FROM fenix_equipos WHERE numero_economico = ?", (placa,))
        if not cur.fetchone():
            cur.execute("""INSERT OR IGNORE INTO fenix_equipos
                           (numero_economico, descripcion, tipo_equipo, tipo_combustible, tipo_rendimiento, obra_id)
                           VALUES (?,?,?,?,?,?)""",
                        (placa, f"Vehiculo {placa}", 'Vehiculo', 'Gasolina', 'kilometros', obra_id))
            nuevos_levet += 1

    conn.commit()
    ok(f"Vehiculos Gasolina (Levet): {nuevos_levet} nuevos.")

# =============================================================================
# FASE 1C: Horas de Trabajo (Captura_Horas)
# =============================================================================
def migrar_horas_trabajo(conn):
    info("Leyendo Captura_Horas...")
    df = pd.read_excel(DIESEL_MASTER, sheet_name='Captura_Horas', header=None)
    # Fila 2: ID Reporte | Fecha | Obra | Maquinaria | No.Economico | Operador | Horas | Actividad | Rend.Esperado | Semana
    df_data = df.iloc[2:].reset_index(drop=True)
    df_data.columns = ['folio','fecha','obra','maquinaria','eco','operador','horas','actividad','rend_esp','semana']

    cur = conn.cursor(); insertados = 0; errores = 0

    for _, row in df_data.iterrows():
        folio  = clean(row['folio'])
        fecha  = clean(row['fecha'])
        horas  = to_num(row['horas'])
        eco    = clean(row['eco'])

        if not folio or folio in ('None','nan'): continue
        if not horas or horas <= 0: continue

        fecha_str = fecha[:10] if fecha and len(fecha) >= 10 else None

        # Buscar equipo por numero economico
        equipo_id = None
        if eco and eco not in ('None','nan','S/N (WIRGENT)'):
            cur.execute("SELECT id FROM fenix_equipos WHERE numero_economico = ?", (eco,))
            r = cur.fetchone()
            if r: equipo_id = r[0]

        # Buscar obra
        obra_id = None
        obra_n = clean(row['obra'])
        if obra_n and obra_n not in ('None','nan'):
            cur.execute("SELECT id FROM fenix_obras WHERE nombre LIKE ?", (f"%{obra_n}%",))
            r = cur.fetchone()
            if r: obra_id = r[0]

        semana_n = to_num(row['semana'])
        sem_int = int(semana_n) if semana_n else iso_week(fecha_str)

        try:
            cur.execute("""INSERT OR IGNORE INTO fenix_horas_trabajo
                           (folio, fecha, semana, obra_id, equipo_id, operador, horas_trabajadas, actividad_principal)
                           VALUES (?,?,?,?,?,?,?,?)""",
                        (folio, fecha_str, sem_int, obra_id, equipo_id,
                         clean(row['operador']), horas, clean(row['actividad'])))
            if cur.rowcount > 0: insertados += 1
        except Exception as e:
            errores += 1

    conn.commit()
    ok(f"Horas de Trabajo: {insertados} registros insertados. ({errores} omitidos/duplicados)")

# =============================================================================
# FASE 1D: Movimientos Diesel historicos (Captura_Obra -> CONSUMO V2)
# =============================================================================
def migrar_diesel_historico(conn):
    info("Leyendo Captura_Obra (historico diesel)...")
    df = pd.read_excel(DIESEL_MASTER, sheet_name='Captura_Obra', header=None)
    # Fila 3: Fecha | Obra | Fuente | Equipo | Economico | LitrosRecibidos | Costo/L | Importe | Actividad | Incidencia | Obs | _ | Semana | Folio
    df_data = df.iloc[3:].reset_index(drop=True)
    df_data.columns = ['fecha','obra','fuente','equipo','eco','litros','costo_l','importe',
                        'actividad','incidencia','obs','_','semana','folio']

    cur = conn.cursor(); insertados = 0; errores = 0

    for _, row in df_data.iterrows():
        fecha   = clean(row['fecha'])
        litros  = to_num(row['litros'])
        costo_l = to_num(row['costo_l'])
        folio   = clean(row['folio'])

        if not fecha or fecha in ('None','nan'): continue
        if not litros or litros <= 0: continue

        fecha_str = fecha[:10] if fecha and len(fecha) >= 10 else None

        fuente  = clean(row['fuente']) or 'Marimba M-01'
        equipo_n= clean(row['equipo']) or ''
        eco     = clean(row['eco'])
        obra_n  = clean(row['obra'])
        semana_n= to_num(row['semana'])
        sem_int = int(semana_n) if semana_n else iso_week(fecha_str)

        # Resolver equipo_id (preferir por Economico, luego por nombre)
        equipo_id = None
        if eco and eco not in ('None','nan'):
            cur.execute("SELECT id FROM fenix_equipos WHERE numero_economico = ?", (eco,))
            r = cur.fetchone()
            if r: equipo_id = r[0]
        if not equipo_id and equipo_n:
            cur.execute("SELECT id FROM fenix_equipos WHERE descripcion LIKE ?", (f"%{equipo_n[:8]}%",))
            r = cur.fetchone()
            if r: equipo_id = r[0]

        # Resolver obra_id
        obra_id = None
        if obra_n and obra_n not in ('None','nan'):
            cur.execute("SELECT id FROM fenix_obras WHERE nombre LIKE ?", (f"%{obra_n}%",))
            r = cur.fetchone()
            if r: obra_id = r[0]

        # Mapeo V2: Fuente -> origen_tipo/nombre, Equipo -> destino
        origen_tipo  = 'Marimba'
        origen_nombre= fuente
        if 'pegaso' in fuente.lower() or 'tanque' in fuente.lower():
            origen_tipo = 'Tanque'
        elif 'marimba' in fuente.lower():
            origen_tipo = 'Marimba'
        elif 'gasolinera' in fuente.lower() or 'gas' in fuente.lower():
            origen_tipo = 'Gasolinera'
        elif 'bidon' in fuente.lower() or 'bidon' in fuente.lower():
            origen_tipo = 'Bidon'

        destino_nombre = eco if eco and eco not in ('None','nan') else equipo_n

        try:
            cur.execute("""INSERT INTO fenix_movimientos_combustible
                           (tipo_movimiento, fecha, semana, origen_tipo, origen_nombre,
                            destino_tipo, destino_nombre, equipo_id, obra_id,
                            litros, precio_unitario, folio_vale, observaciones)
                           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        ('CONSUMO', fecha_str, sem_int,
                         origen_tipo, origen_nombre,
                         'Equipo', destino_nombre,
                         equipo_id, obra_id,
                         litros, costo_l or 0,
                         folio, clean(row['actividad'])))
            insertados += 1
        except Exception as e:
            errores += 1

    conn.commit()
    ok(f"Consumos Diesel (Captura_Obra): {insertados} transacciones insertadas. ({errores} omitidas)")

# =============================================================================
# FASE 1E: Gasolina Levet (JDJ Provisional -> CONSUMO)
# =============================================================================
def migrar_gasolina_levet(conn):
    info("Leyendo Gasolina Levet (JDJ Provisional)...")
    df = pd.read_excel(GAS_PROVISIONAL, sheet_name='JUNIO 2026', header=None)
    df_data = df.iloc[3:].reset_index(drop=True)
    # Col: _ | TICKET | FECHA | UNID. | KM | CONDUCTOR | OBRA | LTS | PRECIO | IMPORTE
    df_data.columns = range(len(df_data.columns))

    cur = conn.cursor(); insertados = 0; errores = 0

    for _, row in df_data.iterrows():
        ticket = clean(row.get(1))
        fecha  = clean(row.get(2))
        placa  = clean(row.get(3))
        litros = to_num(row.get(7))
        precio = to_num(row.get(8))
        importe= to_num(row.get(9))
        obra_n = clean(row.get(6))
        km     = to_num(row.get(4))

        if not placa or placa in ('None','nan','UNID.'): continue
        if not litros or litros <= 0: continue

        fecha_str = fecha[:10] if fecha and len(fecha) >= 10 else None
        sem_int   = iso_week(fecha_str)

        equipo_id = None
        cur.execute("SELECT id FROM fenix_equipos WHERE numero_economico = ?", (placa,))
        r = cur.fetchone()
        if r: equipo_id = r[0]

        obra_id = None
        if obra_n and obra_n not in ('None','nan'):
            cur.execute("SELECT id FROM fenix_obras WHERE upper(nombre) LIKE ?", (f"%{obra_n.upper()[:10]}%",))
            r = cur.fetchone()
            if r: obra_id = r[0]

        try:
            # COMPRA: Gasolinera -> Bidon (Ticket como referencia)
            cur.execute("""INSERT INTO fenix_movimientos_combustible
                           (tipo_movimiento, fecha, semana, origen_tipo, origen_nombre,
                            destino_tipo, destino_nombre, equipo_id, obra_id,
                            litros, precio_unitario, folio_vale, rendimiento)
                           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        ('COMPRA', fecha_str, sem_int,
                         'Gasolinera', 'Gasolinera Levet',
                         'Equipo', placa,
                         equipo_id, obra_id,
                         litros, precio or 0, ticket, km))
            insertados += 1
        except Exception as e:
            errores += 1

    conn.commit()
    ok(f"Gasolina Levet: {insertados} transacciones. ({errores} omitidas)")

# =============================================================================
# FASE 1F: Gasolina Huixquilucan (normalizar formato semanal)
# =============================================================================
def migrar_gasolina_huixquilucan(conn):
    info("Leyendo Gasolina Huixquilucan (CONSUMOS GT - Hoja DIESEL/semanal)...")
    # Intentar leer hoja DIESEL que tiene el formato de autorizacion por fechas
    try:
        df = pd.read_excel(GAS_CONSUMOS, sheet_name='DIESEL', header=None)
    except:
        info("Hoja DIESEL no encontrada, intentando UT...")
        df = pd.read_excel(GAS_CONSUMOS, sheet_name='UT', header=None)

    # Detectar fechas en fila 1 (columnas a partir de col 5)
    fila_header = df.iloc[1].tolist()

    # Extraer fechas disponibles (columnas que son Timestamp)
    fechas_cols = {}
    for i, val in enumerate(fila_header):
        if isinstance(val, pd.Timestamp):
            fechas_cols[i] = val.strftime('%Y-%m-%d')

    cur = conn.cursor(); insertados = 0; errores = 0
    df_data = df.iloc[2:].reset_index(drop=True)

    for _, row in df_data.iterrows():
        placa  = clean(row.get(3) if len(row) > 3 else None)   # PLACAS en col D (indice 3)
        unidad = clean(row.get(2) if len(row) > 2 else None)   # UNIDAD en col C
        importe_autorizado = to_num(row.get(5) if len(row) > 5 else None)

        if not placa or placa in ('None','nan'): continue
        if not re.match(r'[A-Z0-9]{5,}', placa.replace('-','').replace(' ','')):
            continue

        equipo_id = None
        cur.execute("SELECT id FROM fenix_equipos WHERE numero_economico = ?", (placa,))
        r = cur.fetchone()
        if r: equipo_id = r[0]

        # Para cada fecha/col con importe registrado
        for col_idx, fecha_str in fechas_cols.items():
            importe_cargado = to_num(row.get(col_idx))
            if not importe_cargado or importe_cargado <= 0:
                continue

            sem_int = iso_week(fecha_str)
            try:
                cur.execute("""INSERT INTO fenix_movimientos_combustible
                               (tipo_movimiento, fecha, semana, origen_tipo, origen_nombre,
                                destino_tipo, destino_nombre, equipo_id,
                                litros, precio_unitario, folio_vale)
                               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                            ('COMPRA', fecha_str, sem_int,
                             'Gasolinera', 'Gasolinera Huixquilucan',
                             'Equipo', placa,
                             equipo_id,
                             0,      # Litros: no disponibles directamente, usar importe / precio
                             0,      # Precio: calcularemos al conciliar con facturas
                             f"HX-{placa}-{fecha_str}"))
                # Actualizar importe directamente porque la columna es GENERATED
                # (Se deja en 0L pero el importe se puede derivar al conciliar)
                insertados += 1
            except Exception as e:
                errores += 1

    conn.commit()
    ok(f"Gasolina Huixquilucan: {insertados} registros de carga semanal. ({errores} omitidos)")

# =============================================================================
# FASE 1G: Acarreos (Base_Datos del Maestro V12)
# =============================================================================
def migrar_acarreos(conn):
    info("Leyendo Acarreos (GC-MAT-1.0_Maestro_Consolidado_V12 - Base_Datos)...")
    df = pd.read_excel(ACARREOS_MASTER, sheet_name='Base_Datos')
    # Columnas: SEMANA | FECHA | FOLIO | SINDICATO | OBRA | MATERIAL | PLACA | OPERADOR |
    #           CAPACIDAD | OBSERVACIONES | PU | SUBTOTAL | IVA | TOTAL | CATEGORIA

    cur = conn.cursor(); insertados = 0; errores = 0

    for _, row in df.iterrows():
        folio   = clean(row.get('FOLIO'))
        fecha   = clean(row.get('FECHA'))
        semana  = to_num(row.get('SEMANA'))
        sind    = clean(row.get('SINDICATO'))
        obra_n  = clean(row.get('OBRA'))
        material= clean(row.get('MATERIAL'))
        placa   = clean(row.get('PLACA'))
        operador= clean(row.get('OPERADOR'))
        cap_raw = clean(row.get('CAPACIDAD'))
        pu      = to_num(row.get('PU'))
        subtotal= to_num(row.get('SUBTOTAL'))
        iva     = to_num(row.get('IVA'))
        categ   = clean(row.get('CATEGORIA'))
        obs     = clean(row.get('OBSERVACIONES'))

        if not placa or placa in ('None','nan'): continue
        if not subtotal: continue

        fecha_str = fecha[:10] if fecha and len(fecha) >= 10 else None

        # Capacidad: extraer numero de "14 M3" etc.
        cap_num = None
        if cap_raw:
            m = re.search(r'(\d+\.?\d*)', str(cap_raw))
            if m: cap_num = float(m.group(1))

        # Sindicato
        sindicato_id = None
        if sind and sind not in ('None','nan'):
            sindicato_id = get_or_create(cur, 'fenix_sindicatos', 'nombre', sind)

        # Obra
        obra_id = None
        if obra_n and obra_n not in ('None','nan'):
            cur.execute("SELECT id FROM fenix_obras WHERE upper(nombre) LIKE ?", (f"%{obra_n.upper()[:10]}%",))
            r = cur.fetchone()
            if r:
                obra_id = r[0]
            else:
                obra_id = get_or_create(cur, 'fenix_obras', 'nombre', obra_n,
                                        {'codigo': re.sub(r'[^A-Z]','',obra_n.upper())[:4]})

        if not obra_id or not sindicato_id: continue

        sem_int = int(semana) if semana else iso_week(fecha_str)

        try:
            cur.execute("""INSERT OR IGNORE INTO fenix_viajes_acarreo
                           (folio, fecha, semana, obra_id, sindicato_id, material, categoria,
                            placa, capacidad_m3, operador, costo_unitario, subtotal, iva, observaciones)
                           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (folio, fecha_str, sem_int, obra_id, sindicato_id,
                         material, categ, placa, cap_num, operador,
                         pu or 0, subtotal or 0, iva or 0, obs))
            if cur.rowcount > 0: insertados += 1
        except Exception as e:
            errores += 1

    conn.commit()
    ok(f"Acarreos: {insertados} viajes insertados. ({errores} omitidos/duplicados)")

# =============================================================================
# VERIFICACION FINAL
# =============================================================================
def verificar(conn):
    cur = conn.cursor()
    tablas = ['fenix_obras','fenix_sindicatos','fenix_equipos','fenix_contenedores',
              'fenix_facturas_combustible','fenix_movimientos_combustible',
              'fenix_viajes_acarreo','fenix_horas_trabajo']

    print(f"\n{BOLD}{CYAN}======= CONTEO FINAL DE REGISTROS ========{RESET}")
    for t in tablas:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        n = cur.fetchone()[0]
        estado = f"{VERDE}OK{RESET}" if n > 0 else f"{ROJO}VACIO{RESET}"
        print(f"  {t:<42} {n:>6} registros  [{estado}]")

    print(f"\n{BOLD}{CYAN}======= CONCILIACION DE FACTURAS =========={RESET}")
    # Ver columnas reales de la vista
    try:
        cur.execute("SELECT * FROM v_conciliacion_facturas LIMIT 0")
        cols = [d[0] for d in cur.description]
        cur.execute("SELECT * FROM v_conciliacion_facturas")
        rows = cur.fetchall()
        if rows:
            for r in rows:
                print(f"  {dict(zip(cols, r))}")
        else:
            print("  (Sin facturas registradas en esta migracion — esperado)")
    except Exception as e:
        print(f"  Vista no disponible: {e}")

    print(f"\n{BOLD}{CYAN}======= PAGOS ESTIMADOS A SINDICATOS ======{RESET}")
    cur.execute("""SELECT sindicato, obra, semana, total_viajes, total_a_pagar
                   FROM v_estimacion_pagos_sindicatos ORDER BY total_a_pagar DESC LIMIT 10""")
    rows = cur.fetchall()
    for r in rows:
        print(f"  {str(r[0]):<22} {str(r[1]):<22} Sem{r[2]}  {r[3]} viajes  ${float(r[4] or 0):>12,.2f}")

# =============================================================================
# MAIN
# =============================================================================
def main():
    print(f"\n{BOLD}{'='*58}")
    print(f"  SISTEMA FENIX -- Migracion ETL v1.0")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*58}{RESET}\n")

    if not os.path.exists(DB_PATH):
        err(f"fenix.db no encontrado. Ejecuta primero inicializar_fenix.py")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")

    pasos = [
        ("1A. Catalogos Diesel (Inventario + Asignaciones)",   migrar_catalogos_diesel),
        ("1B. Catalogos Gasolina (Placas y Centros de Trabajo)", migrar_catalogos_gasolina),
        ("1C. Horas de Trabajo (Captura_Horas)",               migrar_horas_trabajo),
        ("1D. Consumos Diesel Historico (Captura_Obra V2)",     migrar_diesel_historico),
        ("1E. Gasolina Levet (JDJ Provisional)",               migrar_gasolina_levet),
        ("1F. Gasolina Huixquilucan (Semanal Normalizado)",    migrar_gasolina_huixquilucan),
        ("1G. Acarreos (Maestro V12 - Base_Datos)",            migrar_acarreos),
    ]

    for nombre, fn in pasos:
        print(f"\n{BOLD}[{nombre}]{RESET}")
        try:
            fn(conn)
        except Exception as e:
            err(f"Error en {nombre}: {e}")
            import traceback; traceback.print_exc()

    verificar(conn)
    conn.close()

    print(f"\n{VERDE}{BOLD}{'='*58}")
    print(f"  MIGRACION COMPLETADA")
    print(f"{'='*58}{RESET}\n")

if __name__ == "__main__":
    main()
