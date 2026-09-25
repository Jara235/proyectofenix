import urllib.request
import os

url = "https://docs.google.com/spreadsheets/d/1Er1qP6Gt1pwNmTXmOVLEpaY_cpbGlLUg/export?format=xlsx"
dest_path = "gasolina/conciliacion_gasolina_google_sheets.xlsx"

print("Downloading latest Google Sheet...")
headers = {'User-Agent': 'Mozilla/5.0'}
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req) as response:
    content = response.read()
    print(f"Downloaded {len(content)} bytes.")
    with open(dest_path, 'wb') as f:
        f.write(content)

print(f"Saved to {dest_path}")
