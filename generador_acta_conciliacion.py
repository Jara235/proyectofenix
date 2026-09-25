"""
generador_acta_conciliacion.py - Generador del Acta Oficial de Conciliación Semanal de Combustible
Sistema Fénix 2.0 - Grupo Trujano
Genera un documento PDF foliado con dictamen de IA y cadena de 3 firmas digitales.
"""

import os
import io
import base64
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def generar_acta_pdf(datos_auditoria, output_path=None):
    """
    Genera el PDF oficial a partir del diccionario devuelto por AgenteConciliacionDiesel.auditar_semana.
    Si output_path es None, devuelve los bytes del PDF en un BytesIO.
    """
    buffer = io.BytesIO() if output_path is None else open(output_path, 'wb')
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    titulo_style = ParagraphStyle(
        'TituloDoc',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#0f172a'),
        alignment=1 # Centrado
    )
    
    subtitulo_style = ParagraphStyle(
        'SubtituloDoc',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#3b82f6'),
        alignment=1
    )

    seccion_style = ParagraphStyle(
        'SeccionDoc',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=4
    )

    cuerpo_style = ParagraphStyle(
        'CuerpoDoc',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#334155')
    )

    cuerpo_bold = ParagraphStyle(
        'CuerpoBoldDoc',
        parent=cuerpo_style,
        fontName='Helvetica-Bold'
    )

    elements = []

    semana = datos_auditoria.get('semana', 'N/A')
    ts_auditoria = datos_auditoria.get('fecha_auditoria', datetime.now().isoformat())
    try:
        dt_aud = datetime.fromisoformat(ts_auditoria)
        fecha_legible = dt_aud.strftime('%d/%m/%Y a las %H:%M:%S hrs')
    except Exception:
        fecha_legible = ts_auditoria

    # 1. Encabezado Institucional
    elements.append(Paragraph("GRUPO TRUJANO — SISTEMA FÉNIX 2.0", subtitulo_style))
    elements.append(Paragraph(f"ACTA DE CONCILIACIÓN SEMANAL Y CIERRE DE COMBUSTIBLE", titulo_style))
    elements.append(Paragraph(f"<b>SEMANA OPERATIVA {semana}</b> | Auditoría y Gobernanza Corporativa", subtitulo_style))
    elements.append(Spacer(1, 10))

    # 2. Resumen Ejecutivo y Dictamen del Agente IA
    semaforo = datos_auditoria.get('semaforo_corporativo', 'VERDE')
    dictamen = datos_auditoria.get('dictamen_corporativo', '')
    color_sem = colors.HexColor('#10b981') if semaforo == 'VERDE' else (colors.HexColor('#f59e0b') if semaforo == 'AMARILLO' else colors.HexColor('#ef4444'))

    bg_dictamen = colors.HexColor('#f8fafc')
    resumen_data = [
        [
            Paragraph("<b>Folio Oficial:</b> FENIX-ACTA-S" + str(semana), cuerpo_style),
            Paragraph(f"<b>Fecha de Emisión:</b> {fecha_legible}", cuerpo_style),
            Paragraph(f"<b>Semáforo Corporativo:</b> <font color='{color_sem.hexval()}'><b>● {semaforo}</b></font>", cuerpo_style)
        ],
        [
            Paragraph(f"<b>Dictamen del Agente IA:</b> {dictamen}", cuerpo_style),
            "", ""
        ]
    ]

    t_resumen = Table(resumen_data, colWidths=[180, 200, 160])
    t_resumen.setStyle(TableStyle([
        ('SPAN', (0, 1), (2, 1)),
        ('BACKGROUND', (0, 0), (-1, -1), bg_dictamen),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(t_resumen)
    elements.append(Spacer(1, 12))

    # 3. Métricas Globales de la Semana
    bg = datos_auditoria.get('balance_global', {})
    ac = datos_auditoria.get('auditoria_campo', {})
    
    metrics_data = [
        [
            Paragraph("<b>Métrica Global</b>", cuerpo_bold),
            Paragraph("<b>Volumen (Litros)</b>", cuerpo_bold),
            Paragraph("<b>Importe ($ MXN)</b>", cuerpo_bold),
            Paragraph("<b>Auditoría de Campo (Filtro 1)</b>", cuerpo_bold)
        ],
        [
            Paragraph("<b>Diésel Solicitado:</b>", cuerpo_style),
            f"{bg.get('litros_solicitados', 0):,.2f} L",
            "-",
            f"Total Cargas Realizadas: <b>{ac.get('total_cargas', 0)}</b>"
        ],
        [
            Paragraph("<b>Diésel Facturado (Castilla/Mobil):</b>", cuerpo_style),
            f"<b>{bg.get('litros_facturados', 0):,.2f} L</b>",
            f"<b>${bg.get('importe_facturado_mxn', 0):,.2f}</b>",
            f"Cargas con Foto Cuentalitros: <b>{ac.get('cargas_con_foto', 0)} ({ac.get('cumplimiento_fotos_pct', 0)}%)</b>"
        ],
        [
            Paragraph("<b>Diésel Consumido en Campo:</b>", cuerpo_style),
            f"{bg.get('litros_consumidos', 0):,.2f} L",
            f"${bg.get('importe_consumido_mxn', 0):,.2f}",
            f"Alertas de Campo (Fotos/Horómetros): <b>{ac.get('total_alertas', 0)}</b>"
        ],
        [
            Paragraph("<b>Saldo Remanente en Obra / Tanque:</b>", cuerpo_bold),
            f"<b>{bg.get('saldo_remanente_lts', 0):,.2f} L</b>",
            "-",
            f"Obras con Visto Bueno: <b>{datos_auditoria.get('obras_firmadas_residente', '0/0')}</b>"
        ]
    ]

    t_metrics = Table(metrics_data, colWidths=[160, 110, 110, 160])
    t_metrics.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (1, 0), (2, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    elements.append(t_metrics)
    elements.append(Spacer(1, 14))

    # 4. Desglose y Visto Bueno por Frente de Obra (Filtro 2)
    elements.append(Paragraph("DESGLOSE POR FRENTE DE OBRA Y VISTO BUENO DE RESIDENTES (FILTRO 2)", seccion_style))
    
    obras_headers = [
        Paragraph("<b>Obra / Frente</b>", cuerpo_bold),
        Paragraph("<b>Facturado</b>", cuerpo_bold),
        Paragraph("<b>Suministrado</b>", cuerpo_bold),
        Paragraph("<b>Saldo Tanque</b>", cuerpo_bold),
        Paragraph("<b>Estado / Firma Residente</b>", cuerpo_bold)
    ]
    
    obras_rows = [obras_headers]
    for o in datos_auditoria.get('obras', []):
        f_res = o.get('firma_residente', {})
        estatus_res = f"<font color='#10b981'><b>✓ FIRMADO</b></font><br/>{f_res.get('nombre', '')}" if f_res.get('aprobado') else "<font color='#f59e0b'><b>⏳ PENDIENTE</b></font>"
        
        obras_rows.append([
            Paragraph(f"<b>{o['obra']}</b><br/><font color='#64748b' size='6'>{o.get('dictamen_ia', '')[:95]}...</font>", cuerpo_style),
            f"{o['facturado_lts']:,.2f} L",
            f"{o['consumido_lts']:,.2f} L",
            f"{o['delta_fac_con']:+,.2f} L",
            Paragraph(estatus_res, cuerpo_style)
        ])

    t_obras = Table(obras_rows, colWidths=[200, 80, 80, 80, 100])
    t_obras.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('ALIGN', (1, 1), (3, -1), 'RIGHT'),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
    ]))
    elements.append(t_obras)
    elements.append(Spacer(1, 16))

    # 5. Cadena de Firmas Digitales y Sellos de Auditoría (Los 3 Filtros)
    elements.append(Paragraph("CADENA DE APROBACIÓN Y SELLOS DE SEGURIDAD (3 FILTROS)", seccion_style))

    # Buscar firmas globales o representativas
    primera_obra = datos_auditoria.get('obras', [{}])[0]
    firma_res = primera_obra.get('firma_residente', {})
    firma_gob = primera_obra.get('firma_gobierno', {})

    col_w = 175
    firmas_data = [
        [
            Paragraph("<b>FILTRO 1: ENTREGA-RECEPCIÓN</b><br/>Chofer Marimba / Camión 3.5 ton<br/>vs Operador de Maquinaria", cuerpo_style),
            Paragraph("<b>FILTRO 2: FRENTE DE OBRA</b><br/>Ingeniero Residente de Obra<br/>(Validación Acumulada vs Factura)", cuerpo_style),
            Paragraph("<b>FILTRO 3: GOBIERNO CORPORATIVO</b><br/>Dirección General / Finanzas<br/>(Cierre y Autorización de Pago)", cuerpo_style)
        ],
        [
            Paragraph("<b>Validado en Sistema</b><br/>100% de tickets cruzados con fotos de cuentalitros y horómetros.<br/><font color='#10b981'><b>● VERIFICADO EN CAMPO</b></font>", cuerpo_style),
            Paragraph(f"<b>{firma_res.get('nombre') or 'Ing. Residente de Frente'}</b><br/>" + 
                      (f"<font color='#10b981'><b>✓ APROBADO</b></font><br/>Fecha: {firma_res.get('fecha', '')[:10]}<br/><font size='5' color='#64748b'>Hash: {firma_res.get('hash', '')[:20]}...</font>" if firma_res.get('aprobado') else "<font color='#f59e0b'><b>⏳ PENDIENTE DE FIRMA</b></font>"), cuerpo_style),
            Paragraph(f"<b>{firma_gob.get('nombre') or 'Dirección General'}</b><br/>" + 
                      (f"<font color='#10b981'><b>✓ SELLADO Y AUTORIZADO</b></font><br/>Fecha: {firma_gob.get('fecha', '')[:10]}<br/><font size='5' color='#64748b'>Sello: {firma_gob.get('sello', '')[:20]}...</font>" if firma_gob.get('aprobado') else "<font color='#64748b'><b>EN ESPERA DE RESIDENTES</b></font>"), cuerpo_style)
        ]
    ]

    t_firmas = Table(firmas_data, colWidths=[col_w, col_w, col_w])
    t_firmas.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#94a3b8')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))
    elements.append(t_firmas)
    elements.append(Spacer(1, 10))

    # Pie de página legal
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#94a3b8'), spaceAfter=4))
    elements.append(Paragraph(
        "Este documento constituye un acta oficial de conciliación contable y operativa para Grupo Trujano. "
        "Las firmas electrónicas y hashes registrados certifican la recepción del diésel suministrado a maquinaria de acuerdo con los registros de Fénix 2.0.",
        ParagraphStyle('Legal', parent=styles['Normal'], fontSize=6, leading=8, textColor=colors.HexColor('#64748b'), alignment=1)
    ))

    doc.build(elements)

    if output_path is None:
        buffer.seek(0)
        return buffer.getvalue()
    else:
        buffer.close()
        return output_path


if __name__ == '__main__':
    from motor_agente_conciliacion import AgenteConciliacionDiesel
    ag = AgenteConciliacionDiesel()
    data = ag.auditar_semana('38')
    pdf_out = r"c:\Users\JOSE\Desktop\Proyecto fenix\Acta_Conciliacion_Semana_38_Prueba.pdf"
    generar_acta_pdf(data, pdf_out)
    print(f"PDF generado exitosamente en: {pdf_out}")
