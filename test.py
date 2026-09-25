import urllib.request, json
data = json.loads(urllib.request.urlopen('http://127.0.0.1:5002/api/admin/jalisco/movimientos').read().decode())
print(data)
