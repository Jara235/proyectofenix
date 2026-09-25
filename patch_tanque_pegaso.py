import re

file = r"c:\Users\JOSE\Desktop\Proyecto fenix\app_admin.py"
with open(file, 'r', encoding='utf-8') as f:
    content = f.read()

# PATCH PDF ROUTE
old_pdf_cond = """        # -- CONSULTA DE DATOS -------------------------------------------------
        cond = ""
        params_db = []
        semana_num = None
        if semana_param != 'TODOS':
            # Ya est limpio el DB, usamos comparacin exacta
            semana_limpia = str(semana_param).replace('Semana ', '').strip()
            cond = "WHERE semana = %s"
            params_db = [semana_limpia, semana_limpia, semana_limpia]"""

new_pdf_cond = """        # -- CONSULTA DE DATOS -------------------------------------------------
        cond = "WHERE obra_destino NOT ILIKE %s"
        params_base = ['%Tanque Pegaso%']
        semana_num = None
        if semana_param != 'TODOS':
            # Ya est limpio el DB, usamos comparacin exacta
            semana_limpia = str(semana_param).replace('Semana ', '').strip()
            cond += " AND semana = %s"
            params_base.append(semana_limpia)
        
        params_db = params_base * 3"""

content = content.replace(old_pdf_cond, new_pdf_cond)

# Patch rows_sem execute
content = content.replace("rows_sem = db.execute(q_semanas, tuple(params_db)).fetchall() if params_db else db.execute(q_semanas).fetchall()", 
                          "rows_sem = db.execute(q_semanas, tuple(params_db)).fetchall()")

# Patch rows_sf execute
content = content.replace("rows_sf = db.execute(q_sol_fac, tuple(params_db[:2])).fetchall() if params_db else db.execute(q_sol_fac).fetchall()", 
                          "rows_sf = db.execute(q_sol_fac, tuple(params_base * 2)).fetchall()")

# Patch rows_sc execute
content = content.replace("rows_sc = db.execute(q_sol_con, tuple(params_db[:2])).fetchall() if params_db else db.execute(q_sol_con).fetchall()", 
                          "rows_sc = db.execute(q_sol_con, tuple(params_base * 2)).fetchall()")


# PATCH RESUMEN CONCILIACION
old_res_cond = """    cond = ""
    params = []
    # Extract numeric week for autorizaciones (stored as integer)
    semana_num = None
    if semana != 'TODOS':
        cond = "WHERE semana = %s"
        params.extend([semana, semana, semana])
        try:
            semana_num = int(semana.replace('Semana ', '').strip())
        except:
            semana_num = None"""

new_res_cond = """    cond = "WHERE obra_destino NOT ILIKE %s"
    params_base = ['%Tanque Pegaso%']
    # Extract numeric week for autorizaciones (stored as integer)
    semana_num = None
    if semana != 'TODOS':
        semana_limpia = str(semana).replace('Semana ', '').strip()
        cond += " AND semana = %s"
        params_base.append(semana_limpia)
        try:
            semana_num = int(semana_limpia)
        except:
            semana_num = None
            
    params = params_base * 3"""

content = content.replace(old_res_cond, new_res_cond)

# Patch rows execute
content = content.replace("rows = db.execute(query, tuple(params)).fetchall() if params else db.execute(query).fetchall()", 
                          "rows = db.execute(query, tuple(params)).fetchall()")

with open(file, 'w', encoding='utf-8') as f:
    f.write(content)

print("Patch applied successfully.")
