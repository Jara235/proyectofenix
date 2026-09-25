import urllib.request

servers = [
    ("Dashboard Ejecutivo", "http://127.0.0.1:5000"),
    ("Captura Campo", "http://127.0.0.1:5001"),
    ("Administración Fénix", "http://127.0.0.1:5002")
]

for name, url in servers:
    try:
        req = urllib.request.urlopen(url, timeout=5)
        print(f"[OK] {name} ({url}) -> Status {req.getcode()}")
    except Exception as e:
        print(f"[ERROR] {name} ({url}) -> {e}")
