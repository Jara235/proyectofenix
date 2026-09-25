import openpyxl, psycopg2, re
from psycopg2.extras import DictCursor

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

def safe_float(val):
    if val is None: return 0.0
    try:
        return float(val)
    except:
        return 0.0

# 1. Cargar datos de producción de Acarreos en Semana 25 México-Toluca
wb_ac = openpyxl.load_workbook('acarreos y Fresado/CAPTURA DE ACARREOS (SEM # 25) OBRA MEX-TOL.xlsx', data_only=True)
ws_carp = wb_ac['CARPETA']
tot_m3_carpeta = sum(safe_float(ws_carp.cell(r, 8).value) for r in range(7, ws_carp.max_row + 1))
viajes_carp = sum(1 for r in range(7, ws_carp.max_row + 1) if safe_float(ws_carp.cell(r, 8).value) > 0)
densidad_asfalto = 2.35
tot_ton_carpeta = tot_m3_carpeta * densidad_asfalto

ws_fres = wb_ac['FRESADO']
tot_m3_fresado = sum(safe_float(ws_fres.cell(r, 8).value) for r in range(7, ws_fres.max_row + 1))
viajes_fres = sum(1 for r in range(7, ws_fres.max_row + 1) if safe_float(ws_fres.cell(r, 8).value) > 0)

# 2. Cargar horas registradas en Semana 25
wb_m = openpyxl.load_workbook('formatos/GC-COMB-3.1_Excel_Maestro_Control_Combustible_Grupo_Trujano_FINAL_V2.xlsx', data_only=True)
ws_h = wb_m['Captura_Horas']
horas_eq = {}
for r in range(4, ws_h.max_row + 1):
    obra = str(ws_h.cell(r, 3).value or '')
    maq = str(ws_h.cell(r, 4).value or '').strip()
    eco = str(ws_h.cell(r, 5).value or '').strip()
    h = ws_h.cell(r, 7).value
    if 'TOLUCA' in obra.upper() and h:
        try:
            h_val = float(h)
            k = (eco, maq)
            if k not in horas_eq:
                horas_eq[k] = {'horas': 0.0, 'dias_activos': 0}
            horas_eq[k]['horas'] += h_val
            horas_eq[k]['dias_activos'] += 1
        except: pass

# 3. Cargar consumos de Diesel reales de la BD para Semana 25 México-Toluca
cur.execute("""
    SELECT equipo, sum(litros) as total_litros, count(*) as cargas
    FROM diesel.consumos
    WHERE semana = '25' AND (obra_destino ILIKE '%TOLUCA%' OR obra_destino ILIKE '%MÉXICO%')
    GROUP BY equipo;
""")
diesel_db = {re.sub(r'\s+', ' ', r['equipo'].strip().upper()): float(r['total_litros']) for r in cur.fetchall()}

# Tabla de rendimientos esperados ajustados 2026
rend_esp_dict = {
    'PAVIMENTADORA': 15.37,
    'PERFILADORA': 65.00,
    'VIBROCOMPACTADOR': 13.30,
    'TANDEM': 13.73,
    'NEUMATICO': 10.87,
    'BARREDORA': 8.94,
    'RETROEXCAVADORA': 7.36,
    'PETROLIZADORA': 12.76,
    'DOBLE RODILLO': 14.30,
    'COMPRESOR': 9.97,
}

print("=" * 135)
print("EJERCICIO DE ESTIMACIÓN DE RENDIMIENTOS DE MAQUINARIA — SEMANA 25 (OBRA MÉXICO-TOLUCA)")
print("=" * 135)
print(f"Producción Registrada:")
print(f"   • Carpeta Asfáltica Tendida: {viajes_carp} viajes | {tot_m3_carpeta:,.2f} m³ | {tot_ton_carpeta:,.2f} Toneladas")
print(f"   • Fresado de Pavimento:     {viajes_fres} viajes | {tot_m3_fresado:,.2f} m³\n")

print(f"{'Eco / ID':<15} | {'Equipo / Maquinaria':<30} | {'Hrs Reg.':<9} | {'Diesel (L)':<10} | {'Rend. Real':<11} | {'Rend. Esperado':<14} | {'Eficiencia':<14} | {'Rend. Producción':<20}")
print("-" * 135)

for (eco, maq), hinfo in horas_eq.items():
    hrs = hinfo['horas']
    dias = hinfo['dias_activos']
    
    # Buscar litros en diesel_db
    maq_clean = re.sub(r'\s+', ' ', maq.strip().upper())
    lts = diesel_db.get(maq_clean, 0.0)
    if lts == 0.0:
        for k_d, v_d in diesel_db.items():
            if any(w in k_d for w in maq_clean.split() if len(w) > 4):
                lts = v_d
                break
                
    rend_real = (lts / hrs) if hrs > 0 and lts > 0 else 0.0
    
    # Determinar esperado
    r_esp = 10.0
    for kw, val in rend_esp_dict.items():
        if kw in maq_clean:
            r_esp = val
            break
            
    if rend_real > 0:
        desv = ((rend_real - r_esp) / r_esp) * 100
        eficiencia = f"{desv:+.1f}% ({'ALTO' if desv > 10 else 'OPTIMO' if desv >= -10 else 'BAJO'})"
    else:
        eficiencia = "S/D"
        
    # Rendimiento por produccion
    if 'PAVIMENTADORA' in maq_clean and tot_ton_carpeta > 0 and lts > 0:
        rend_prod = f"{lts/tot_ton_carpeta:.3f} L/Ton asfalto"
    elif 'PERFILADORA' in maq_clean and tot_m3_fresado > 0 and lts > 0:
        rend_prod = f"{lts/tot_m3_fresado:.3f} L/m³ fresado"
    elif 'RETROEXCAVADORA' in maq_clean and tot_m3_fresado > 0 and lts > 0:
        rend_prod = f"{lts/tot_m3_fresado:.3f} L/m³ carga"
    else:
        rend_prod = f"{lts/dias:.1f} L/día activo" if dias > 0 and lts > 0 else "—"

    print(f"{eco:<15} | {maq[:30]:<30} | {hrs:>6.1f} hrs | {lts:>8.1f} L | {rend_real:>8.2f} L/h | {r_esp:>8.2f} L/h    | {eficiencia:<14} | {rend_prod:<20}")

print("-" * 135)
conn.close()
