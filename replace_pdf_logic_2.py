import sys
import re

with open(r'c:\Users\JOSE\Desktop\Proyecto fenix\app_admin.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_pdf_logic = """# ── CONSULTA DE DATOS ─────────────────────────────────────────────────
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

        # === 1. DATOS PARA RESPONSABLES ===
        q_resp = f'''
            SELECT 
                COALESCE(NULLIF(NULLIF(responsable, 'nan'), ''), 'S/R') as resp,
                STRING_AGG(DISTINCT obra_destino, ', ') as obras,
                SUM(litros) as consumido
            FROM {modulo}.consumos
            {cond_con}
            GROUP BY COALESCE(NULLIF(NULLIF(responsable, 'nan'), ''), 'S/R')
            ORDER BY resp
        '''
        try:
            rows_resp = db.execute(q_resp, tuple(params_con)).fetchall()
        except:
            rows_resp = []

        # === 2. DATOS PARA MAQUINARIA ===
        q_maq = f'''
            SELECT 
                obra_destino as obra,
                COALESCE(NULLIF(NULLIF(equipo, 'nan'), ''), 'S/E') as maquinaria,
                SUM(litros) as consumido
            FROM {modulo}.consumos
            {cond_con}
            GROUP BY obra_destino, COALESCE(NULLIF(NULLIF(equipo, 'nan'), ''), 'S/E')
            ORDER BY obra_destino, maquinaria
        '''
        try:
            rows_maq = db.execute(q_maq, tuple(params_con)).fetchall()
        except:
            rows_maq = []

        db.close()

        # ── SECCIÓN 1: DESGLOSE POR RESPONSABLE ───────────────────────────────
        story.append(Paragraph('📊 Sección 1 — Desglose por Responsable', st_seccion))
        story.append(Paragraph(
            'Esta sección presenta el consolidado de litros de combustible Autorizados vs Consumidos agrupados por Responsable, sumando todas las obras en las que laboró durante la semana.',
            st_explicacion))

        col_w_resp = [4*cm, 7*cm, 3.5*cm, 3.5*cm, 3.5*cm]
        hdr_resp = [
            Paragraph('<b>Responsable</b>', st_celda),
            Paragraph('<b>Obras / Centros de Trabajo</b>', st_celda),
            Paragraph('<para align=center><b>Autorizado (L)</b></para>', st_celda),
            Paragraph('<para align=center><b>Consumido (L)</b></para>', st_celda),
            Paragraph('<para align=center><b>Diferencia (L)</b></para>', st_celda),
        ]
        tabla_resp_data = [hdr_resp]
        tot_auto = 0
        tot_con = 0
        
        for r in rows_resp:
            resp = r['resp']
            obras = str(r['obras'] or '—')
            
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
                Paragraph(resp, st_celda),
                Paragraph(obras, st_celda),
                Paragraph(f'<para align=right>{auto:,.2f} L</para>' if auto > 0 else '<para align=right>—</para>', st_celda),
                Paragraph(f'<para align=right>{con:,.2f} L</para>' if con > 0 else '<para align=right>—</para>', st_celda),
                Paragraph(f'<para align=right><b>{diff_str}</b></para>', st_celda),
            ])

        # Totals row for Responsables
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
        
        # ── SECCIÓN 2: DESGLOSE POR MAQUINARIA ───────────────────────────────
        story.append(Spacer(1, 0.4*cm))
        story.append(Paragraph('🚜 Sección 2 — Desglose por Maquinaria', st_seccion))
        story.append(Paragraph(
            'Esta tabla desglosa el combustible consumido agrupado por Obra y Equipo (Maquinaria o Vehículo).',
            st_explicacion))

        col_w_maq = [7*cm, 7*cm, 3.5*cm, 4*cm]
        hdr_maq = [
            Paragraph('<b>Obra / Centro de Trabajo</b>', st_celda),
            Paragraph('<b>Maquinaria / Equipo</b>', st_celda),
            Paragraph('<para align=center><b>Autorizado (L)</b></para>', st_celda),
            Paragraph('<para align=center><b>Consumido (L)</b></para>', st_celda),
        ]
        tabla_maq_data = [hdr_maq]
        tot_maq_con = 0
        
        for r in rows_maq:
            obra = str(r['obra'] or '—')
            maq = str(r['maquinaria'] or 'S/E')
            con = float(r['consumido'] or 0)
            
            tot_maq_con += con
                
            tabla_maq_data.append([
                Paragraph(obra, st_celda),
                Paragraph(maq, st_celda),
                Paragraph(f'<para align=right>—</para>', st_celda),
                Paragraph(f'<para align=right>{con:,.2f} L</para>' if con > 0 else '<para align=right>—</para>', st_celda),
            ])

        # Totals row for Maquinaria
        tabla_maq_data.append([
            Paragraph('<b>TOTAL MAQUINARIA</b>', st_celda),
            Paragraph('', st_celda),
            Paragraph('<para align=right><b>—</b></para>', st_celda),
            Paragraph(f'<para align=right><b>{tot_maq_con:,.2f} L</b></para>', st_celda),
        ])

        t_maq = Table(tabla_maq_data, colWidths=col_w_maq, repeatRows=1)
        t_maq.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), COLOR_OSCURO),
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
        story.append(t_maq)

"""

start_marker = "# ── CONSULTA DE DATOS ─────────────────────────────────────────────────"
end_marker = "# ── FOOTER ────────────────────────────────────────────────────────────"

parts = content.split(start_marker)
before = parts[0]
after = end_marker + parts[1].split(end_marker, 1)[1]

content = before + new_pdf_logic + after

with open(r'c:\Users\JOSE\Desktop\Proyecto fenix\app_admin.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Replaced PDF logic.")
