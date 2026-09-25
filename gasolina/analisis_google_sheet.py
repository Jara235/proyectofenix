import json

with open("gasolina/datos_extraidos_gasolina_completo.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print("| Semana | Personas | Autorizado ($) | Consumido ($) | Total Cargas | Excedidos |")
print("|---|---|---|---|---|---|")
for w, d in data.items():
    tot = d["totales"]
    p = tot["personas"]
    a = tot["autorizado"]
    c = tot["consumido"]
    n = tot["cargas_individuales"]
    e = len(tot["excedidos"])
    print(f"| {w} | {p} | ${a:,.2f} | ${c:,.2f} | {n} | {e} personas |")
