import pdfplumber, re

def parse_num(val):
    if not val: return 0.0
    clean = re.sub(r'[^\d.]', '', str(val))
    try:
        return float(clean)
    except:
        return 0.0

# JDJ
print("=== JDJ AUTORIZACIONES DETALLADAS DEL PDF ===")
jdj_data = []
with pdfplumber.open('TAGS/aurotirzaciones/AUTORIZACION TAG JDJ.pdf') as pdf:
    for p in pdf.pages:
        for t in p.extract_tables():
            for r in t:
                cleaned = [str(c or '').replace('\n', ' ').strip() for c in r]
                if cleaned and cleaned[0].isdigit():
                    no = cleaned[0]
                    tag = cleaned[1]
                    ct = cleaned[2]
                    placas = cleaned[3]
                    unidad = cleaned[4]
                    resp = cleaned[5]
                    clase = cleaned[6]
                    estatus = cleaned[7]
                    actual = parse_num(cleaned[8])
                    ct_dest = cleaned[9] if len(cleaned) > 10 else ''
                    aut = parse_num(cleaned[-1])
                    
                    # Para Bryan Chavez, el usuario indicó explícitamente $1,000.00
                    if 'BRAYAN' in resp.upper() or 'BRYAN' in resp.upper() or '30874329' in tag:
                        aut = 1000.0
                        
                    jdj_data.append({
                        'empresa': 'JDJ',
                        'tag': tag,
                        'no_economico': resp.split('(')[0].strip(),
                        'responsable': resp,
                        'placas': placas,
                        'tipo_unidad': unidad or ct,
                        'obra_base': ct_dest or ct,
                        'saldo_anterior': actual,
                        'monto_autorizado': aut,
                        'estatus': estatus.upper()
                    })

for d in jdj_data:
    print(f"JDJ | Tag:{d['tag']:<15} | Resp:{d['responsable']:<30} | Placas:{d['placas']:<10} | Unidad:{d['tipo_unidad']:<18} | Aut:${d['monto_autorizado']:>8.2f} | Obra:{d['obra_base']}")

# TRD
print("\n=== TRD AUTORIZACIONES DETALLADAS DEL PDF ===")
trd_data = []
with pdfplumber.open('TAGS/aurotirzaciones/AUTORIZACION TAG TRD.pdf') as pdf:
    for p in pdf.pages:
        for t in p.extract_tables():
            for r in t:
                cleaned = [str(c or '').replace('\n', ' ').strip() for c in r]
                if cleaned and cleaned[0].isdigit():
                    no = cleaned[0]
                    tag = cleaned[1].replace('..', '').strip()
                    ct = cleaned[2]
                    placas = cleaned[3]
                    unidad = cleaned[4]
                    resp = cleaned[5]
                    clase = cleaned[6]
                    estatus = cleaned[7]
                    saldo = parse_num(cleaned[8])
                    aut = parse_num(cleaned[9])
                    
                    trd_data.append({
                        'empresa': 'TRD',
                        'tag': tag,
                        'no_economico': resp or unidad,
                        'responsable': resp or unidad,
                        'placas': placas if placas != 'NULL' else '',
                        'tipo_unidad': unidad if unidad != 'NULL' else '',
                        'obra_base': 'TRITURADORA ROCA DURA',
                        'saldo_anterior': saldo,
                        'monto_autorizado': aut,
                        'estatus': estatus.upper()
                    })

for d in trd_data:
    print(f"TRD | Tag:{d['tag']:<15} | Resp:{d['responsable']:<30} | Placas:{d['placas']:<10} | Unidad:{d['tipo_unidad']:<18} | Aut:${d['monto_autorizado']:>8.2f} | Estatus:{d['estatus']}")
