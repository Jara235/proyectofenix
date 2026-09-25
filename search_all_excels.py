import os, openpyxl, glob

for f in glob.glob("*.xlsx"):
    try:
        wb = openpyxl.load_workbook(f, data_only=True)
        for s in wb.sheetnames:
            ws = wb[s]
            for r in range(1, min(ws.max_row+1, 300)):
                for c in range(1, min(ws.max_column+1, 40)):
                    v = ws.cell(r, c).value
                    if v and ('10922' in str(v) or '4184' in str(v)):
                        print(f"File {f} | Sheet {s} | Row {r}, Col {c}: {v}")
    except Exception as e:
        pass
print("Search across .xlsx done.")
