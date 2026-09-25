"""
motor_agente_conciliacion.py - Agente de IA para Auditoría y Conciliación Forense de Combustibles
Sistema Fénix 2.0 - Grupo Trujano

Estructura de 3 Filtros:
1. Filtro 1 (Campo): Entrega-Recepción (Conductor Marimba / Camión 3½ Ton vs Operador Maquinaria).
2. Filtro 2 (Frente de Obra): Verificación y Firma del Ingeniero Residente (Carga Total Obra vs Factura).
3. Filtro 3 (Gobierno Corporativo): Auditoría Integral de Cargas Individuales y Total Consolidado + Sello y Pago.
"""

import os
import sys
import json
import hashlib
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    'dbname': 'fenix_db',
    'user': 'postgres',
    'password': 'Bupito*268',
    'host': 'localhost',
    'port': 5432
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def redondear(val, dec=2):
    return round(float(val or 0), dec)

class AgenteConciliacionDiesel:
    def __init__(self, conn=None):
        self.conn = conn or get_connection()

    def auditar_semana(self, semana_str):
        """
        Ejecuta la auditoría completa de una semana para todos los frentes de obra.
        semana_str puede ser '37', '38', 'Semana 38', etc.
        """
        sem_num = ''.join(filter(str.isdigit, str(semana_str)))
        cur = self.conn.cursor(cursor_factory=RealDictCursor)

        formatos_semana = (sem_num, f"Semana {sem_num}", f"SEM {sem_num}", f"SEM_{sem_num}")

        # 1. Extraer Facturas
        cur.execute("""
            SELECT id, folio_factura, uuid_cfdi, proveedor, fecha_factura, litros_facturados, precio_unitario, importe_total,
                   UPPER(TRIM(COALESCE(obra_destino, 'SIN_ASIGNAR'))) as obra
            FROM diesel.facturas
            WHERE TRIM(semana) IN %s
            ORDER BY fecha_factura ASC;
        """, (formatos_semana,))
        facturas = cur.fetchall()

        # 2. Extraer Cargas en Campo (Filtro 1)
        cur.execute("""
            SELECT id, folio_conciliacion, fecha, equipo_economico, equipo, litros, costo_por_litro, importe_total,
                   operador, responsable, horometro_inicial,
                   foto_evidencia,
                   COALESCE(medio_suministro, 'MARIMBA') as medio_suministro,
                   COALESCE(conductor_distribuidor, responsable, 'CHOFER CAMPO') as conductor_distribuidor,
                   COALESCE(unidad_reparto, 'CAMION_3.5') as unidad_reparto,
                   UPPER(TRIM(COALESCE(obra_destino, 'SIN_OBRA'))) as obra
            FROM diesel.consumos
            WHERE TRIM(semana) IN %s
            ORDER BY fecha ASC, id ASC;
        """, (formatos_semana,))
        consumos = cur.fetchall()

        # 3. Extraer Solicitudes de los Residentes
        cur.execute("""
            SELECT id, folio_solicitud, fecha, solicitante, litros, importe_total,
                   UPPER(TRIM(COALESCE(obra_destino, 'SIN_OBRA'))) as obra
            FROM diesel.solicitudes
            WHERE TRIM(semana) IN %s
            ORDER BY fecha ASC;
        """, (formatos_semana,))
        solicitudes = cur.fetchall()

        # Agrupar por Obra
        obras_set = set()
        for f in facturas: obras_set.add(f['obra'])
        for c in consumos: obras_set.add(c['obra'])
        for s in solicitudes: obras_set.add(s['obra'])
        
        # Excluir asignaciones a tanques de transporte puro si es necesario, o mantenerlas como centro nodriza
        obras_lista = sorted(list(obras_set))

        resultados_obras = []
        cargas_auditadas_total = len(consumos)
        cargas_con_foto_total = 0
        cargas_con_horometro_total = 0
        banderas_rojas_globales = []

        total_litros_facturados_gral = 0.0
        total_importe_facturado_gral = 0.0
        total_litros_solicitados_gral = 0.0
        total_litros_consumidos_gral = 0.0
        total_importe_consumido_gral = 0.0

        for obra in obras_lista:
            fac_obra = [f for f in facturas if f['obra'] == obra]
            con_obra = [c for c in consumos if c['obra'] == obra]
            sol_obra = [s for s in solicitudes if s['obra'] == obra]

            lts_sol = sum(redondear(s['litros']) for s in sol_obra)
            lts_fac = sum(redondear(f['litros_facturados']) for f in fac_obra)
            imp_fac = sum(redondear(f['importe_total']) for f in fac_obra)
            lts_con = sum(redondear(c['litros']) for c in con_obra)
            imp_con = sum(redondear(c['importe_total']) for c in con_obra)

            total_litros_facturados_gral += lts_fac
            total_importe_facturado_gral += imp_fac
            total_litros_solicitados_gral += lts_sol
            total_litros_consumidos_gral += lts_con
            total_importe_consumido_gral += imp_con

            n_cargas = len(con_obra)
            n_fotos = sum(1 for c in con_obra if c.get('foto_evidencia'))
            n_horometros = sum(1 for c in con_obra if c.get('horometro_inicial') and float(c.get('horometro_inicial') or 0) > 0)

            cargas_con_foto_total += n_fotos
            cargas_con_horometro_total += n_horometros

            delta_sol_fac = redondear(lts_sol - lts_fac)
            delta_fac_con = redondear(lts_fac - lts_con) # Saldo en tanque/obra

            # --- FILTRO 1: Auditoría de Campo Individual de Cargas ---
            banderas_obra = []
            medios_reparto = {}
            for c in con_obra:
                m_rep = c.get('medio_suministro', 'MARIMBA')
                medios_reparto[m_rep] = medios_reparto.get(m_rep, 0) + redondear(c['litros'])
                
                # Regla: Foto cuentalitros faltante
                if not c.get('foto_evidencia'):
                    banderas_obra.append({
                        'nivel': 'ADVERTENCIA',
                        'tipo': 'FALTA_FOTO_CUENTALITROS',
                        'carga_id': c['id'],
                        'equipo': c['equipo_economico'],
                        'litros': float(c['litros'] or 0),
                        'mensaje': f"Carga de {float(c['litros'] or 0):.1f} L a {c['equipo_economico']} sin foto del cuentalitros."
                    })
                # Regla: Carga atípica > 400 L sin justificación en un solo evento
                if float(c['litros'] or 0) > 400.0:
                    banderas_obra.append({
                        'nivel': 'CRITICO',
                        'tipo': 'VOLUMEN_EXCESIVO_EVENTO',
                        'carga_id': c['id'],
                        'equipo': c['equipo_economico'],
                        'litros': float(c['litros'] or 0),
                        'mensaje': f"Carga de {float(c['litros'] or 0):.1f} L excede volumen estándar por máquina en evento único."
                    })


            # --- FILTRO 2: Dictamen para Ingeniero Residente ---
            # Determinación de Semáforo
            pct_fotos = (n_fotos / n_cargas * 100) if n_cargas > 0 else 100.0
            
            if lts_fac == 0 and lts_con > 0:
                semaforo = 'ROJO'
                dictamen = (f"ALERTA CRÍTICA: Se consumieron {lts_con:.2f} L en campo mediante camiones de reparto, "
                            f"pero NO existe ninguna factura de proveedor asignada a esta obra para amparar el gasto.")
            elif delta_fac_con < -20.0:
                semaforo = 'ROJO'
                dictamen = (f"SOBREGIRO DE COMBUSTIBLE: Las máquinas consumieron {lts_con:.2f} L, superando los "
                            f"{lts_fac:.2f} L facturados por {-delta_fac_con:.2f} L. Requiere aclaración inmediata con proveedor.")
            elif abs(delta_fac_con) <= 15.0:
                semaforo = 'VERDE'
                dictamen = (f"CONCILIACIÓN EXACTA: Facturados {lts_fac:.2f} L vs Consumidos {lts_con:.2f} L. "
                            f"Diferencia marginal de {delta_fac_con:+.2f} L. Cumplimiento fotográfico al {pct_fotos:.0f}%. "
                            f"Listo para firma del Ingeniero Residente.")
            else: # delta_fac_con > 15.0 (Saldo remanente en tambos de 3.5 ton o tanque)
                semaforo = 'VERDE' if pct_fotos >= 80 else 'AMARILLO'
                detalle_reparto = ", ".join([f"{k}: {v:.1f} L" for k, v in medios_reparto.items()])
                dictamen = (f"SALDO REMANENTE EN OBRA: De los {lts_fac:.2f} L facturados, se suministraron {lts_con:.2f} L "
                            f"a maquinaria ({detalle_reparto or 'sin cargas registradas'}). Queda un inventario disponible de "
                            f"{delta_fac_con:.2f} L en tambos/tanque para el siguiente turno.")
            
            if abs(delta_sol_fac) > 50.0 and lts_sol > 0:
                dictamen += f" [Nota Fiscal: Solicitados {lts_sol:.2f} L vs Facturados {lts_fac:.2f} L (Delta: {delta_sol_fac:+.2f} L)]."

            banderas_rojas_globales.extend(banderas_obra)

            # Consultar si ya existe registro de firma previa en diesel.conciliaciones_semanales
            cur.execute("""
                SELECT id, aprobado_residente, residente_nombre, fecha_residente, firma_hash_residente, obs_residente,
                       aprobado_gobierno_corp, directivo_nombre, fecha_gobierno_corp, sello_digital_final, obs_gobierno_corp,
                       estatus_global, bloqueado
                FROM diesel.conciliaciones_semanales
                WHERE modulo = 'diesel' AND semana = %s AND obra = %s;
            """, (sem_num, obra))
            reg_existente = cur.fetchone()

            # Guardar o actualizar en base de datos
            cur.execute("""
                INSERT INTO diesel.conciliaciones_semanales (
                    modulo, semana, obra,
                    solicitado_lts, facturado_lts, consumido_lts,
                    delta_sol_fac, delta_fac_con, importe_total,
                    total_cargas, cargas_con_foto, cargas_con_horometro,
                    dictamen_ia, semaforo_ia, banderas_rojas,
                    updated_at
                ) VALUES (
                    'diesel', %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    NOW()
                )
                ON CONFLICT (modulo, semana, obra) DO UPDATE SET
                    solicitado_lts = EXCLUDED.solicitado_lts,
                    facturado_lts = EXCLUDED.facturado_lts,
                    consumido_lts = EXCLUDED.consumido_lts,
                    delta_sol_fac = EXCLUDED.delta_sol_fac,
                    delta_fac_con = EXCLUDED.delta_fac_con,
                    importe_total = EXCLUDED.importe_total,
                    total_cargas = EXCLUDED.total_cargas,
                    cargas_con_foto = EXCLUDED.cargas_con_foto,
                    cargas_con_horometro = EXCLUDED.cargas_con_horometro,
                    dictamen_ia = EXCLUDED.dictamen_ia,
                    semaforo_ia = EXCLUDED.semaforo_ia,
                    banderas_rojas = EXCLUDED.banderas_rojas,
                    updated_at = NOW();
            """, (
                sem_num, obra,
                lts_sol, lts_fac, lts_con,
                delta_sol_fac, delta_fac_con, imp_fac,
                n_cargas, n_fotos, n_horometros,
                dictamen, semaforo, json.dumps(banderas_obra, default=str)
            ))

            resultados_obras.append({
                'obra': obra,
                'solicitado_lts': lts_sol,
                'facturado_lts': lts_fac,
                'consumido_lts': lts_con,
                'delta_sol_fac': delta_sol_fac,
                'delta_fac_con': delta_fac_con, # Saldo remanente
                'importe_total': imp_fac,
                'total_cargas': n_cargas,
                'cargas_con_foto': n_fotos,
                'cargas_con_horometro': n_horometros,
                'cumplimiento_fotos_pct': redondear(pct_fotos, 1),
                'semaforo': semaforo,
                'dictamen_ia': dictamen,
                'banderas_rojas': banderas_obra,
                'distribucion_medios': medios_reparto,
                'firma_residente': {
                    'aprobado': bool(reg_existente['aprobado_residente']) if reg_existente else False,
                    'nombre': reg_existente['residente_nombre'] if reg_existente else None,
                    'fecha': reg_existente['fecha_residente'].isoformat() if reg_existente and reg_existente['fecha_residente'] else None,
                    'hash': reg_existente['firma_hash_residente'] if reg_existente else None,
                    'observaciones': reg_existente['obs_residente'] if reg_existente else None
                },
                'firma_gobierno': {
                    'aprobado': bool(reg_existente['aprobado_gobierno_corp']) if reg_existente else False,
                    'nombre': reg_existente['directivo_nombre'] if reg_existente else None,
                    'fecha': reg_existente['fecha_gobierno_corp'].isoformat() if reg_existente and reg_existente['fecha_gobierno_corp'] else None,
                    'sello': reg_existente['sello_digital_final'] if reg_existente else None,
                    'observaciones': reg_existente['obs_gobierno_corp'] if reg_existente else None
                },
                'estatus_global': reg_existente['estatus_global'] if reg_existente else 'PENDIENTE_RESIDENTE',
                'bloqueado': bool(reg_existente['bloqueado']) if reg_existente else False
            })

        self.conn.commit()

        # --- FILTRO 3: Dictamen Global Consolidado para Gobierno Corporativo ---
        total_delta_remanente = redondear(total_litros_facturados_gral - total_litros_consumidos_gral)
        obras_firmadas_residente = sum(1 for o in resultados_obras if o['firma_residente']['aprobado'])
        obras_firmadas_gobierno = sum(1 for o in resultados_obras if o['firma_gobierno']['aprobado'])

        if len(banderas_rojas_globales) == 0 and total_delta_remanente >= 0:
            semaforo_corporativo = 'VERDE'
            dictamen_corporativo = (f"DICTAMEN FAVORABLE: Semana {sem_num} auditada con éxito. Facturado total: "
                                    f"{total_litros_facturados_gral:,.2f} L (${total_importe_facturado_gral:,.2f} MXN) vs "
                                    f"Consumido en frentes: {total_litros_consumidos_gral:,.2f} L. "
                                    f"Saldo remanente en inventario: {total_delta_remanente:,.2f} L. "
                                    f"Apta para dispersión de pago tras firmas de residentes.")
        elif any(o['semaforo'] == 'ROJO' for o in resultados_obras):
            semaforo_corporativo = 'ROJO'
            dictamen_corporativo = (f"DICTAMEN CON OBSERVACIONES CRÍTICAS: Existen obras con consumos no amparados o "
                                    f"sobregiros. Se requiere resolución de banderas rojas antes de autorizar el pago a proveedores.")
        else:
            semaforo_corporativo = 'AMARILLO'
            dictamen_corporativo = (f"DICTAMEN CONDICIONADO: Se identificaron {len(banderas_rojas_globales)} alertas de campo "
                                    f"(fotos/horómetros faltantes). Revisar observaciones de residentes antes de cierre final.")

        resumen_global = {
            'semana': sem_num,
            'fecha_auditoria': datetime.now().isoformat(),
            'total_obras': len(resultados_obras),
            'obras_firmadas_residente': f"{obras_firmadas_residente}/{len(resultados_obras)}",
            'obras_firmadas_gobierno': f"{obras_firmadas_gobierno}/{len(resultados_obras)}",
            'semaforo_corporativo': semaforo_corporativo,
            'dictamen_corporativo': dictamen_corporativo,
            'balance_global': {
                'litros_solicitados': redondear(total_litros_solicitados_gral),
                'litros_facturados': redondear(total_litros_facturados_gral),
                'importe_facturado_mxn': redondear(total_importe_facturado_gral),
                'litros_consumidos': redondear(total_litros_consumidos_gral),
                'importe_consumido_mxn': redondear(total_importe_consumido_gral),
                'saldo_remanente_lts': total_delta_remanente
            },
            'auditoria_campo': {
                'total_cargas': cargas_auditadas_total,
                'cargas_con_foto': cargas_con_foto_total,
                'cumplimiento_fotos_pct': redondear((cargas_con_foto_total / cargas_auditadas_total * 100) if cargas_auditadas_total else 100, 1),
                'total_alertas': len(banderas_rojas_globales)
            },
            'obras': resultados_obras
        }

        cur.close()
        return resumen_global

    def registrar_firma_residente(self, semana, obra, residente_nombre, residente_usuario, firma_img_base64, observaciones="", ip_origen="127.0.0.1"):
        """
        Nivel 2: Registra la firma y visto bueno del Ingeniero Residente de Obra
        """
        sem_num = ''.join(filter(str.isdigit, str(semana)))
        cur = self.conn.cursor(cursor_factory=RealDictCursor)

        # Verificar si la semana está bloqueada
        cur.execute("SELECT bloqueado, facturado_lts, consumido_lts FROM diesel.conciliaciones_semanales WHERE modulo='diesel' AND semana=%s AND obra=%s", (sem_num, obra))
        r = cur.fetchone()
        if r and r['bloqueado']:
            cur.close()
            return {'exito': False, 'mensaje': 'Esta semana ya ha sido sellada y bloqueada por Gobierno Corporativo.'}

        # Generar Hash Criptográfico de la Firma
        timestamp_str = datetime.now().isoformat()
        datos_sello = f"NIVEL2_RESIDENTE|SEM:{sem_num}|OBRA:{obra}|USER:{residente_usuario}|TS:{timestamp_str}|IP:{ip_origen}|LTS_CON:{r['consumido_lts'] if r else 0}"
        firma_hash = hashlib.sha256(datos_sello.encode('utf-8')).hexdigest()

        cur.execute("""
            UPDATE diesel.conciliaciones_semanales
            SET aprobado_residente = TRUE,
                residente_nombre = %s,
                residente_usuario = %s,
                fecha_residente = NOW(),
                firma_img_residente = %s,
                firma_hash_residente = %s,
                obs_residente = %s,
                estatus_global = CASE WHEN estatus_global = 'SELLADO_Y_PAGADO' THEN 'SELLADO_Y_PAGADO' ELSE 'PENDIENTE_GOBIERNO' END,
                updated_at = NOW()
            WHERE modulo = 'diesel' AND semana = %s AND obra = %s
            RETURNING id;
        """, (residente_nombre, residente_usuario, firma_img_base64, firma_hash, observaciones, sem_num, obra))
        
        self.conn.commit()
        cur.close()
        return {
            'exito': True,
            'mensaje': f'Firma del Ingeniero Residente registrada exitosamente para {obra}.',
            'hash_sello': firma_hash,
            'timestamp': timestamp_str
        }

    def registrar_firma_gobierno_corp(self, semana, directivo_nombre, directivo_usuario, firma_img_base64, observaciones="", ip_origen="127.0.0.1"):
        """
        Nivel 3: Registra la firma final de Gobierno Corporativo, sella la semana y bloquea modificaciones.
        """
        sem_num = ''.join(filter(str.isdigit, str(semana)))
        cur = self.conn.cursor(cursor_factory=RealDictCursor)

        timestamp_str = datetime.now().isoformat()
        datos_sello = f"NIVEL3_GOBIERNO_CORP|SEM:{sem_num}|DIRECTIVO:{directivo_usuario}|TS:{timestamp_str}|IP:{ip_origen}"
        sello_final = hashlib.sha256(datos_sello.encode('utf-8')).hexdigest()

        cur.execute("""
            UPDATE diesel.conciliaciones_semanales
            SET aprobado_gobierno_corp = TRUE,
                directivo_nombre = %s,
                directivo_usuario = %s,
                fecha_gobierno_corp = NOW(),
                firma_img_gobierno_corp = %s,
                sello_digital_final = %s,
                obs_gobierno_corp = %s,
                estatus_global = 'SELLADO_Y_PAGADO',
                bloqueado = TRUE,
                updated_at = NOW()
            WHERE modulo = 'diesel' AND semana = %s
            RETURNING obra;
        """, (directivo_nombre, directivo_usuario, firma_img_base64, sello_final, observaciones, sem_num))
        
        obras_actualizadas = [r['obra'] for r in cur.fetchall()]
        self.conn.commit()
        cur.close()

        return {
            'exito': True,
            'mensaje': f'Semana {sem_num} APROBADA Y SELLADA por Gobierno Corporativo para {len(obras_actualizadas)} obras.',
            'sello_digital': sello_final,
            'timestamp': timestamp_str,
            'obras_selladas': obras_actualizadas
        }


if __name__ == '__main__':
    sem = sys.argv[1] if len(sys.argv) > 1 else '38'
    print(f"\n>>> Ejecutando Agente IA de Conciliación para Semana {sem}...")
    agente = AgenteConciliacionDiesel()
    resultado = agente.auditar_semana(sem)
    print(f"\n[SEMAFORO CORPORATIVO]: {resultado['semaforo_corporativo']}")
    print(f"[DICTAMEN]: {resultado['dictamen_corporativo']}")
    print(f"\nBalance Global:")
    print(f" - Facturado:  {resultado['balance_global']['litros_facturados']:,.2f} L (${resultado['balance_global']['importe_facturado_mxn']:,.2f} MXN)")
    print(f" - Consumido:  {resultado['balance_global']['litros_consumidos']:,.2f} L")
    print(f" - Saldo Obra: {resultado['balance_global']['saldo_remanente_lts']:,.2f} L")
    print(f"\nDetalle por Frente de Obra ({resultado['total_obras']}):")
    for o in resultado['obras']:
        print(f" * [{o['semaforo']:7}] {o['obra']:26} | Fac: {o['facturado_lts']:>7.2f} L | Con: {o['consumido_lts']:>7.2f} L | Saldo: {o['delta_fac_con']:>7.2f} L | Cargas: {o['total_cargas']}")
        print(f"   Dictamen: {o['dictamen_ia']}")
