import pandas as pd
df = pd.read_excel('c:/Users/JOSE/Desktop/Proyecto fenix/gasolina/SEMANA 26.xlsx', header=1)
print(df.columns.tolist())
print(df[['RESONSABLE', 'CENTRO DE TRABAJO', 'UNIDAD / EQUIPO', 'PLACAS', 'IMPORTE SEMANAL AUTORIZADO']].head(5))

