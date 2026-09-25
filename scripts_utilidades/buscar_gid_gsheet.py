import openpyxl, zipfile, xml.etree.ElementTree as ET

# Para encontrar los sheetIds (gid) en el archivo xlsx descargado:
with zipfile.ZipFile('gasolina/conciliacion_gasolina_google_sheets.xlsx', 'r') as z:
    with z.open('xl/workbook.xml') as f:
        tree = ET.parse(f)
        root = tree.getroot()
        # namespaces
        ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
              'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
        sheets = root.findall('main:sheets/main:sheet', ns)
        print("=== Mapeo de Hojas y sheetId (gid) ===")
        for s in sheets:
            name = s.attrib.get('name')
            sheet_id = s.attrib.get('sheetId')
            r_id = s.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
            print(f"Sheet: '{name}' -> sheetId: {sheet_id}")
