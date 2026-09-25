import psycopg2
from psycopg2.extras import DictCursor

conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor(cursor_factory=DictCursor)

# Obtener movimientos por semana
cur.execute("""
    SELECT DISTINCT semana, empresa, tag, no_economico, responsable, tipo_unidad, placas, obra_asignada
    FROM tags.movimientos
    ORDER BY semana, empresa, responsable;
""")
mov_tags = cur.fetchall()

# Obtener autorizaciones
cur.execute("SELECT * FROM tags.autorizaciones;")
aut_rows = cur.fetchall()

def clean_tag(t):
    return (t or '').replace('.', '').replace(' ', '').strip().upper()

aut_by_tag = {}
aut_by_resp = {}
for a in aut_rows:
    t = clean_tag(a['tag'])
    r = (a['responsable'] or '').strip().upper()
    emp = a['empresa']
    if t:
        aut_by_tag[(emp, t)] = a
    if r:
        aut_by_resp[(emp, r)] = a

print("=== VERIFICACIÓN DE CRUCE MOVIMIENTOS vs AUTORIZACIONES ===")
sin_autorizacion = []
for m in mov_tags:
    sem = m['semana']
    emp = m['empresa']
    t_clean = clean_tag(m['tag'])
    resp = (m['responsable'] or '').strip()
    no_econ = (m['no_economico'] or '').strip()
    
    # Intento 1: Por tag limpio
    matched = aut_by_tag.get((emp, t_clean))
    
    # Intento 2: Por responsable
    if not matched:
        matched = aut_by_resp.get((emp, resp.upper()))
        
    # Intento 3: Por coincidencia parcial
    if not matched:
        for (e, t_k), a in aut_by_tag.items():
            if e == emp and (t_k in t_clean or t_clean in t_k):
                matched = a
                break
                
    if not matched or float(matched['monto_autorizado'] or 0) == 0:
        sin_autorizacion.append({
            'semana': sem,
            'empresa': emp,
            'tag': m['tag'],
            'tag_clean': t_clean,
            'no_economico': no_econ,
            'responsable': resp,
            'matched': dict(matched) if matched else None,
            'monto_aut': float(matched['monto_autorizado']) if matched else 0.0
        })

print(f"Total registros analizados: {len(mov_tags)}")
print(f"Registros con Autorizado $0 o sin match: {len(sin_autorizacion)}")
for s in sin_autorizacion[:25]:
    print(f"[{s['semana']}] {s['empresa']} | Tag: {s['tag']} | Resp: {s['responsable']} | Match: {s['matched']['responsable'] if s['matched'] else 'NINGUNO'} -> Aut: ${s['monto_aut']:,.2f}")

conn.close()
