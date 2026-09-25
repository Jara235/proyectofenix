import re

with open('dashboard_fenix.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_gasolina = '''# ─────────────────────────────────────────────────
#  GASOLINA (Modelo Matriz)
# ─────────────────────────────────────────────────
@app.route("/api/gasolina/kpis")
def api_gasolina_kpis():
    db = get_db(); cur = db.cursor()
    sem = semana_param()
    
    # Presupuesto Autorizado Total
    sql_aut = "SELECT ROUND(SUM(monto_autorizado),2) as importe_aut FROM fenix_gas_presupuestos"
    sql_aut, p_aut = q_filter(sql_aut, "semana", sem)
    cur.execute(sql_aut, p_aut)
    aut = dict(cur.fetchone())
    
    # Consumo Reportado (Matriz Excel)
    sql_rep = "SELECT ROUND(SUM(monto_reportado),2) as importe_rep FROM fenix_gas_reportes_diarios r JOIN fenix_gas_presupuestos p ON r.presupuesto_id = p.id"
    sql_rep, p_rep = q_filter(sql_rep, "p.semana", sem)
    cur.execute(sql_rep, p_rep)
    rep = dict(cur.fetchone())
    
    # Consumo Real (Tickets Gasolinera)
    sql_real = "SELECT ROUND(SUM(litros),1) as lts_real, ROUND(SUM(importe),2) as importe_real FROM fenix_gas_tickets_reales"
    sql_real, p_real = q_filter(sql_real, "semana", sem)
    cur.execute(sql_real, p_real)
    real = dict(cur.fetchone())
    
    db.close()
    return jsonify({
        "importe_autorizado": aut["importe_aut"] or 0,
        "importe_reportado": rep["importe_rep"] or 0,
        "litros_real": real["lts_real"] or 0,
        "importe_real": real["importe_real"] or 0
    })

@app.route("/api/gasolina/matriz")
def api_gasolina_matriz():
    db = get_db(); cur = db.cursor()
    sem = semana_param()
    
    # Traer todos los presupuestos
    sql_p = "SELECT id, responsable, obra, unidad, placa, ROUND(monto_autorizado,2) as autorizado FROM fenix_gas_presupuestos"
    sql_p, p_p = q_filter(sql_p, "semana", sem)
    cur.execute(sql_p, p_p)
    presupuestos = [dict(r) for r in cur.fetchall()]
    
    # Traer todos los reportes diarios
    sql_r = "SELECT r.presupuesto_id, r.fecha, r.proveedor, ROUND(r.monto_reportado,2) as monto FROM fenix_gas_reportes_diarios r JOIN fenix_gas_presupuestos p ON p.id = r.presupuesto_id"
    sql_r, p_r = q_filter(sql_r, "p.semana", sem)
    cur.execute(sql_r + " ORDER BY r.fecha", p_r)
    reportes = [dict(r) for r in cur.fetchall()]
    
    # Agrupar reportes en presupuestos
    # Estructura: presupuesto -> fecha -> proveedor -> monto
    from collections import defaultdict
    fechas_unicas = set()
    for p in presupuestos:
        p["dias"] = defaultdict(lambda: {"LEVET": 0, "MOBILE": 0, "SIVALE": 0})
    
    # Crear un diccionario para busqueda rápida
    p_dict = {p["id"]: p for p in presupuestos}
    
    for r in reportes:
        pid = r["presupuesto_id"]
        fecha = r["fecha"]
        prov = r["proveedor"]
        fechas_unicas.add(fecha)
        if pid in p_dict:
            p_dict[pid]["dias"][fecha][prov] += r["monto"]
            
    # Formatear la matriz
    fechas_ordenadas = sorted(list(fechas_unicas))
    
    # Agrupar por responsable
    matriz_final = []
    
    # Sort presupuestos by responsable
    presupuestos.sort(key=lambda x: str(x["responsable"]))
    
    for p in presupuestos:
        dias_list = []
        for f in fechas_ordenadas:
            dias_list.append({
                "fecha": f,
                "levet": p["dias"][f]["LEVET"],
                "mobile": p["dias"][f]["MOBILE"],
                "sivale": p["dias"][f]["SIVALE"]
            })
        p["dias"] = dias_list
        matriz_final.append(p)
        
    db.close()
    return jsonify({
        "fechas": fechas_ordenadas,
        "filas": matriz_final
    })

@app.route("/api/gasolina/conciliacion")
def api_gasolina_conciliacion():
    # Compara Matriz Excel vs Tickets Gasolinera
    db = get_db(); cur = db.cursor()
    sem = semana_param()
    
    # Agrupar Excel por Fecha y Proveedor y Placa
    sql_excel = """
    SELECT r.fecha, r.proveedor, p.placa, ROUND(SUM(r.monto_reportado),2) as monto_excel
    FROM fenix_gas_reportes_diarios r
    JOIN fenix_gas_presupuestos p ON p.id = r.presupuesto_id
    WHERE (p.semana = ? OR ? IS NULL) AND p.placa IS NOT NULL AND p.placa != ''
    GROUP BY r.fecha, r.proveedor, p.placa
    """
    cur.execute(sql_excel, (sem, sem))
    excel_data = [dict(r) for r in cur.fetchall()]
    
    # Agrupar Tickets por Fecha, Proveedor y Placa
    sql_tickets = """
    SELECT fecha, gasolinera as proveedor, placa, ROUND(SUM(importe),2) as monto_ticket
    FROM fenix_gas_tickets_reales
    WHERE (semana = ? OR ? IS NULL) AND placa IS NOT NULL AND placa != ''
    GROUP BY fecha, gasolinera, placa
    """
    cur.execute(sql_tickets, (sem, sem))
    ticket_data = [dict(r) for r in cur.fetchall()]
    
    # Cruzar datos
    from collections import defaultdict
    cross = defaultdict(lambda: {"monto_excel": 0, "monto_ticket": 0})
    
    for e in excel_data:
        key = f"{e['fecha']}|{e['proveedor']}|{e['placa']}"
        cross[key]["monto_excel"] += e["monto_excel"]
        
    for t in ticket_data:
        key = f"{t['fecha']}|{t['proveedor']}|{t['placa']}"
        cross[key]["monto_ticket"] += t["monto_ticket"]
        
    alertas = []
    for key, val in cross.items():
        diff = val["monto_ticket"] - val["monto_excel"]
        if abs(diff) > 10:  # Margen de 10 pesos
            f, prov, pl = key.split("|")
            alertas.append({
                "fecha": f,
                "proveedor": prov,
                "placa": pl,
                "monto_excel": val["monto_excel"],
                "monto_ticket": val["monto_ticket"],
                "diferencia": diff
            })
            
    # Ordenar por diferencia absoluta descendente
    alertas.sort(key=lambda x: abs(x["diferencia"]), reverse=True)
    db.close()
    
    return jsonify(alertas)
'''

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

    # 2. Gasolina por semana (Ahora desde fenix_gas_tickets_reales)
    cur.execute("""SELECT semana, ROUND(SUM(litros),1) as gasolina, ROUND(SUM(importe),2) as gasto_gasolina
                   FROM fenix_gas_tickets_reales
                   WHERE semana IS NOT NULL
                   GROUP BY semana ORDER BY semana""")
    consumos_semana_gasolina = {r['semana']: dict(r) for r in cur.fetchall()}

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

# Reemplazar seccion de gasolina
start_gas = content.find('# ─────────────────────────────────────────────────\n#  GASOLINA')
end_gas = content.find('# ─────────────────────────────────────────────────\n#  ACARREOS')
content = content[:start_gas] + new_gasolina + '\n' + content[end_gas:]

# Reemplazar seccion de totales
start_tot = content.find('@app.route("/api/totales")')
end_tot = content.find('@app.route("/api/kpis")', start_tot)
if end_tot == -1: end_tot = len(content)
content = content[:start_tot] + new_totales + '\n\n' + content[end_tot:]

with open('dashboard_fenix.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Patch complete.')
