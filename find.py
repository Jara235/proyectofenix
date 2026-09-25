with open('dashboard_fenix.py', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if 'def api_gasolina' in line or '@app.route("/api/gasolina' in line:
            print(f'{i+1}: {line.strip()}')
