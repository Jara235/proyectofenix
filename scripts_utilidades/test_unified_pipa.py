import psycopg2, re
from psycopg2.extras import DictCursor

def clean_str(s):
    if not s: return ''
    return re.sub(r'[^A-Za-z0-9]', '', str(s)).upper()

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

sem = 'SEMANA 32'

cur.execute("SELECT * FROM tags.autorizaciones ORDER BY empresa, responsable;")
auth_rows = cur.fetchall()

cur.execute("""
    SELECT empresa, tag, no_economico, responsable, obra_asignada, SUM(ABS(importe)) as consumo_real, COUNT(*) as pasadas
    FROM tags.movimientos
    WHERE semana = %s OR semana = %s
    GROUP BY empresa, tag, no_economico, responsable, obra_asignada;
""", (sem, sem.replace('SEMANA ', '')))
movs_rows = cur.fetchall()

print(f"=== TEST CALCULO TOTAL POR UNIDAD/RESPONSABLE EN {sem} ===")

for a in auth_rows:
    emp = a['empresa']
    a_tag = clean_str(a['tag'])
    a_ne = clean_str(a['no_economico'])
    a_resp = clean_str(a['responsable'])
    aut = float(a['monto_autorizado'] or 0)
    
    # Encontrar todos los movimientos de la semana que correspondan a este vehículo/responsable
    c_real = 0.0
    pasadas = 0
    matched_tags = []
    
    for m in movs_rows:
        if m['empresa'] != emp:
            continue
        m_tag = clean_str(m['tag'])
        m_ne = clean_str(m['no_economico'])
        m_resp = clean_str(m['responsable'])
        
        is_match = False
        if a_tag and m_tag and (a_tag == m_tag or a_tag in m_tag or m_tag in a_tag):
            is_match = True
        elif a_ne and m_ne and (a_ne == m_ne or a_ne in m_ne or m_ne in a_ne):
            is_match = True
        elif a_resp and m_resp and (a_resp == m_resp or a_resp in m_resp or m_resp in a_resp):
            is_match = True
            
        if is_match:
            c_real += float(m['consumo_real'] or 0)
            pasadas += int(m['pasadas'] or 0)
            matched_tags.append(m['tag'])
            
    if 'PIPA' in a_resp or 'BRYAN' in a_resp or 'BRAYAN' in a_resp:
        print(f"[{emp}] {a['responsable']:<25} | Tags: {matched_tags} | Pasadas: {pasadas} | Aut: ${aut:>8.2f} | Consumo: ${c_real:>8.2f} | Exc: ${max(0, c_real - aut):>8.2f}")

conn.close()
