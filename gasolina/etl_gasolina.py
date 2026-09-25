# -*- coding: utf-8 -*-
"""
SISTEMA FENIX -- ETL Gasolina Completo (Modelo Matriz)
Extrae el presupuesto y los reportes diarios de deducción (SEMANA 26 (1).xlsx)
y cruza contra los consumos reales de gasolineras (Levet, Huixquilucan).
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import sqlite3, os, re
import openpyxl
from datetime import datetime, date

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
GAS_DIR   = os.path.join(BASE_DIR, "gasolina")
DB_PATH   = os.path.join(BASE_DIR, "fenix.db")

F_SEM26   = os.path.join(GAS_DIR, "SEMANA 26 (1).xlsx")
F_LEVET   = os.path.join(GAS_DIR, "CONTROL JDJ PROVISIONAL semana 27.xlsx")
F_HUIX    = os.path.join(GAS_DIR, "CONSUMOS  DE GASOLINA SEMANALES GT.xlsx")

def fecha_str(v):
    if isinstance(v, datetime): return v.strftime('%Y-%m-%d')
    if isinstance(v, date):     return v.strftime('%Y-%m-%d')
    if isinstance(v, str) and v.strip(): return v.strip()[:10]
    return None

def semana_de_fecha(fecha_str_val):
    if not fecha_str_val: return None
    try:
        d = datetime.strptime(fecha_str_val[:10], '%Y-%m-%d')
        return d.isocalendar()[1]
    except: return None

def clean_str(v):
    if v is None: return None
    s = str(v).strip()
    return s if s else None

def clean_float(v):
    if v is None: return 0.0
    if isinstance(v, (int, float)): return float(v)
    s = str(v).replace('$','').replace(',','').strip()
    try: return float(s)
    except: return 0.0

def normalizar_placa(p):
    if not p: return None
    return re.sub(r'[\s\-_]+', '', str(p).upper().strip())

def run():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1. Crear nuevo esquema
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS fenix_gas_presupuestos (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        semana          INTEGER,
        responsable     TEXT,
        obra            TEXT,
        unidad          TEXT,
        placa           TEXT,
        monto_autorizado REAL DEFAULT 0,
        created_at      TEXT DEFAULT (datetime('now','localtime'))
    );
    CREATE TABLE IF NOT EXISTS fenix_gas_reportes_diarios (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        presupuesto_id  INTEGER,
        fecha           TEXT,
        proveedor       TEXT,
        monto_reportado REAL DEFAULT 0,
        FOREIGN KEY(presupuesto_id) REFERENCES fenix_gas_presupuestos(id)
    );
    -- Tabla para consumos reales de gasolinera
    CREATE TABLE IF NOT EXISTS fenix_gas_tickets_reales (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        folio           TEXT UNIQUE,
        ticket          TEXT,
        fecha           TEXT,
        semana          INTEGER,
        placa           TEXT,
        conductor       TEXT,
        responsable     TEXT,
        obra            TEXT,
        unidad          TEXT,
        litros          REAL DEFAULT 0,
        precio_litro    REAL DEFAULT 0,
        importe         REAL DEFAULT 0,
        gasolinera      TEXT,
        created_at      TEXT DEFAULT (datetime('now','localtime'))
    );
    """)
    conn.commit()

    cur.execute("DELETE FROM fenix_gas_presupuestos")
    cur.execute("DELETE FROM fenix_gas_reportes_diarios")
    cur.execute("DELETE FROM fenix_gas_tickets_reales")
    conn.commit()

    print("\n=== FASE A: Lectura de Matriz Maestra (SEMANA 26) ===")
    wb = openpyxl.load_workbook(F_SEM26, data_only=True)
    ws = wb.active
    
    # Extraer fechas y proveedores de las filas 2 y 3
    row2 = list(ws.iter_rows(min_row=2, max_row=2, values_only=True))[0]
    row3 = list(ws.iter_rows(min_row=3, max_row=3, values_only=True))[0]
    
    column_maps = [] # list of (col_idx, fecha_str, proveedor)
    current_fecha = None
    for col_idx in range(6, len(row2)): # Datos de dias empiezan en col G (index 6)
        if col_idx < len(row2) and isinstance(row2[col_idx], datetime):
            current_fecha = fecha_str(row2[col_idx])
        elif col_idx < len(row2) and isinstance(row2[col_idx], str) and re.match(r'\d{2}/\d{2}/\d{4}', row2[col_idx]):
            d = datetime.strptime(row2[col_idx], '%d/%m/%Y')
            current_fecha = d.strftime('%Y-%m-%d')
            
        prov = clean_str(row3[col_idx]) if col_idx < len(row3) else None
        if not prov: prov = "LEVET" if col_idx % 3 == 0 else "MOBILE" if col_idx % 3 == 1 else "SIVALE"
        
        # Estandarizar nombre de proveedor
        prov_norm = "LEVET" if "LEVET" in prov.upper() else "MOBILE" if "MOBIL" in prov.upper() else "SIVALE"
        
        if current_fecha:
            column_maps.append((col_idx, current_fecha, prov_norm))

    print(f"  Columnas mapeadas para dias: {len(column_maps)}")

    # Leer datos de matriz
    total_pres = 0
    total_reps = 0
    current_responsable = "DESCONOCIDO"
    
    for row in ws.iter_rows(min_row=4, values_only=True):
        if not any(v for v in row): continue
        # Fila de totales = parar
        if row[0] and clean_str(str(row[0])).upper() in ['TOTALES', 'TOTAL']: break
        # Verificar que la fila tenga número de fila (col A) 
        num_fila = clean_str(str(row[0])) if row[0] is not None else None
        if num_fila and not num_fila.isdigit(): continue  # fila de titulo/header
        
        # Col B (index 1) = RESPONSABLE. Si está vacío, heredar el anterior
        resp_col = clean_str(row[1])
        if resp_col:
            current_responsable = resp_col
        # Si row[1] es None o vacío, current_responsable se mantiene (herencia)
            
        obra = clean_str(row[2])
        unidad = clean_str(row[3])
        placa = normalizar_placa(row[4])
        monto_aut = clean_float(row[5])
        
        if not unidad and not placa and monto_aut == 0:
            continue
            
        cur.execute("""INSERT INTO fenix_gas_presupuestos
                       (semana, responsable, obra, unidad, placa, monto_autorizado)
                       VALUES (?,?,?,?,?,?)""",
                    (26, current_responsable, obra, unidad, placa, monto_aut))
        pres_id = cur.lastrowid
        total_pres += 1
        
        # Leer los reportes diarios
        for col_idx, fecha, prov in column_maps:
            if col_idx < len(row):
                monto_rep = clean_float(row[col_idx])
                if monto_rep > 0:
                    cur.execute("""INSERT INTO fenix_gas_reportes_diarios
                                   (presupuesto_id, fecha, proveedor, monto_reportado)
                                   VALUES (?,?,?,?)""",
                                (pres_id, fecha, prov, monto_rep))
                    total_reps += 1

    conn.commit()
    print(f"  Presupuestos (filas): {total_pres}")
    print(f"  Deducciones diarias : {total_reps}")


    # ─── FASE B: CONSUMOS LEVET ───
    print("\n=== FASE B: Consumos Gasolinería Levet ===")
    total_tickets = 0
    wb = openpyxl.load_workbook(F_LEVET, data_only=True)
    for sheet_name in wb.sheetnames:
        if 'JUNIO' in sheet_name.upper():
            ws = wb[sheet_name]
            for i, row in enumerate(ws.iter_rows(min_row=1, values_only=True)):
                if not any(v for v in row): continue
                if len(row) >= 10 and isinstance(row[2], datetime):
                    ticket = clean_str(row[1])
                    fecha = fecha_str(row[2])
                    placa = normalizar_placa(row[3])
                    conductor = clean_str(row[5])
                    obra = clean_str(row[6])
                    litros = clean_float(row[7])
                    precio = clean_float(row[8])
                    importe = clean_float(row[9])
                    
                    if not placa and not conductor: continue
                    if litros == 0 and importe == 0: continue
                    
                    folio = f"LE-{i+1:03d}"
                    semana = semana_de_fecha(fecha)
                    
                    cur.execute("""INSERT OR IGNORE INTO fenix_gas_tickets_reales
                                   (folio,ticket,fecha,semana,placa,conductor,obra,litros,precio_litro,importe,gasolinera)
                                   VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                                (folio, ticket, fecha, semana, placa, conductor, obra, litros, precio, importe, 'LEVET'))
                    total_tickets += 1

    # ─── FASE C: CONSUMOS HUIXQUILUCAN (MOBILE) ───
    print("\n=== FASE C: Consumos Gasolinería Huixquilucan (MOBILE) ===")
    wb = openpyxl.load_workbook(F_HUIX, data_only=True)
    if 'UT' in wb.sheetnames:
        ws = wb['UT']
        for i, row in enumerate(ws.iter_rows(min_row=4, values_only=True)):
            if not any(v for v in row): continue
            responsable = clean_str(row[0])
            unidad = clean_str(row[1])
            placa = normalizar_placa(row[2])
            obra = clean_str(row[3])
            
            if not responsable: continue
            
            for col_idx in range(7, len(row), 2):
                if col_idx+1 >= len(row): break
                fecha_val = fecha_str(row[col_idx])
                importe = clean_float(row[col_idx+1])
                
                if fecha_val and importe > 0:
                    precio_huix = 23.89
                    litros = round(importe / precio_huix, 3)
                    folio = f"HX-{placa or i}-{fecha_val}"
                    semana = semana_de_fecha(fecha_val)
                    
                    cur.execute("""INSERT OR IGNORE INTO fenix_gas_tickets_reales
                                   (folio,fecha,semana,placa,responsable,unidad,obra,litros,precio_litro,importe,gasolinera)
                                   VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                                (folio, fecha_val, semana, placa, responsable, unidad, obra, litros, precio_huix, importe, 'MOBILE'))
                    total_tickets += 1

    conn.commit()
    conn.close()
    
    print(f"\nETL Completado Exitosamente.")
    print(f"Total Presupuestos (Filas): {total_pres}")
    print(f"Total Reportes Diarios    : {total_reps}")
    print(f"Total Tickets Gasolinera  : {total_tickets}")

if __name__ == "__main__":
    run()
