from app_admin import get_db
import json

db = get_db()

# Check what the updated API will return for week 33
# Let's write a sync script for autorizaciones across all weeks first
from extract_s33_clean import parse_sheet_semana
import openpyxl

wb = openpyxl.load_workbook('gasolina/conciliacion_gasolina_google_sheets.xlsx', data_only=True)

for w in ['SEMANA 26', 'SEMANA 27', 'SEMANA 28', 'SEMANA 29', 'SEMANA 30', 'SEMANA 31', 'SEMANA 32', 'SEMANA 33']:
    if w in wb.sheetnames:
        sem_num = int(w.replace('SEMANA ', '').strip())
        personas = parse_sheet_semana(wb[w], sem_num)
        print(f"{w}: {len(personas)} personas extraídas")
