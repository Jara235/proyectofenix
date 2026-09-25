import re
with open('dashboard_fenix.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_totales = '''@app.route("/api/totales")
def api_totales():
    db = get_db(); cur = db.cursor()
    sem = semana_param()

    # 1. Diesel por semana
    cur.execute("""SELECT semana,
                          ROUND(SUM(CASE WHEN tipo_combustible='Diesel' THEN litros ELSE 0 END),1) as diesel
                   FROM fenix_movimientos_combustible
                   WHERE tipo_movimiento='CONSUMO' AND semana IS NOT NULL
                   GROUP BY semana ORDER BY semana""")
    consumos_semana_diesel = {r['semana']: dict(r) for r in cur.fetchall()}

    # 2. Gasolina por semana
    cur.execute("""SELECT semana, ROUND(SUM(litros),1) as gasolina, ROUND(SUM(importe),2) as gasto_gasolina
                   FROM fenix_gasolina_consumos
                   WHERE semana IS NOT NULL
                   GROUP BY semana ORDER BY semana""")
    consumos_semana_gasolina = {r['semana']: dict(r) for r in cur.fetchall()}

    # Combine consumos_semana
    all_weeks = sorted(list(set(list(consumos_semana_diesel.keys()) + list(consumos_semana_gasolina.keys()))))
    consumos_semana = []
    for w in all_weeks:
        d = consumos_semana_diesel.get(w, {'diesel': 0})
        g = consumos_semana_gasolina.get(w, {'gasolina': 0, 'gasto_gasolina': 0})
        consumos_semana.append({
            'semana': w,
            'diesel': d.get('diesel', 0),
            'gasolina': g.get('gasolina', 0),
            'gasto_gasolina': g.get('gasto_gasolina', 0)
        })

    # Acarreos por semana
    cur.execute("""SELECT semana, ROUND(SUM(total),2) as acarreos, COUNT(*) as viajes
                   FROM fenix_viajes_acarreo WHERE semana IS NOT NULL
                   GROUP BY semana ORDER BY semana""")
    acarreos_semana = [dict(r) for r in cur.fetchall()]

    # Facturas validadas totales
    cur.execute("""SELECT tipo_combustible,
                          COUNT(*) as facturas,
                          ROUND(SUM(litros_totales),1) as litros,
                          ROUND(SUM(total),2) as monto
                   FROM fenix_facturas_documentos
                   WHERE estatus_validacion='VALIDADA'
                   GROUP BY tipo_combustible""")
    facturas_resumen = [dict(r) for r in cur.fetchall()]

    db.close()
    return jsonify({
        "consumos_por_semana": consumos_semana,
        "acarreos_por_semana": acarreos_semana,
        "facturas_resumen": facturas_resumen
    })
'''

start_idx = content.find('@app.route("/api/totales")')
if start_idx != -1:
    end_idx = content.find('@app.route("/api/kpis")', start_idx)
    if end_idx == -1: end_idx = len(content)
    new_content = content[:start_idx] + new_totales + '\n' + content[end_idx:]
    with open('dashboard_fenix.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print('Updated dashboard_fenix.py')
else:
    print('Could not find /api/totales')
