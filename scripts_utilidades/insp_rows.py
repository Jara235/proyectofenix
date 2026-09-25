import sqlite3
conn = sqlite3.connect(r'c:\Users\JOSE\Desktop\Proyecto fenix\fenix.db')
cur = conn.cursor()
tables = ['fenix_gas_presupuestos', 'fenix_gas_reportes_diarios', 'fenix_gas_tickets_reales', 'fenix_gasolina_autorizaciones', 'fenix_gasolina_consumos', 'fenix_facturas_combustible']
for t in tables:
    try:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        print(f"{t}: {cur.fetchone()[0]} rows")
    except:
        print(f"{t}: Error or does not exist")
