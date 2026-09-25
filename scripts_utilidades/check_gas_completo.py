import sqlite3
import pandas as pd
db = r'c:\Users\JOSE\Desktop\Proyecto fenix\fenix_v2.db'
c = sqlite3.connect(db)

df = pd.read_sql("SELECT * FROM gasolina_consumos WHERE semana='Semana 26' ORDER BY origen, fecha", c)
print("=== RESUMEN CRITICO POR ORIGEN ===")
resumen = df.groupby('origen').agg(
    registros=('id','count'),
    litros=('litros','sum'),
    importe=('importe_total','sum'),
    regs_sin_litros=('litros', lambda x: (x==0).sum()),
    regs_sin_importe=('importe_total', lambda x: (x==0).sum())
).reset_index()
print(resumen.to_string())

print()
print("=== REGS CON LITROS Y SIN IMPORTE (datos incompletos) ===")
incompl = df[(df['litros']>0) & (df['importe_total']==0)]
print(f"  Total: {len(incompl)} registros, {incompl['litros'].sum():.0f} litros SIN importe")

print()
print("=== REGS CON IMPORTE Y SIN LITROS (datos incompletos) ===")
incompl2 = df[(df['importe_total']>0) & (df['litros']==0)]
print(f"  Total: {len(incompl2)} registros, importes:  SIN litros")
print(incompl2[['fecha','placa','vehiculo','obra_destino','origen','litros','importe_total']].to_string())

c.close()
