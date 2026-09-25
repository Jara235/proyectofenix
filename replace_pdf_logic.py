import re

with open(r'c:\Users\JOSE\Desktop\Proyecto fenix\app_admin.py', 'r', encoding='utf-8') as f:
    content = f.read()

start_marker = "# ── CONSULTA DE DATOS ─────────────────────────────────────────────────"
end_marker = "# ── FOOTER ────────────────────────────────────────────────────────────"

new_logic = """# ── CONSULTA DE DATOS ─────────────────────────────────────────────────
        cond_con = "WHERE obra_destino NOT ILIKE %s AND estatus_revision = 'APROBADO'"
        params_con = ['%Tanque Pegaso%']
        semana_num = None
        if semana_param != 'TODOS':
            semana_limpia = str(semana_param).replace('Semana ', '').strip()
            cond_con += " AND semana = %s"
            params_con.append(semana_limpia)
            try:
                semana_num = int(semana_limpia)
            except:
                pass

        auth_map = {}
        if modulo == 'diesel' and semana_num:
            try:
                auth_rows = db.execute(
                    "SELECT referencia, litros_autorizados FROM catalogos.autorizaciones WHERE tipo='DIESEL' AND semana=%s",
                    (semana_num,)
                ).fetchall()
                for ar in auth_rows:
                    auth_map[ar['referencia']] = float(ar['litros_autorizados'] or 0)
            except:
                pass

        if semana_param == 'TODOS':
            q_obras = f'''
                WITH sol AS (
                    SELECT DISTINCT obra_destino FROM {modulo}.solicitudes {cond_con.replace('estatus_revision', 'estatus_conciliacion')}
                ),
                con AS (
                    SELECT DISTINCT obra_destino FROM {modulo}.consumos {cond_con}
                ),
                fac AS (
                    SELECT DISTINCT obra_destino FROM {modulo}.facturas {cond_con}
                ),
                todas AS (
                    SELECT obra_destino FROM sol UNION
                    SELECT obra_destino FROM con UNION
                    SELECT obra_destino FROM fac
                )
                SELECT t.obra_destino as obra,
                       (SELECT STRING_AGG(DISTINCT NULLIF(NULLIF(responsable, 'nan'), ''), ', ') 
                        FROM {modulo}.consumos c 
                        WHERE c.obra_destino = t.obra_destino) as responsable,
                       (SELECT SUM(litros) 
                        FROM {modulo}.consumos c 
                        WHERE c.obra_destino = t.obra_destino AND c.estatus_revision = 'APROBADO') as consumido
                FROM todas t
                WHERE t.obra_destino IS NOT NULL
                ORDER BY t.obra_destino
            '''
            params_obras = params_con * 3
        else:
            q_obras = f'''
                WITH sol AS (
                    SELECT DISTINCT obra_destino FROM {modulo}.solicitudes {cond_con.replace('estatus_revision', 'estatus_conciliacion')}
                ),
                con AS (
                    SELECT DISTINCT obra_destino FROM {modulo}.consumos {cond_con}
                ),
                fac AS (
                    SELECT DISTINCT obra_destino FROM {modulo}.facturas {cond_con}
                ),
                todas AS (
                    SELECT obra_destino FROM sol UNION
                    SELECT obra_destino FROM con UNION
                    SELECT obra_destino FROM fac
                )
                SELECT t.obra_destino as obra,
                       (SELECT STRING_AGG(DISTINCT NULLIF(NULLIF(responsable, 'nan'), ''), ', ') 
                        FROM {modulo}.consumos c 
                        WHERE c.obra_destino = t.obra_destino AND c.semana = %s) as responsable,
                       (SELECT SUM(litros) 
                        FROM {modulo}.consumos c 
                        WHERE c.obra_destino = t.obra_destino AND c.semana = %s AND c.estatus_revision = 'APROBADO') as consumido
                FROM todas t
                WHERE t.obra_destino IS NOT NULL
                ORDER BY t.obra_destino
            '''
            params_obras = params_con * 3 + [semana_limpia, semana_limpia]

        try:
            rows_obras = db.execute(q_obras, tuple(params_obras)).fetchall()
        except:
            rows_obras = []

        db.close()

        # ── SECCIÓN 1: DESGLOSE POR RESPONSABLE ───────────────────────────────
        story.append(Paragraph('📊 Desglose por Responsable', st_seccion))
        story.append(Paragraph(
            'Esta sección presenta el consolidado de litros de combustible Autorizados vs Consumidos por Obra y Responsable.',
            st_explicacion))

        col_w_resp = [6*cm, 4*cm, 4*cm, 4*cm, 4*cm]
        hdr_resp = [
            Paragraph('<b>Obra / Centro de Trabajo</b>', st_celda),
            Paragraph('<b>Responsable</b>', st_celda),
            Paragraph('<para align=center><b>Autorizado (L)</b></para>', st_celda),
            Paragraph('<para align=center><b>Consumido (L)</b></para>', st_celda),
            Paragraph('<para align=center><b>Diferencia (L)</b></para>', st_celda),
        ]
        tabla_resp_data = [hdr_resp]
        tot_auto = 0
        tot_con = 0
        
        for r in rows_obras:
            resp = r['responsable'] or 'S/R'
            auto = 0
            if resp != 'S/R':
                for rep_indiv in resp.split(','):
                    auto += auth_map.get(rep_indiv.strip(), 0)
            
            con = float(r['consumido'] or 0)
            diff = auto - con
            
            tot_auto += auto
            tot_con += con
            
            if abs(diff) < 0.1:
                diff_str = f'<font color="{COLOR_VERDE}">0.00</font>'
            elif diff > 0:
                diff_str = f'<font color="{COLOR_VERDE}">+{diff:+,.2f}</font>'
            else:
                diff_str = f'<font color="{COLOR_ROJO}">{diff:+,.2f}</font>'
                
            tabla_resp_data.append([
                Paragraph(str(r['obra'] or '—'), st_celda),
                Paragraph(resp, st_celda),
                Paragraph(f'<para align=right>{auto:,.2f} L</para>' if auto > 0 else '<para align=right>—</para>', st_celda),
                Paragraph(f'<para align=right>{con:,.2f} L</para>' if con > 0 else '<para align=right>—</para>', st_celda),
                Paragraph(f'<para align=right><b>{diff_str}</b></para>', st_celda),
            ])

        # Totals row
        diff_tot = tot_auto - tot_con
        if abs(diff_tot) < 0.1:
            dt_str = f'<font color="{COLOR_VERDE}">0.00</font>'
        elif diff_tot > 0:
            dt_str = f'<font color="{COLOR_VERDE}">+{diff_tot:+,.2f}</font>'
        else:
            dt_str = f'<font color="{COLOR_ROJO}">{diff_tot:+,.2f}</font>'
            
        tabla_resp_data.append([
            Paragraph('<b>TOTAL RESPONSABLES</b>', st_celda),
            Paragraph('', st_celda),
            Paragraph(f'<para align=right><b>{tot_auto:,.2f} L</b></para>', st_celda),
            Paragraph(f'<para align=right><b>{tot_con:,.2f} L</b></para>', st_celda),
            Paragraph(f'<para align=right><b>{dt_str}</b></para>', st_celda),
        ])

        t_resp = Table(tabla_resp_data, colWidths=col_w_resp, repeatRows=1)
        t_resp.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), COLOR_PRIMARIO),
            ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
            ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
            ('ROWBACKGROUNDS', (0,1), (-1,-2), [COLOR_GRIS_CLARO, colors.white]),
            ('BACKGROUND', (0,-1), (-1,-1), COLOR_GRIS_MED),
            ('FONTNAME',   (0,-1), (-1,-1), 'Helvetica-Bold'),
            ('GRID',       (0,0), (-1,-1), 0.3, COLOR_GRIS_MED),
            ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING',   (0,0), (-1,-1), 6),
        ]))
        story.append(t_resp)

        """

parts = content.split(start_marker)
before = parts[0]
after = start_marker + parts[1].split(end_marker, 1)[1]

new_content = before + new_logic + end_marker + after.split(start_marker)[1]

with open(r'c:\Users\JOSE\Desktop\Proyecto fenix\app_admin.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Replacement done.")
