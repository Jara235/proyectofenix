import os
folder = 'c:/Users/JOSE/Desktop/Proyecto fenix/facturas'
pdfs = set(f.replace('.pdf', '') for f in os.listdir(folder) if f.endswith('.pdf'))
xmls = set(f.replace('.xml', '') for f in os.listdir(folder) if f.endswith('.xml'))
missing_xmls = pdfs - xmls
print('PDFs without XML:', sorted(list(missing_xmls)))

