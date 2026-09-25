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

print(f"=== TEST MATCHING EXACTO POR TAG Y RESPONSABLE ({sem}) ===")

# Construir mapa de tag a autorización
auth_by_tag = {}
auth_by_resp = {}
for a in auth_rows:
    emp = a['empresa']
    t_c = clean_str(a['tag'])
    r_c = clean_str(a['responsable'])
    ne_c = clean_str(a['no_economico'])
    if t_c: auth_by_tag[(emp, t_c)] = a
    if r_c: auth_by_resp[(emp, r_c)] = a

# Asignar cada movimiento de la semana a su autorización específica
mov_match = {}
for m in movs_rows:
    emp = m['empresa']
    m_t = clean_str(m['tag'])
    m_ne = clean_str(m['no_economico'])
    m_r = clean_str(m['responsable'])
    
    # 1. Match por tag
    matched_a = None
    if (emp, m_t) in auth_by_tag:
        matched_a = auth_by_tag[(emp, m_t)]
    else:
        for (e, t_k), a in auth_by_tag.items():
            if e == emp and t_k and len(t_k) >= 6 and (t_k in m_t or m_t in t_k):
                matched_a = a; break
                
    # 2. Si no hubo match por tag, match por responsable
    if not matched_a:
        if (emp, m_r) in auth_by_resp:
            matched_a = auth_by_resp[(emp, m_r)]
        else:
            for (e, r_k), a in auth_by_resp.items():
                if e == emp and r_k and len(r_k) >= 5 and (r_k in m_r or m_r in r_k):
                    matched_a = a; break
                    
    a_id = matched_a['id'] if matched_a else None
    if a_id not in mov_match:
        mov_match[a_id] = {'consumo': 0.0, 'pasadas': 0, 'tags': set(), 'matched_a': matched_a}
    mov_match[a_id]['consumo'] += float(m['consumo_real'] or 0)
    mov_match[a_id]['pasadas'] += int(m['pasadas'] or 0)
    if m['tag']: mov_match[a_id]['tags'].add(m['tag'])

print("\n--- RESULTADOS JDJ ---")
for a in auth_rows:
    if a['empresa'] == 'JDJ':
        m_info = mov_match.get(a['id'], {'consumo': 0.0, 'pasadas': 0, 'tags': set()})
        c_real = m_info['consumo']
        aut = float(a['monto_autorizado'] or 0)
        print(f"{a['responsable']:<30} | Tag: {a['tag']:<15} | Aut: ${aut:>8.2f} | Cons: ${c_real:>8.2f} | Tags Mov: {list(m_info['tags'])}")

print("\n--- RESULTADOS TRD ---")
for a in auth_rows:
    if a['empresa'] == 'TRD':
        m_info = mov_match.get(a['id'], {'consumo': 0.0, 'pasadas': 0, 'tags': set()})
        c_real = m_info['consumo']
        aut = float(a['monto_autorizado'] or 0)
        print(f"{a['responsable']:<30} | Tag: {a['tag']:<15} | Aut: ${aut:>8.2f} | Cons: ${c_real:>8.2f} | Tags Mov: {list(m_info['tags'])}")

conn.close()
