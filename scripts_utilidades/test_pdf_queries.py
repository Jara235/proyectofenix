import sys
import os
sys.path.append(r"c:\Users\JOSE\Desktop\Proyecto fenix")
from app_admin import get_db

db = get_db()
cond = "WHERE obra_destino NOT ILIKE %s"
params_base = ['%Tanque Pegaso%']
semana_param = "28"

semana_limpia = str(semana_param).replace('Semana ', '').strip()
cond += " AND semana = %s"
params_base.append(semana_limpia)

params_db = params_base * 3

q_semanas = f"""
    SELECT sem, 
        SUM(sol) as solicitado, 
        SUM(fac) as facturado, 
        SUM(con) as consumido
    FROM (
        SELECT semana::text as sem, SUM(litros) as sol, 0 as fac, 0 as con FROM diesel.solicitudes {cond} GROUP BY semana
        UNION ALL
        SELECT semana::text as sem, 0, SUM(litros_facturados), 0 FROM diesel.facturas {cond} GROUP BY semana
        UNION ALL
        SELECT semana::text as sem, 0, 0, SUM(litros) FROM diesel.consumos {cond} GROUP BY semana
    ) t
    GROUP BY sem
    ORDER BY sem
"""

q_sol_fac = f"""
    SELECT 
        COALESCE(s.obra_destino, f.obra_destino) as obra,
        COALESCE(s.semana::text, f.semana::text) as semana,
        COALESCE(SUM(s.litros), 0) as solicitado,
        COALESCE(SUM(f.litros_facturados), 0) as facturado
    FROM (SELECT * FROM diesel.solicitudes {cond}) s
    FULL OUTER JOIN (SELECT * FROM diesel.facturas {cond}) f 
        ON s.obra_destino = f.obra_destino AND s.semana::text = f.semana::text
    GROUP BY COALESCE(s.obra_destino, f.obra_destino), COALESCE(s.semana::text, f.semana::text)
    ORDER BY semana, obra
"""

try:
    rows = db.execute(q_sol_fac, tuple(params_base * 2)).fetchall()
    print("q_sol_fac returned", len(rows), "rows")
except Exception as e:
    print(f"q_sol_fac ERROR: {e}")

q_sol_con = f"""
    SELECT 
        COALESCE(s.obra_destino, c.obra_destino) as obra,
        COALESCE(s.semana::text, c.semana::text) as semana,
        COALESCE(SUM(s.litros), 0) as solicitado,
        COALESCE(SUM(c.litros), 0) as consumido
    FROM (SELECT * FROM diesel.solicitudes {cond}) s
    FULL OUTER JOIN (SELECT * FROM diesel.consumos {cond}) c 
        ON s.obra_destino = c.obra_destino AND s.semana::text = c.semana::text
    GROUP BY COALESCE(s.obra_destino, c.obra_destino), COALESCE(s.semana::text, c.semana::text)
    ORDER BY semana, obra
"""

try:
    rows = db.execute(q_sol_con, tuple(params_base * 2)).fetchall()
    print("q_sol_con returned", len(rows), "rows")
except Exception as e:
    print(f"q_sol_con ERROR: {e}")

