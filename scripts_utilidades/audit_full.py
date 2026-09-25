import sqlite3
import pandas as pd
db = sqlite3.connect('c:/Users/JOSE/Desktop/Proyecto fenix/fenix_v2.db')

# Check diesel semana breakdown
print('=== DIESEL por Semana ===')
rows = db.execute("""
SELECT semana, origen, COUNT(*) as cnt, 
       SUM(litros) as total_lts, SUM(importe_total) as total_imp
FROM diesel_consumos
GROUP BY semana, origen
ORDER BY semana
""").fetchall()
for r in rows:
    print(f"  Sem:{r[0]} | Origen:{r[1]} | Registros:{r[2]} | Litros:{r[3]:.0f} | Importe:")

# Check catalogos
print('\n=== CATALOGOS ===')
obras = db.execute('SELECT COUNT(*) FROM catalogos_obras').fetchone()[0]
equipos = db.execute('SELECT COUNT(*) FROM catalogos_equipos').fetchone()[0]
operadores = db.execute('SELECT COUNT(*) FROM catalogos_operadores').fetchone()[0]
ops = db.execute('SELECT COUNT(*) FROM catalogos_operaciones').fetchone()[0]
print(f'  Obras: {obras} | Equipos: {equipos} | Operadores: {operadores} | Operaciones: {ops}')

# Check the 2 invoices
print('\n=== FACTURAS en BD ===')
facs = db.execute("SELECT folio_conciliacion, fecha, obra_destino, litros, importe_total FROM diesel_consumos WHERE origen='FACTURA'").fetchall()
for f in facs:
    print(f"  {f}")

db.close()
