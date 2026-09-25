with open(r"c:\Users\JOSE\Desktop\Proyecto fenix\dashboard_fenix_v2.py", "r", encoding="utf-8") as f:
    for line in f:
        if "sqlite3" in line or "get_db" in line or "execute" in line:
            pass # Just to see how many lines we are talking about
