import pdfplumber
with pdfplumber.open('c:/Users/JOSE/Desktop/Proyecto fenix/facturas/Diesel/Semana_25/2c6f01d9-fdba-4376-8cef-ed0d989e49df.pdf') as pdf:
    text = pdf.pages[0].extract_text()
    print('--- PDF TEXT START ---')
    print(text[:1000])
    print('--- PDF TEXT END ---')

