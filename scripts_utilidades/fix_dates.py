import sqlite3, re
db = sqlite3.connect('c:/Users/JOSE/Desktop/Proyecto fenix/fenix.db')
c = db.cursor()
c.execute('SELECT id, fecha_emision, nota_leyenda FROM fenix_facturas_documentos')
rows = c.fetchall()
for row in rows:
    fid, fecha, leyenda = row
    leyenda = leyenda.lower() if leyenda else ''
    real_date = fecha[:10] if fecha else '2000-01-01'
    # find all dates
    dates = re.findall(r'(\d{2})[-/](\d{2})[-/](\d{2,4})', leyenda)
    for d, m, y in dates:
        if len(y) == 2: y = '20' + y
        if y == '2026':
            real_date = f'{y}-{m}-{d}'
            break
    week = 0
    if '2026-06-15' <= real_date <= '2026-06-21': week = 25
    elif '2026-06-22' <= real_date <= '2026-06-28': week = 26
    elif '2026-06-29' <= real_date <= '2026-07-05': week = 27
    else:
        try:
            from datetime import datetime
            week = datetime.strptime(real_date, '%Y-%m-%d').isocalendar()[1]
        except: pass
    c.execute('UPDATE fenix_facturas_documentos SET semana=? WHERE id=?', (week, fid))
db.commit()
c.execute("SELECT semana, COUNT(*), ROUND(SUM(litros_totales),1), ROUND(SUM(total),2) FROM fenix_facturas_documentos WHERE tipo_combustible='Diesel' GROUP BY semana")
print('Resumen Corregido:')
for r in c.fetchall(): print('Semana', r[0], ':', r[1], 'facturas,', r[2], 'Lts, $', r[3])
db.close()

