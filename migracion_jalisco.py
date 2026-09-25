import pandas as pd
import psycopg2
import re

try:
    conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
    cur = conn.cursor()
    cur.execute("DELETE FROM diesel.jalisco_movimientos")
    cur.execute("ALTER SEQUENCE diesel.jalisco_movimientos_id_seq RESTART WITH 1")
    
    file_path = 'c:\\Users\\JOSE\\Desktop\\Proyecto fenix\\MAESTRO_CONTROL_DIESEL_NUEVO.xlsx'
    df = pd.read_excel(file_path, sheet_name='BD_JALISCO', engine='calamine')
    
    inserted = 0
    for idx, row in df.iterrows():
        # Saltamos filas vacías
        if pd.isna(row.get('Fecha')):
            continue
            
        fecha = pd.to_datetime(row['Fecha']).date() if not pd.isna(row['Fecha']) else None
        if fecha is None: continue
        
        # Parse semana
        semana = 0
        if not pd.isna(row['Semana']):
            val = str(row['Semana'])
            m = re.search(r'\d+', val)
            if m:
                semana = int(m.group(0))
                
        tipo_mov = str(row['Movimiento']).strip().upper() if not pd.isna(row['Movimiento']) else 'AJUSTE'
        if tipo_mov == 'NAN' or not tipo_mov: tipo_mov = 'AJUSTE'
        
        equipo_desc = str(row['Equipo']).strip() if not pd.isna(row['Equipo']) else None
        eq_eco = str(row['Económico']).strip() if not pd.isna(row['Económico']) else None
        
        # Determinar litros basados en la columna
        lts = 0.0
        if tipo_mov == 'ENTRADA' and not pd.isna(row.get('Entrada (L)')):
            lts = float(row['Entrada (L)'])
        elif tipo_mov == 'SALIDA' and not pd.isna(row.get('Salida (L)')):
            lts = float(row['Salida (L)'])
        elif tipo_mov == 'AJUSTE':
            if not pd.isna(row.get('Ajuste')):
                lts = float(row['Ajuste'])
                
        costo = float(row['Costo/L']) if not pd.isna(row.get('Costo/L')) else None
        importe = float(row['Importe']) if not pd.isna(row.get('Importe')) else None
            
        saldo = float(row['Existencia Teórica']) if not pd.isna(row.get('Existencia Teórica')) else 0.0
        obs = str(row['Observaciones']).strip() if not pd.isna(row.get('Observaciones')) else ''
        
        if obs == 'nan': obs = ''
        if equipo_desc == 'nan': equipo_desc = None
        if eq_eco == 'nan': eq_eco = None
        
        cur.execute("""
            INSERT INTO diesel.jalisco_movimientos 
            (fecha, semana, tipo_movimiento, equipo, equipo_economico, litros, costo_por_litro, importe_total, saldo_teorico, observaciones)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (fecha, semana, tipo_mov, equipo_desc, eq_eco, lts, costo, importe, saldo, obs))
        inserted += 1
        
    conn.commit()
    conn.close()
    print(f"Migración completada. Se insertaron {inserted} registros.")
except Exception as e:
    print("Error migrando:", e)
