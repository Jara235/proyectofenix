import sys
sys.path.append(r'c:\Users\JOSE\Desktop\Proyecto fenix')
from app_admin import get_db
db = get_db()
try:
    semana_limpia = '28'
    cond_con = "WHERE obra_destino NOT ILIKE '%Tanque Pegaso%' AND estatus_revision = 'APROBADO' AND semana = %s"
    params_con = [semana_limpia]
    q_con = f"""
        SELECT obra_destino as obra, responsable, SUM(litros) as consumido
        FROM diesel.consumos
        {cond_con}
        GROUP BY obra_destino, responsable
    """
    rows_con = db.execute(q_con, tuple(params_con)).fetchall()
    print(f"Consumos found: {len(rows_con)}")
except Exception as e:
    import traceback
    print("Exception in query:", traceback.format_exc())
db.close()
