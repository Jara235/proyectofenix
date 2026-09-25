import urllib.request
import json
url = "http://127.0.0.1:5002/api/admin/resumen/responsables?modulo=diesel&semana=28"
req = urllib.request.Request(url)
try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        print(f"Data for week 28: {len(data)} items")
        print(data)
except Exception as e:
    print(f"Error: {e}")
