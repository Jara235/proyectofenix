with open(r"c:\Users\JOSE\Desktop\Proyecto fenix\app_captura.py", "r", encoding="utf-8") as f:
    for line in f:
        if "DB_PATH" in line:
            print(line.strip())
