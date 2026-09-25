import json, sys, os
import psycopg2
from psycopg2.extras import DictCursor

class DbProxy:
    def __init__(self, conn):
        self.conn = conn
    def execute(self, sql, params=()):
        cur = self.conn.cursor(cursor_factory=DictCursor)
        cur.execute(sql, params)
        return cur
    def commit(self):
        self.conn.commit()
    def close(self):
        self.conn.close()

def get_db():
    conn = psycopg2.connect(
        dbname="fenix_db",
        user="postgres",
        password="Bupito*268",
        host="localhost"
    )
    conn.autocommit = True
    return DbProxy(conn)

def run_ingesta():
    db = get_db()
    
    with open('gasolina/datos_extraidos_gasolina_completo.json', 'r', encoding='utf-8') as f:
        sheets_data = json.load(f)
        
    print("=== INICIANDO INGESTA SEGURA DE GASOLINA ===")
    
    # 1. Asegurar catálogo de Obras y Equipos
    cur_obras = db.execute("SELECT nombre FROM catalogos.obras").fetchall()
    obras_existentes = set(r[0] for r in cur_obras if r[0])
    
    cur_equipos = db.execute("SELECT numero_economico FROM catalogos.equipos").fetchall()
    equipos_existentes = set(r[0] for r in cur_equipos if r[0])
    
    for w_name, w_data in sheets_data.items():
        for p in w_data.get('personas', []):
            obra = (p.get('obra') or '').strip()
            placa = (p.get('placas') or '').strip().upper()
            unidad = (p.get('unidad') or '').strip()
            conductor = (p.get('conductor') or '').strip()
            
            if obra and obra not in ['CENTRO DE TRABAJO', 'TOTALES'] and obra not in obras_existentes:
                codigo = obra[:3].upper().replace(' ', '')
                # Ensure unique code
                cod_test = codigo
                idx_c = 1
                while True:
                    chk = db.execute("SELECT 1 FROM catalogos.obras WHERE codigo = %s", (cod_test,)).fetchone()
                    if not chk:
                        break
                    cod_test = f"{codigo[:2]}{idx_c}"
                    idx_c += 1
                    
                db.execute("""
                    INSERT INTO catalogos.obras (codigo, nombre, ingeniero_responsable, responsable_default)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (nombre) DO NOTHING
                """, (cod_test, obra, conductor, conductor))
                obras_existentes.add(obra)
                
            if placa and placa not in ['PLACAS', 'S/P'] and placa not in equipos_existentes:
                db.execute("""
                    INSERT INTO catalogos.equipos (numero_economico, descripcion, tipo_equipo, operador_default)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (numero_economico) DO NOTHING
                """, (placa, unidad or 'Vehículo', 'GASOLINA', conductor))
                equipos_existentes.add(placa)

    print("Catálogos de obras y equipos actualizados.")
    
    # 2. Plantilla base (Semana 33 o 30)
    plantilla_base = sheets_data.get('SEMANA 33', {}).get('personas', [])
    if not plantilla_base:
        plantilla_base = sheets_data.get('SEMANA 30', {}).get('personas', [])
        
    print(f"Plantilla base: {len(plantilla_base)} personas/unidades")
    
    # Sincronizar autorizaciones_maestro
    db.execute("DELETE FROM gasolina.autorizaciones_semanal")
    db.execute("DELETE FROM gasolina.autorizaciones_maestro")
    
    maestro_map = []
    for idx, p in enumerate(plantilla_base, 1):
        cur = db.execute("""
            INSERT INTO gasolina.autorizaciones_maestro (
                empresa, num_renglon, responsable, centro_trabajo, unidad_equipo, placas, importe_semanal, activo
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE)
            RETURNING id, empresa, num_renglon, responsable, centro_trabajo, unidad_equipo, placas, importe_semanal
        """, (
            p['empresa'], idx, p['conductor'], p['obra'], p['unidad'], p['placas'], p['autorizado']
        ))
        row = cur.fetchone()
        maestro_map.append(row)
    
    print(f"Insertados {len(maestro_map)} registros en gasolina.autorizaciones_maestro.")
    
    # Sincronizar autorizaciones_semanal para cada semana
    for w_name, w_data in sheets_data.items():
        sem_num = w_data['semana']
        week_personas = w_data.get('personas', [])
        
        for m in maestro_map:
            monto_sem = float(m['importe_semanal'])
            obra_sem = m['centro_trabajo']
            
            for wp in week_personas:
                if (m['placas'] and wp['placas'] and m['placas'].strip().upper() == wp['placas'].strip().upper()) or \
                   (m['responsable'] and wp['conductor'] and m['responsable'].strip().upper() == wp['conductor'].strip().upper() and m['unidad_equipo'].strip().upper() == wp['unidad'].strip().upper()):
                    monto_sem = float(wp['autorizado'])
                    obra_sem = wp['obra'] or m['centro_trabajo']
                    break
                    
            db.execute("""
                INSERT INTO gasolina.autorizaciones_semanal (
                    semana, maestro_id, empresa, num_renglon, responsable, centro_trabajo, unidad_equipo, placas, importe_semanal
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                sem_num, m['id'], m['empresa'], m['num_renglon'], m['responsable'], obra_sem, m['unidad_equipo'], m['placas'], monto_sem
            ))
            
    print("Sincronizadas autorizaciones_semanal para todas las semanas.")
    
    # 3. Ingestar consumos
    consumos_db = db.execute("SELECT id, semana, fecha, conductor, placa, importe_total, gasolineria, foto_evidencia IS NOT NULL as tiene_foto FROM gasolina.consumos").fetchall()
    
    total_insertadas = 0
    total_preservadas = 0
    
    for w_name, w_data in sheets_data.items():
        sem_num = str(w_data['semana'])
        db_semana = [c for c in consumos_db if str(c['semana']) == sem_num]
        
        for p in w_data.get('personas', []):
            conductor = p['conductor']
            obra = (p.get('obra') or '').strip()
            if not obra or obra in ['CENTRO DE TRABAJO', 'TOTALES']:
                obra = None
                
            unidad = p['unidad']
            placa = (p.get('placas') or '').strip().upper()
            if not placa or placa in ['PLACAS', 'S/P']:
                placa = None
                
            for carga in p.get('detalle_cargas', []):
                fecha_carga = carga['fecha']
                gasolinera = carga['gasolinera']
                monto = float(carga['importe'])
                folio = carga.get('folio', '')
                
                costo_litro = 23.90
                litros = round(monto / costo_litro, 2)
                
                match_existente = False
                for c_db in db_semana:
                    if str(c_db['fecha']) == fecha_carga:
                        monto_db = float(c_db['importe_total'] or 0)
                        if abs(monto_db - monto) < 1.0:
                            if c_db['tiene_foto']:
                                match_existente = True
                                total_preservadas += 1
                                break
                            elif (c_db['placa'] and placa and c_db['placa'].strip().upper() == placa) or \
                                 (c_db['conductor'] and conductor and c_db['conductor'].strip().upper() == conductor.strip().upper()):
                                match_existente = True
                                break
                
                if not match_existente:
                    folio_con = f"GAS-S{sem_num}-{fecha_carga.replace('-','')}-{idx_c}"
                    idx_c += 1
                    if folio:
                        folio_con = f"GAS-S{sem_num}-{folio}"
                        
                    db.execute("""
                        INSERT INTO gasolina.consumos (
                            folio_conciliacion, fecha, semana, origen, obra_destino, vehiculo, placa,
                            kilometraje, litros, costo_por_litro, importe_total, conductor, observaciones,
                            estatus_revision, gasolineria, usuario_captura
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s,
                            0, %s, %s, %s, %s, %s,
                            'APROBADO', %s, 'SISTEMA_IMPORTACION'
                        )
                    """, (
                        folio_con, fecha_carga, sem_num, 'IMPORTACION_EXCEL', obra, unidad, placa,
                        litros, costo_litro, monto, conductor, f"Carga {gasolinera} {folio}".strip(),
                        gasolinera
                    ))
                    total_insertadas += 1
    
    print(f"\n=== INGESTA CONCLUIDA EXITOSAMENTE ===")
    print(f"  Total cargas preservadas intactas (con foto / existentes): {total_preservadas}")
    print(f"  Total cargas insertadas: {total_insertadas}")
    
    res = db.execute("""
        SELECT semana, count(*) as total, count(foto_evidencia) as con_foto, sum(importe_total) as monto_total
        FROM gasolina.consumos
        GROUP BY semana
        ORDER BY CAST(semana AS INTEGER)
    """).fetchall()
    print("\nEstado actual en PostgreSQL (gasolina.consumos):")
    for r in res:
        print(f"  Semana {r['semana']:2s}: {r['total']:3d} cargas | {r['con_foto']:2d} con foto | Total: ${float(r['monto_total']):,.2f}")
        
    db.close()

if __name__ == '__main__':
    run_ingesta()
