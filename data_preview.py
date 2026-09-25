import pandas as pd
import json

def analyze_file(filepath):
    try:
        xls = pd.ExcelFile(filepath)
        result = {"sheets": {}}
        for sheet in xls.sheet_names:
            try:
                df = pd.read_excel(filepath, sheet_name=sheet, nrows=10, header=None)
                result["sheets"][sheet] = df.to_string()
            except Exception as e:
                result["sheets"][sheet] = f"Error reading: {e}"
        return result
    except Exception as e:
        return {"error": str(e)}

files = {
    "gasolina_consumos": "gasolina/CONSUMOS  DE GASOLINA SEMANALES GT.xlsx",
    "gasolina_provisional": "gasolina/CONTROL JDJ PROVISIONAL semana 27.xlsx"
}

output = {}
for key, path in files.items():
    output[key] = analyze_file(path)

with open("preview_gasolina.txt", "w", encoding="utf-8") as f:
    for key, data in output.items():
        f.write(f"===== {key} =====\n")
        if "error" in data:
            f.write(f"Error: {data['error']}\n")
        else:
            for sheet, content in data["sheets"].items():
                f.write(f"--- Sheet: {sheet} ---\n")
                f.write(content + "\n\n")

print("Analysis saved to preview_gasolina.txt")
