#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ETL directo: Carga de Acarreos sem25 y sem26 desde Excel -> fenix.db
"""
import sqlite3, openpyxl, sys, os
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, 'fenix.db')

# ─── TARIFAS ─────────────────────────────────────────────────────────────────
def get_tarifa(material, obra_key):
    mat = str(material).upper().strip() if material else ''
    is_l3m = any(k in str(obra_key).upper() for k in ['L3M', 'LERMA', 'TRES MARIAS'])
    if is_l3m:
        if 'FRESADO' in mat:   return 7000
        if 'PROTOCOLO' in mat or 'MEZCLA' in mat or 'AMAAC' in mat: return 6280
        if 'LIMPIEZA' in mat:  return 7000
        return 7000
    # MEX-TOL / Default COSUM
    if 'FRESADO' in mat:   return 2000
    if 'CARPETA' in mat:   return 2850
    if 'MEZCLA' in mat:    return 2850
    if 'LIMPIEZA' in mat:  return 2000
    return 2000

def safe_date(val):
    if val is None: return None
    if isinstance(val, datetime): return val.strftime('%Y-%m-%d')
    return str(val)[:10]

def get_sindicato_id(text):
    t = str(text).upper() if text else ''
    if 'EMULSIONES' in t or 'JORGE' in t: return 7
    if 'COSUM' in t: return 5
    if 'OBRAS PUBLICAS' in t: return 2
    return 5  # default COSUM-TOLUCA

# ─── PARSE ARCHIVO 1: MEX-TOL SEM 26 ─────────────────────────────────────────
# Columnas (col A=1 vacía): B=SEM,C=NO,D=FOLIO,E=FECHA,F=VIAJES,G=MATERIAL,
# H=PLACAS,I=CAPACIDAD,J=UNIDAD,K=OPERADOR,L=SINDICATO,...,R=OBSERVACIONES
def parse_mextol(filepath):
    wb = openpyxl.load_workbook(filepath, data_only=True)
    rows = []
    for shname in wb.sheetnames:
        ws = wb[shname]
        categoria = 'FRESADO' if 'FRESADO' in shname.upper() else 'MEZCLA'
        for r in range(7, ws.max_row + 1):
            semana   = ws.cell(r, 2).value
            folio    = ws.cell(r, 4).value
            fecha    = ws.cell(r, 5).value
            material = ws.cell(r, 7).value
            placa    = ws.cell(r, 8).value
            capac    = ws.cell(r, 9).value
            operador = ws.cell(r, 11).value
            sindicato= ws.cell(r, 12).value
            obs      = ws.cell(r, 18).value

            if not (folio and fecha and placa): continue
            try: sem = int(semana) if semana else 26
            except: sem = 26

            capac_val = float(capac) if capac else 14.0  # default 14 M3

            costo    = get_tarifa(material or categoria, 'MEX-TOL')
            subtotal = costo
            iva      = round(subtotal * 0.16, 2)

            rows.append({
                'folio':          str(int(folio)) if folio else None,
                'fecha':          safe_date(fecha),
                'semana':         sem,
                'obra_id':        1,  # México-Toluca
                'sindicato_id':   get_sindicato_id(sindicato),
                'material':       str(material).strip() if material else shname,
                'categoria':      categoria,
                'placa':          str(placa).strip().upper(),
                'capacidad_m3':   capac_val,
                'operador':       str(operador).strip() if operador else '',
                'costo_unitario': costo,
                'subtotal':       subtotal,
                'iva':            iva,
                'observaciones':  str(obs).strip() if obs else '',
            })
    return rows

# ─── PARSE ARCHIVO 2: L3M SEM 25 ─────────────────────────────────────────────
# Columnas (sin col vacía inicial): A=SEM,B=NO,C=FOLIO,D=FECHA,E=VIAJES,
# F=MATERIAL,G=PLACAS,H=CAPACIDAD,I=UNIDAD/PESO,J=OPERADOR,K=SINDICATO,...
def parse_l3m(filepath):
    wb = openpyxl.load_workbook(filepath, data_only=True)
    rows = []
    for shname in wb.sheetnames:
        ws = wb[shname]
        is_mezcla = 'MEZCLA' in shname.upper()
        categoria = 'MEZCLA' if is_mezcla else 'FRESADO'
        for r in range(7, ws.max_row + 1):
            semana   = ws.cell(r, 1).value
            folio    = ws.cell(r, 3).value
            fecha    = ws.cell(r, 4).value
            material = ws.cell(r, 6).value
            placa    = ws.cell(r, 7).value
            capac    = ws.cell(r, 8).value
            operador = ws.cell(r, 10).value
            sindicato= ws.cell(r, 11).value

            if not (folio and fecha and placa): continue
            try: sem = int(semana) if semana else 25
            except: sem = 25

            capac_val = float(capac) if capac else 14.0

            costo    = get_tarifa(material or categoria, 'L3M')
            subtotal = costo
            iva      = round(subtotal * 0.16, 2)

            rows.append({
                'folio':          str(int(folio)) if folio else None,
                'fecha':          safe_date(fecha),
                'semana':         sem,
                'obra_id':        2,  # Lerma - Tres Marías
                'sindicato_id':   get_sindicato_id(sindicato),
                'material':       str(material).strip() if material else shname,
                'categoria':      categoria,
                'placa':          str(placa).strip().upper(),
                'capacidad_m3':   capac_val,
                'operador':       str(operador).strip() if operador else '',
                'costo_unitario': costo,
                'subtotal':       subtotal,
                'iva':            iva,
                'observaciones':  '',
            })
    return rows

# ─── INSERT ───────────────────────────────────────────────────────────────────
def insert_rows(cur, rows):
    inserted = skipped = errors = 0
    for row in rows:
        if not row['folio'] or not row['fecha']: continue
        cur.execute('SELECT id FROM fenix_viajes_acarreo WHERE folio=? AND fecha=?',
                    (row['folio'], row['fecha']))
        if cur.fetchone():
            skipped += 1
            continue
        try:
            cur.execute('''
                INSERT INTO fenix_viajes_acarreo
                    (folio, fecha, semana, obra_id, sindicato_id, material, categoria,
                     placa, capacidad_m3, operador, costo_unitario, subtotal, iva, estatus, observaciones)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ''', (
                row['folio'], row['fecha'], row['semana'],
                row['obra_id'], row['sindicato_id'],
                row['material'], row['categoria'], row['placa'],
                row['capacidad_m3'], row['operador'],
                row['costo_unitario'], row['subtotal'], row['iva'],
                'Registrado', row['observaciones']
            ))
            inserted += 1
        except Exception as e:
            errors += 1
            print(f'  ERROR folio={row["folio"]} placa={row["placa"]}: {e}')
    return inserted, skipped, errors

# ─── MAIN ─────────────────────────────────────────────────────────────────────
f1 = os.path.join(BASE_DIR, 'CAPTURA DE ACARREOS (SEM # 26) OBRA MEX-TOL.xlsx')
f2 = os.path.join(BASE_DIR, 'CAPTURA DE ACARREOS POR SEMANA L3M FRESADO.xlsx')

print('Leyendo archivos...')
rows_mextol = parse_mextol(f1)
rows_l3m    = parse_l3m(f2)
print(f'  MEX-TOL SEM26: {len(rows_mextol)} registros')
print(f'  L3M     SEM25: {len(rows_l3m)} registros')
print(f'  TOTAL:         {len(rows_mextol)+len(rows_l3m)} registros a procesar')

total_mex = sum(r['subtotal'] for r in rows_mextol)
total_l3m = sum(r['subtotal'] for r in rows_l3m)
print(f'\nSubtotal MEX-TOL SEM26: ${total_mex:,.2f}')
print(f'Subtotal L3M    SEM25:  ${total_l3m:,.2f}')

print('\nInsertando en fenix.db...')
db  = sqlite3.connect(DB_PATH)
cur = db.cursor()

ins1, skip1, err1 = insert_rows(cur, rows_mextol)
ins2, skip2, err2 = insert_rows(cur, rows_l3m)
db.commit()

print(f'\nMEX-TOL SEM26: {ins1} insertados, {skip1} duplicados omitidos, {err1} errores')
print(f'L3M     SEM25: {ins2} insertados, {skip2} duplicados omitidos, {err2} errores')
print(f'TOTAL insertados: {ins1+ins2}')

print('\n=== VERIFICACION FINAL EN BASE DE DATOS ===')
cur.execute('''
    SELECT v.semana, o.nombre as obra, v.categoria,
           COUNT(*) as registros,
           ROUND(SUM(v.subtotal),2) as subtotal,
           ROUND(SUM(v.iva),2) as iva,
           ROUND(SUM(v.subtotal+v.iva),2) as total_con_iva
    FROM fenix_viajes_acarreo v
    JOIN fenix_obras o ON o.id=v.obra_id
    WHERE v.semana IN (25,26)
    GROUP BY v.semana, o.nombre, v.categoria
    ORDER BY v.semana, o.nombre, v.categoria
''')
print(f'{"Sem":>4} {"Obra":<25} {"Categ":<10} {"Regs":>5} {"Subtotal":>14} {"IVA":>12} {"Total c/IVA":>14}')
print('-'*90)
for r in cur.fetchall():
    print(f'{r[0]:>4} {r[1]:<25} {r[2]:<10} {r[3]:>5} ${r[4]:>13,.2f} ${r[5]:>11,.2f} ${r[6]:>13,.2f}')

cur.execute('SELECT semana, ROUND(SUM(subtotal),2), ROUND(SUM(subtotal+iva),2) FROM fenix_viajes_acarreo WHERE semana IN (25,26) GROUP BY semana')
print()
print('=== TOTALES GENERALES ===')
for r in cur.fetchall():
    print(f'Semana {r[0]}: Subtotal=${r[1]:,.2f}  Total con IVA=${r[2]:,.2f}')

db.close()
