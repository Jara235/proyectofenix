import os

file_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\app_admin.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the location of `if __name__ == '__main__':`
idx = content.rfind("if __name__ == '__main__':")

new_api = """@app.route('/api/admin/resumen/conciliacion')
def api_resumen_conciliacion():
    db = get_db()
    modulo = request.args.get('modulo', 'diesel')
    semana = request.args.get('semana', 'TODOS')
    
    cond = ""
    params = []
    if semana != 'TODOS':
        # we will extract just the number if it contains "Semana"
        sem_num = semana.replace('Semana ', '').strip()
        cond = "WHERE semana = %s"
        params.extend([sem_num, sem_num, sem_num])
        
    if modulo == 'diesel':
        query = f\"\"\"
        WITH sol AS (
            SELECT obra_destino, fecha, SUM(litros) as solicitado
            FROM diesel.solicitudes
            {cond.replace('semana', 'semana')}
            GROUP BY obra_destino, fecha
        ),
        con AS (
            SELECT obra_destino, fecha, SUM(litros) as consumido
            FROM diesel.consumos
            {cond.replace('semana', 'semana')}
            GROUP BY obra_destino, fecha
        ),
        fac AS (
            SELECT c.obra_destino, c.fecha, SUM(f.litros_facturados) as facturado
            FROM diesel.facturas f
            LEFT JOIN (SELECT DISTINCT folio_conciliacion, obra_destino, fecha FROM diesel.consumos) c 
              ON f.folio_conciliacion = c.folio_conciliacion
            {cond.replace('semana', 'f.semana')}
            GROUP BY c.obra_destino, c.fecha
        ),
        fechas_obras AS (
            SELECT obra_destino, fecha FROM sol
            UNION
            SELECT obra_destino, fecha FROM con
            UNION
            SELECT obra_destino, fecha FROM fac
        )
        SELECT 
            fo.obra_destino as obra,
            TO_CHAR(fo.fecha, 'YYYY-MM-DD') as fecha,
            COALESCE(s.solicitado, 0) as solicitado,
            COALESCE(c.consumido, 0) as consumido,
            COALESCE(f.facturado, 0) as facturado
        FROM fechas_obras fo
        LEFT JOIN sol s ON fo.obra_destino = s.obra_destino AND (fo.fecha = s.fecha OR (fo.fecha IS NULL AND s.fecha IS NULL))
        LEFT JOIN con c ON fo.obra_destino = c.obra_destino AND (fo.fecha = c.fecha OR (fo.fecha IS NULL AND c.fecha IS NULL))
        LEFT JOIN fac f ON fo.obra_destino = f.obra_destino AND (fo.fecha = f.fecha OR (fo.fecha IS NULL AND f.fecha IS NULL))
        WHERE fo.obra_destino IS NOT NULL
        ORDER BY fo.obra_destino, fo.fecha DESC
        \"\"\"
        try:
            rows = db.execute(query, tuple(params) if params else ()).fetchall()
            db.close()
            return jsonify([dict(r) for r in rows])
        except Exception as e:
            print("ERROR SQL DIESEL:", e)
            db.close()
            return jsonify([])
            
    elif modulo == 'gasolina':
        if params: params.pop() # only 2 queries for gasolina
        query = f\"\"\"
        WITH con AS (
            SELECT obra_destino, fecha, SUM(litros) as consumido
            FROM gasolina.consumos
            {cond.replace('semana', 'semana')}
            GROUP BY obra_destino, fecha
        ),
        fac AS (
            SELECT c.obra_destino, c.fecha, SUM(f.litros_facturados) as facturado
            FROM gasolina.facturas f
            LEFT JOIN (SELECT DISTINCT folio_conciliacion, obra_destino, fecha FROM gasolina.consumos) c 
              ON f.folio_conciliacion = c.folio_conciliacion
            {cond.replace('semana', 'f.semana')}
            GROUP BY c.obra_destino, c.fecha
        ),
        fechas_obras AS (
            SELECT obra_destino, fecha FROM con
            UNION
            SELECT obra_destino, fecha FROM fac
        )
        SELECT 
            fo.obra_destino as obra,
            TO_CHAR(fo.fecha, 'YYYY-MM-DD') as fecha,
            0 as solicitado,
            COALESCE(c.consumido, 0) as consumido,
            COALESCE(f.facturado, 0) as facturado
        FROM fechas_obras fo
        LEFT JOIN con c ON fo.obra_destino = c.obra_destino AND (fo.fecha = c.fecha OR (fo.fecha IS NULL AND c.fecha IS NULL))
        LEFT JOIN fac f ON fo.obra_destino = f.obra_destino AND (fo.fecha = f.fecha OR (fo.fecha IS NULL AND f.fecha IS NULL))
        WHERE fo.obra_destino IS NOT NULL
        ORDER BY fo.obra_destino, fo.fecha DESC
        \"\"\"
        try:
            rows = db.execute(query, tuple(params) if params else ()).fetchall()
            db.close()
            return jsonify([dict(r) for r in rows])
        except Exception as e:
            print("ERROR SQL GASOLINA:", e)
            db.close()
            return jsonify([])
    
    db.close()
    return jsonify([])

"""

new_content = content[:idx] + new_api + content[idx:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("API appended.")
