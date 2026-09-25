with open(r"c:\Users\JOSE\Desktop\Proyecto fenix\app_captura.py", "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if "estado_cuenta" in line.lower() or "estados_cuenta" in line.lower():
            print(f"Line {i}: {line.strip()}")
