import psycopg2, re
from psycopg2.extras import DictCursor

def clean_tag_str(t):
    if not t: return ''
    return re.sub(r'[^A-Za-z0-9]', '', str(t)).upper()

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

for sem in ['SEMANA 32', 'SEMANA 33', 'TODAS']:
    print(f"\n=======================================================")
    print(f"TEST COMPARATIVA AUTORIZACIONES: {sem}")
    print(f"=======================================================")
    
    cur.execute("SELECT * FROM tags.autorizaciones ORDER BY empresa, responsable;")
    auth_rows = cur.fetchall()
    
    if sem == 'TODAS':
        cur.execute("""
            SELECT empresa, tag, no_economico, responsable, obra_asignada, SUM(ABS(importe)) as consumo_real, COUNT(*) as pasadas
            FROM tags.movimientos
            GROUP BY empresa, tag, no_economico, responsable, obra_asignada;
        """)
    else:
        cur.execute("""
            SELECT empresa, tag, no_economico, responsable, obra_asignada, SUM(ABS(importe)) as consumo_real, COUNT(*) as pasadas
            FROM tags.movimientos
            WHERE semana = %s OR semana = %s
            GROUP BY empresa, tag, no_economico, responsable, obra_asignada;
        """, (sem, sem.replace('SEMANA ', '')))
    movs_rows = cur.fetchall()
    
    consumo_map = {}
    for m in movs_rows:
        emp = m['empresa']
        tag = clean_tag_str(m['tag'])
        no_econ = clean_tag_str(m['no_economico'])
        resp = (m['responsable'] or '').strip().upper()
        c_real = float(m['consumo_real'] or 0)
        
        if tag: consumo_map[(emp, tag)] = consumo_map.get((emp, tag), 0.0) + c_real
        if no_econ: consumo_map[(emp, no_econ)] = consumo_map.get((emp, no_econ), 0.0) + c_real
        if resp: consumo_map[(emp, resp)] = consumo_map.get((emp, resp), 0.0) + c_real
        
    for a in auth_rows:
        emp = a['empresa']
        c_tag = clean_tag_str(a['tag'])
        c_ne = clean_tag_str(a['no_economico'])
        c_resp = (a['responsable'] or '').strip().upper()
        aut = float(a['monto_autorizado'] or 0)
        
        c_real = consumo_map.get((emp, c_tag), 0.0) or consumo_map.get((emp, c_ne), 0.0) or consumo_map.get((emp, c_resp), 0.0)
        
        if not c_real:
            for (e, k), val in consumo_map.items():
                if e == emp:
                    if c_tag and len(c_tag) >= 6 and (c_tag in k or k in c_tag):
                        c_real = val; break
                    if c_resp and len(c_resp) >= 5 and (c_resp in k or k in c_resp):
                        c_real = val; break
                        
        if 'BRYAN' in c_resp or 'BRAYAN' in c_resp or '30874329' in c_tag or '30874326' in c_tag:
            print(f"[{emp}] {a['responsable']:<30} | Tag:{a['tag']:<15} | Aut:${aut:>8.2f} | Cons:${c_real:>8.2f} | Exc:${max(0, c_real - aut):>8.2f}")

conn.close()
