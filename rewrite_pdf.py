with open(r'c:\Users\JOSE\Desktop\Proyecto fenix\app_admin.py', 'r', encoding='utf-8') as f:
    content = f.read()

start_marker = "        # ── CONSULTA DE DATOS ─────────────────────────────────────────────────"
end_marker = "    except Exception as e:\n        import traceback\n        return jsonify({'success': False, 'error': str(e), 'trace': traceback.format_exc()})"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker, start_idx)

new_section = r"""        # ── CONSULTA DE DATOS ─────────────────────────────────────────────────
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
        q_resp = f"""
            SELECT
                COALESCE(NULLIF(NULLIF(responsable, 'nan'), ''), 'S/R') as resp,
                STRING_AGG(DISTINCT obra_destino, ', ') as obras,
                SUM(litros) as consumido
            FROM {modulo}.consumos
            {cond_con}
            GROUP BY COALESCE(NULLIF(NULLIF(responsable, 'nan'), ''), 'S/R')
            ORDER BY resp
        """
        try:
            rows_resp = db.execute(q_resp, tuple(params_con)).fetchall()
        except:
            rows_resp = []

        # === 2. DATOS PARA MAQUINARIA ===
        q_maq = f"""
            SELECT
                obra_destino as obra,
                COALESCE(NULLIF(NULLIF(equipo, 'nan'), ''), 'S/E') as maquinaria,
                SUM(litros) as consumido
            FROM {modulo}.consumos
            {cond_con}
            GROUP BY obra_destino, COALESCE(NULLIF(NULLIF(equipo, 'nan'), ''), 'S/E')
            ORDER BY obra_destino, maquinaria
        """
        try:
            rows_maq = db.execute(q_maq, tuple(params_con)).fetchall()
        except:
            rows_maq = []

        # === 3. DATOS DIARIOS PARA DESGLOSE OPERATIVO ===
        q_diario = f"""
            SELECT
                fecha,
                obra_destino,
                COALESCE(NULLIF(NULLIF(equipo, 'nan'), ''), 'S/E') as maquinaria,
                COALESCE(NULLIF(NULLIF(responsable, 'nan'), ''), 'S/R') as resp,
                SUM(litros) as consumido
            FROM {modulo}.consumos
            {cond_con}
            GROUP BY fecha, obra_destino,
                COALESCE(NULLIF(NULLIF(equipo, 'nan'), ''), 'S/E'),
                COALESCE(NULLIF(NULLIF(responsable, 'nan'), ''), 'S/R')
            ORDER BY obra_destino, fecha, equipo
        """
        try:
            rows_diario = db.execute(q_diario, tuple(params_con)).fetchall()
        except:
            rows_diario = []

        db.close()

        from collections import defaultdict
        import datetime as dt_module

        DIAS_ES = {0: 'LUNES', 1: 'MARTES', 2: 'MIERCOLES', 3: 'JUEVES', 4: 'VIERNES', 5: 'SABADO', 6: 'DOMINGO'}

        # Autorizado DIARIO FIJO = Total Autorizado del Responsable / 5 dias habiles
        # Es una tarifa fija: si trabaja sabado, el dia vale lo mismo (no se redistribuye)
        def get_autorizado_diario(resp):
            auto_sem = auth_map.get(resp, 0)
            if auto_sem <= 0:
                return 0
            return auto_sem / 5.0  # FIJO: siempre dividido entre 5

        # Estructurar: {obra: {fecha: [(maquinaria, litros, resp)]}}
        desglose_obra = defaultdict(lambda: defaultdict(list))
        for r in rows_diario:
            obra = str(r['obra_destino'] or 'Sin Obra')
            desglose_obra[obra][r['fecha']].append(
                (str(r['maquinaria']), float(r['consumido'] or 0), str(r['resp']))
            )

        # ── SECCION 1: DESGLOSE POR RESPONSABLE ──────────────────────────────
        story.append(Paragraph('Seccion 1 - Desglose por Responsable', st_seccion))
        story.append(Paragraph(
            'Consolidado de litros Autorizados vs Consumidos por Ingeniero Responsable, incluyendo todas las obras en las que laboro durante la semana.',
            st_explicacion))

        col_w_resp = [4*cm, 7*cm, 3.5*cm, 3.5*cm, 3.5*cm]
        hdr_resp = [
            Paragraph('<font color="white"><b>Responsable</b></font>', st_celda),
            Paragraph('<font color="white"><b>Obras / Centros de Trabajo</b></font>', st_celda),
            Paragraph('<para align=center><font color="white"><b>Autorizado (L)</b></font></para>', st_celda),
            Paragraph('<para align=center><font color="white"><b>Consumido (L)</b></font></para>', st_celda),
            Paragraph('<para align=center><font color="white"><b>Diferencia (L)</b></font></para>', st_celda),
        ]
        tabla_resp_data = [hdr_resp]
        tot_auto = 0
        tot_con = 0

        for r in rows_resp:
            resp = r['resp']
            obras = str(r['obras'] or '-')
            auto = auth_map.get(resp, 0)
            con = float(r['consumido'] or 0)
            diff = auto - con
            tot_auto += auto
            tot_con += con

            if abs(diff) < 0.1:
                diff_str = f'<font color="{COLOR_VERDE}">0.00</font>'
            elif diff > 0:
                diff_str = f'<font color="{COLOR_VERDE}">+{diff:,.2f}</font>'
            else:
                diff_str = f'<font color="{COLOR_ROJO}">{diff:,.2f}</font>'

            tabla_resp_data.append([
                Paragraph(resp, st_celda),
                Paragraph(obras, st_celda),
                Paragraph(f'<para align=right>{auto:,.2f} L</para>' if auto > 0 else '<para align=right>-</para>', st_celda),
                Paragraph(f'<para align=right>{con:,.2f} L</para>' if con > 0 else '<para align=right>-</para>', st_celda),
                Paragraph(f'<para align=right><b>{diff_str}</b></para>', st_celda),
            ])

        diff_tot = tot_auto - tot_con
        if abs(diff_tot) < 0.1:
            dt_str = f'<font color="{COLOR_VERDE}">0.00</font>'
        elif diff_tot > 0:
            dt_str = f'<font color="{COLOR_VERDE}">+{diff_tot:,.2f}</font>'
        else:
            dt_str = f'<font color="{COLOR_ROJO}">{diff_tot:,.2f}</font>'

        tabla_resp_data.append([
            Paragraph('<font color="white"><b>TOTAL RESPONSABLES</b></font>', st_celda),
            Paragraph('', st_celda),
            Paragraph(f'<para align=right><font color="white"><b>{tot_auto:,.2f} L</b></font></para>', st_celda),
            Paragraph(f'<para align=right><font color="white"><b>{tot_con:,.2f} L</b></font></para>', st_celda),
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

        # ── SECCION 2: DESGLOSE POR OBRA Y MAQUINARIA ────────────────────────
        story.append(Spacer(1, 0.4*cm))
        story.append(Paragraph('Seccion 2 - Desglose por Obra y Maquinaria', st_seccion))
        story.append(Paragraph(
            'Consumo total de la semana agrupado por Obra y Equipo/Maquinaria.',
            st_explicacion))

        col_w_maq = [7*cm, 8*cm, 4*cm]
        hdr_maq = [
            Paragraph('<font color="white"><b>Obra / Centro de Trabajo</b></font>', st_celda),
            Paragraph('<font color="white"><b>Maquinaria / Equipo</b></font>', st_celda),
            Paragraph('<para align=center><font color="white"><b>Consumido (L)</b></font></para>', st_celda),
        ]
        tabla_maq_data = [hdr_maq]
        tot_maq_con = 0

        for r in rows_maq:
            obra = str(r['obra'] or '-')
            maq = str(r['maquinaria'] or 'S/E')
            con = float(r['consumido'] or 0)
            tot_maq_con += con
            tabla_maq_data.append([
                Paragraph(obra, st_celda),
                Paragraph(maq, st_celda),
                Paragraph(f'<para align=right>{con:,.2f} L</para>' if con > 0 else '<para align=right>-</para>', st_celda),
            ])

        tabla_maq_data.append([
            Paragraph('<font color="white"><b>TOTAL MAQUINARIA</b></font>', st_celda),
            Paragraph('', st_celda),
            Paragraph(f'<para align=right><font color="white"><b>{tot_maq_con:,.2f} L</b></font></para>', st_celda),
        ])

        t_maq = Table(tabla_maq_data, colWidths=col_w_maq, repeatRows=1)
        t_maq.setStyle(TableStyle([
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
        story.append(t_maq)

        # ── SECCION 3: DESGLOSE OPERATIVO POR OBRA / DIA / MAQUINARIA ────────
        from reportlab.platypus import PageBreak
        story.append(PageBreak())
        story.append(Paragraph('Seccion 3 - Desglose Operativo por Obra, Dia y Maquinaria', st_seccion))
        story.append(Paragraph(
            'Consumo diario por Obra. Para cada dia se muestra la maquinaria utilizada y los litros consumidos. '
            'El "Autorizado/Dia" es una tarifa FIJA: Total Autorizado del Responsable / 5 dias habiles. '
            'Si trabaja sabado o domingo, el autorizado de ese dia es el mismo.',
            st_explicacion))

        st_obra_hdr = ParagraphStyle('obra_hdr', fontName='Helvetica-Bold', fontSize=9,
                                      textColor=colors.white, alignment=TA_LEFT)
        COLOR_SUBTOTAL = colors.HexColor('#E0E7FF')
        col_w_sec3 = [3.5*cm, 5.5*cm, 3.5*cm, 3.5*cm]

        for obra_nombre in sorted(desglose_obra.keys()):
            fechas_dict = desglose_obra[obra_nombre]
            story.append(Spacer(1, 0.3*cm))

            # Barra de encabezado de Obra (azul marino)
            t_obra_hdr = Table([[Paragraph(f'  {obra_nombre}', st_obra_hdr), '', '', '']], colWidths=col_w_sec3)
            t_obra_hdr.setStyle(TableStyle([
                ('BACKGROUND',   (0,0), (-1,0), COLOR_OSCURO),
                ('SPAN',         (0,0), (-1,0)),
                ('TOPPADDING',   (0,0), (-1,0), 6),
                ('BOTTOMPADDING',(0,0), (-1,0), 6),
                ('LEFTPADDING',  (0,0), (-1,0), 10),
            ]))
            story.append(t_obra_hdr)

            sec3_data = [[
                Paragraph('<font color="white"><b>Dia</b></font>', st_celda),
                Paragraph('<font color="white"><b>Maquinaria / Equipo</b></font>', st_celda),
                Paragraph('<para align=right><font color="white"><b>Consumido (L)</b></font></para>', st_celda),
                Paragraph('<para align=right><font color="white"><b>Autoriz./Dia (L)</b></font></para>', st_celda),
            ]]
            sec3_styles = [
                ('BACKGROUND',   (0,0), (-1,0), COLOR_PRIMARIO),
                ('TEXTCOLOR',    (0,0), (-1,0), colors.white),
                ('FONTNAME',     (0,0), (-1,0), 'Helvetica-Bold'),
                ('GRID',         (0,0), (-1,-1), 0.3, COLOR_GRIS_MED),
                ('VALIGN',       (0,0), (-1,-1), 'MIDDLE'),
                ('TOPPADDING',   (0,0), (-1,-1), 4),
                ('BOTTOMPADDING',(0,0), (-1,-1), 4),
                ('LEFTPADDING',  (0,0), (-1,-1), 5),
            ]

            row_idx = 1
            for fecha in sorted(fechas_dict.keys()):
                maquinas = fechas_dict[fecha]
                try:
                    fecha_dt = fecha if hasattr(fecha, 'weekday') else dt_module.datetime.strptime(str(fecha), '%Y-%m-%d').date()
                    dia_nombre = DIAS_ES.get(fecha_dt.weekday(), str(fecha))
                    dia_label = f'{dia_nombre} {fecha_dt.strftime("%d/%m")}'
                except:
                    dia_label = str(fecha)

                total_dia = sum(lts for _, lts, _ in maquinas)
                resps_dia = [r3 for _, _, r3 in maquinas if r3 != 'S/R']
                resp_principal = resps_dia[0] if resps_dia else 'S/R'
                auto_dia = get_autorizado_diario(resp_principal)  # FIJO: total/5

                is_first = True
                for maq, lts, resp3 in sorted(maquinas, key=lambda x: x[0]):
                    dia_cell = Paragraph(dia_label, st_celda) if is_first else Paragraph('', st_celda)
                    auto_cell = Paragraph(
                        f'<para align=right>{auto_dia:,.2f}</para>' if (is_first and auto_dia > 0) else '<para align=right></para>',
                        st_celda)
                    sec3_data.append([dia_cell, Paragraph(maq, st_celda),
                                       Paragraph(f'<para align=right>{lts:,.2f}</para>', st_celda), auto_cell])
                    is_first = False
                    row_idx += 1

                # Subtotal del dia
                sec3_data.append([
                    Paragraph('', st_celda),
                    Paragraph('<b>Total del Dia</b>', st_celda),
                    Paragraph(f'<para align=right><b>{total_dia:,.2f} L</b></para>', st_celda),
                    Paragraph('', st_celda),
                ])
                sec3_styles.append(('BACKGROUND', (0, row_idx), (-1, row_idx), COLOR_SUBTOTAL))
                sec3_styles.append(('FONTNAME',   (0, row_idx), (-1, row_idx), 'Helvetica-Bold'))
                row_idx += 1

            t_sec3 = Table(sec3_data, colWidths=col_w_sec3, repeatRows=1)
            t_sec3.setStyle(TableStyle(sec3_styles))
            story.append(t_sec3)

        # ── FOOTER ────────────────────────────────────────────────────────────
        story.append(Spacer(1, 0.4*cm))
        story.append(HRFlowable(width='100%', thickness=0.5, color=COLOR_GRIS_MED))
        story.append(Spacer(1, 0.2*cm))
        story.append(Paragraph(
            f'Reporte generado automaticamente por Sistema Fenix 2.0 - Grupo Trujano. '
            f'Fecha: {hoy.strftime("%d/%m/%Y %H:%M")}. Documento de uso interno y confidencial.',
            st_footer))

        # ── GENERAR PDF ───────────────────────────────────────────────────────
        doc.build(story)
        buf.seek(0)

        from flask import send_file as flask_send_file
        return flask_send_file(buf, mimetype='application/pdf',
                               as_attachment=True,
                               download_name=f'Reporte_Combustible_{modulo_label}_{semana_label.replace(" ", "_")}_{hoy.strftime("%Y%m%d_%H%M")}.pdf')

"""

new_content = content[:start_idx] + new_section + content[end_idx:]

with open(r'c:\Users\JOSE\Desktop\Proyecto fenix\app_admin.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Done. File written.")
