import os, glob
pdfs = glob.glob('c:/Users/JOSE/Desktop/Proyecto fenix/**/*.pdf', recursive=True)
print([p for p in pdfs if '2c6f' in p or 'Semana_25' in p][:5])

