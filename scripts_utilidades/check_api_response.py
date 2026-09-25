import urllib.request
import json

try:
    url = "http://127.0.0.1:5002/api/admin/resumen/responsables?modulo=diesel&semana=28"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode('utf-8'))
        for r in data:
            print(f"{r['responsable']}: {r['autorizado']}")
except Exception as e:
    print(e)
