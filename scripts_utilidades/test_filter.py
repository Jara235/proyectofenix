import urllib.request, json
for sem in ['Semana 26', 'Semana 27', '']:
    url = 'http://127.0.0.1:5000/api/kpis?semana=' + sem.replace(' ','%20')
    d = json.loads(urllib.request.urlopen(url).read())
    dl = d['diesel']['litros']
    gr = d['gasolina']['registros']
    print(f"sem={sem!r:15}  diesel_lts={dl:.0f}  gas_regs={gr}")
