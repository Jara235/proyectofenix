import openpyxl
from app_admin import get_db
from extract_s33_clean import parse_sheet_semana

wb = openpyxl.load_workbook('gasolina/conciliacion_gasolina_google_sheets.xlsx', data_only=True)
db = get_db()

print("=== RE-SINCRONIZANDO AUTORIZACIONES DESDE GOOGLE SHEETS ===")

db.execute("DELETE FROM gasolina.autorizaciones_semanal")
db.execute("DELETE FROM gasolina.autorizaciones_maestro")

# 1. Base maestro de Semana 33 (48 registros)
s33_personas = parse_sheet_semana(wb['SEMANA 33'], 33)
maestro_map = []
for idx, p in enumerate(s33_personas, 1):
    cur = db.execute("""
        INSERT INTO gasolina.autorizaciones_maestro (
            empresa, num_renglon, responsable, centro_trabajo, unidad_equipo, placas, importe_semanal, activo
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE)
        RETURNING id, empresa, num_renglon, responsable, centro_trabajo, unidad_equipo, placas, importe_semanal
    """, (
        p['empresa'], idx, p['responsable'], p['centro_trabajo'], p['unidad_equipo'], p['placas'], p['importe_semanal']
    ))
    row = cur.fetchone()
    maestro_map.append(row)

print(f"Insertados {len(maestro_map)} registros en gasolina.autorizaciones_maestro.")

# 2. Autorizaciones semanales para cada semana
for w in ['SEMANA 26', 'SEMANA 27', 'SEMANA 28', 'SEMANA 29', 'SEMANA 30', 'SEMANA 31', 'SEMANA 32', 'SEMANA 33']:
    if w in wb.sheetnames:
        sem_num = int(w.replace('SEMANA ', '').strip())
        week_personas = parse_sheet_semana(wb[w], sem_num)
        
        usados_maestro = set()
        for p in week_personas:
            # Buscar maestro_id correspondiente único
            m_id = None
            # 1. Por placa si existe y no usada
            if p['placas']:
                for m in maestro_map:
                    if m['id'] not in usados_maestro and m['placas'] == p['placas']:
                        m_id = m['id']
                        break
            # 2. Por responsable + empresa si no encontrada
            if m_id is None and p['responsable']:
                for m in maestro_map:
                    if m['id'] not in usados_maestro and m['responsable'].upper() == p['responsable'].upper() and m['empresa'] == p['empresa']:
                        m_id = m['id']
                        break
            # 3. Por unidad_equipo + empresa
            if m_id is None and p['unidad_equipo']:
                for m in maestro_map:
                    if m['id'] not in usados_maestro and m['unidad_equipo'].upper() == p['unidad_equipo'].upper() and m['empresa'] == p['empresa']:
                        m_id = m['id']
                        break
            # 4. Cualquier maestro disponible no usado
            if m_id is None:
                for m in maestro_map:
                    if m['id'] not in usados_maestro:
                        m_id = m['id']
                        break
                        
            if m_id is not None:
                usados_maestro.add(m_id)
            
            db.execute("""
                INSERT INTO gasolina.autorizaciones_semanal (
                    semana, maestro_id, empresa, num_renglon, responsable, centro_trabajo, unidad_equipo, placas, importe_semanal
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                sem_num, m_id, p['empresa'], p['num_renglon'], p['responsable'], p['centro_trabajo'], p['unidad_equipo'], p['placas'], p['importe_semanal']
            ))
        print(f"Sincronizada {w} ({len(week_personas)} autorizaciones)")

db.close()
print("Sincronización completa.")
