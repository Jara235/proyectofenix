# -*- coding: utf-8 -*-
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def create_fenix_documentation():
    doc = Document()

    # Define Palette
    COLOR_PRIMARY = RGBColor(27, 54, 93)     # #1B365D - Deep Navy
    COLOR_SECONDARY = RGBColor(59, 98, 155)  # #3B629B - Steel Blue
    COLOR_DARK = RGBColor(34, 34, 34)        # #222222 - Charcoal
    COLOR_MUTED = RGBColor(100, 110, 120)    # #646E78 - Slate Gray
    HEX_PRIMARY = "1B365D"
    HEX_SECONDARY = "3B629B"
    HEX_LIGHT_BG = "F2F5F9"
    HEX_ALT_ROW = "F8FAFC"
    HEX_CALLOUT = "EBF2F7"
    HEX_DIAGRAM_BG = "F0F4F8"
    HEX_BORDER = "CBD5E1"

    # Set margins
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Set Base Normal Style
    normal_style = doc.styles['Normal']
    normal_font = normal_style.font
    normal_font.name = 'Calibri'
    normal_font.size = Pt(11)
    normal_font.color.rgb = COLOR_DARK

    # Helper Functions for Formatting
    def set_cell_background(cell, hex_color):
        tcPr = cell._element.get_or_add_tcPr()
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
        tcPr.append(shd)

    def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
        tcPr = cell._element.get_or_add_tcPr()
        tcMar = OxmlElement('w:tcMar')
        for margin_name, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
            node = OxmlElement(f'w:{margin_name}')
            node.set(qn('w:w'), str(val))
            node.set(qn('w:type'), 'dxa')
            tcMar.append(node)
        tcPr.append(tcMar)

    def set_cell_border(cell, **kwargs):
        tcPr = cell._element.get_or_add_tcPr()
        tcBorders = OxmlElement('w:tcBorders')
        for border_name, border_props in kwargs.items():
            b = OxmlElement(f'w:{border_name}')
            b.set(qn('w:val'), border_props.get('val', 'single'))
            b.set(qn('w:sz'), str(border_props.get('sz', 4)))
            b.set(qn('w:space'), '0')
            b.set(qn('w:color'), border_props.get('color', 'auto'))
            tcBorders.append(b)
        tcPr.append(tcBorders)

    def add_title(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(20)
        p.paragraph_format.space_after = Pt(6)
        run = p.add_run(text)
        run.font.name = 'Segoe UI'
        run.font.size = Pt(22)
        run.font.bold = True
        run.font.color.rgb = COLOR_PRIMARY
        return p

    def add_subtitle(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(24)
        run = p.add_run(text)
        run.font.name = 'Segoe UI'
        run.font.size = Pt(12)
        run.font.italic = True
        run.font.color.rgb = COLOR_SECONDARY
        return p

    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Segoe UI'
        run.font.size = Pt(15)
        run.font.bold = True
        run.font.color.rgb = COLOR_PRIMARY
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Segoe UI'
        run.font.size = Pt(12.5)
        run.font.bold = True
        run.font.color.rgb = COLOR_SECONDARY
        return p

    def add_h3(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Calibri'
        run.font.size = Pt(11)
        run.font.bold = True
        run.font.color.rgb = COLOR_PRIMARY
        return p

    def add_p(text, bold_prefix="", space_after=6):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_bold = p.add_run(bold_prefix)
            r_bold.bold = True
            r_bold.font.color.rgb = COLOR_DARK
        r_text = p.add_run(text)
        r_text.font.color.rgb = COLOR_DARK
        return p

    def add_bullet(text, bold_prefix=""):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_bold = p.add_run(bold_prefix)
            r_bold.bold = True
            r_bold.font.color.rgb = COLOR_DARK
        r_text = p.add_run(text)
        r_text.font.color.rgb = COLOR_DARK
        return p

    def add_callout(title, text):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = False
        cell = tbl.cell(0, 0)
        cell.width = Inches(6.5)
        set_cell_background(cell, HEX_CALLOUT)
        set_cell_margins(cell, top=140, bottom=140, left=180, right=140)
        set_cell_border(cell, left={'sz': 24, 'val': 'single', 'color': HEX_PRIMARY},
                              top={'sz': 0, 'val': 'none'},
                              bottom={'sz': 0, 'val': 'none'},
                              right={'sz': 0, 'val': 'none'})
        
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(4)
        r_title = p.add_run(f"📌 {title}\n")
        r_title.bold = True
        r_title.font.name = 'Segoe UI'
        r_title.font.size = Pt(11)
        r_title.font.color.rgb = COLOR_PRIMARY

        r_text = p.add_run(text)
        r_text.font.name = 'Calibri'
        r_text.font.size = Pt(10)
        r_text.font.color.rgb = COLOR_DARK

        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    def add_diagram(title, diagram_text):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = False
        cell = tbl.cell(0, 0)
        cell.width = Inches(6.5)
        set_cell_background(cell, HEX_DIAGRAM_BG)
        set_cell_margins(cell, top=140, bottom=140, left=160, right=140)
        set_cell_border(cell, top={'sz': 8, 'val': 'single', 'color': HEX_PRIMARY},
                              bottom={'sz': 8, 'val': 'single', 'color': HEX_PRIMARY},
                              left={'sz': 8, 'val': 'single', 'color': HEX_PRIMARY},
                              right={'sz': 8, 'val': 'single', 'color': HEX_PRIMARY})
        
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(6)
        r_title = p.add_run(f"📐 DIAGRAMA ARQUITECTÓNICO: {title}\n")
        r_title.bold = True
        r_title.font.name = 'Segoe UI'
        r_title.font.size = Pt(10.5)
        r_title.font.color.rgb = COLOR_PRIMARY

        r_diag = p.add_run(diagram_text)
        r_diag.font.name = 'Consolas'
        r_diag.font.size = Pt(8.5)
        r_diag.font.color.rgb = COLOR_DARK

        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    def style_table(table, col_widths, headers, data):
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False

        # Header Row
        hdr_cells = table.add_row().cells
        for i, header_text in enumerate(headers):
            hdr_cells[i].width = col_widths[i]
            p = hdr_cells[i].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_after = Pt(0)
            run = p.add_run(header_text)
            run.bold = True
            run.font.name = 'Segoe UI'
            run.font.size = Pt(10)
            run.font.color.rgb = RGBColor(255, 255, 255)
            set_cell_background(hdr_cells[i], HEX_PRIMARY)
            set_cell_margins(hdr_cells[i], top=120, bottom=120, left=120, right=120)
            set_cell_border(hdr_cells[i], bottom={'sz': 12, 'val': 'single', 'color': HEX_PRIMARY})

        # Data Rows
        for r_idx, row_data in enumerate(data):
            row_cells = table.add_row().cells
            bg_color = HEX_ALT_ROW if r_idx % 2 == 1 else "FFFFFF"
            for c_idx, cell_value in enumerate(row_data):
                row_cells[c_idx].width = col_widths[c_idx]
                p = row_cells[c_idx].paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.15
                run = p.add_run(str(cell_value))
                run.font.name = 'Calibri'
                run.font.size = Pt(9.5)
                run.font.color.rgb = COLOR_DARK
                set_cell_background(row_cells[c_idx], bg_color)
                set_cell_margins(row_cells[c_idx], top=80, bottom=80, left=100, right=100)
                set_cell_border(row_cells[c_idx], bottom={'sz': 4, 'val': 'single', 'color': HEX_BORDER})

        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # ==========================================
    # COVER PAGE / HEADER METADATA
    # ==========================================
    add_title("DOCUMENTACIÓN TÉCNICA, AUTOMATIZACIÓN n8n Y PLAN DE TRABAJO: SISTEMA FÉNIX 2.0")
    add_subtitle("Manual de Arquitectura de Software, Motor de Automatizaciones n8n con IA (Gemini 1.5 Flash), Sistema de Conciliación de 2 Vías, Matriz de Permisos RBAC, Plan de Trabajo con Metas e Impacto ISO 9001/14001")

    # Document Metadata Block
    meta_table = doc.add_table(rows=0, cols=2)
    style_table(
        meta_table,
        [Inches(2.2), Inches(4.3)],
        ["Parámetro de Control", "Detalle Institucional"],
        [
            ["Código del Documento", "PR-IT-001-FENIX (Documento Maestro)"],
            ["Nombre del Sistema", "Sistema Fénix 2.0 — Control Operativo, Automatización y Finanzas"],
            ["Versión del Sistema", "2.0 (Snapshot Producción - Agosto 2026)"],
            ["Empresa / Organización", "Grupo Trujano"],
            ["Motor de Automatización", "n8n (Workflows Email IMAP, Drive, Webhooks, Gemini 1.5 Flash AI)"],
            ["Modelo de Conciliación", "Conciliación Multinivel de 2 Vías (Distribuidor / Marimba / Obra)"],
            ["Seguridad y Acceso", "Gobierno Corporativo con Cierre y Bloqueo Definitivo de Datos"],
            ["Plan de Trabajo", "Hitos Ejecutados (Fases 1 a 6) y Hitos Proyectados (Fase 7)"],
            ["Alcance Normativo", "Certificación ISO 9001:2015 (Calidad) e ISO 14001:2015 (Ambiental)"]
        ]
    )

    add_callout(
        "Directiva de Documentación Profesional Exhaustiva",
        "El presente documento técnico integra la arquitectura completa del Sistema Fénix 2.0: "
        "desde la justificación estratégica, la matriz de permisos RBAC y el modelo de conciliación de 2 vías, "
        "hasta el desglose detallado del Motor de Automatizaciones en n8n (procesamiento de facturas por correo, "
        "agente de IA multimodal Gemini 1.5 Flash para WhatsApp, webhooks de conciliación) y el Plan de Trabajo "
        "formal con todas las metas alcanzadas y futuras."
    )

    # ==========================================
    # SECCIÓN 1: INTRODUCCIÓN, CONTEXTO Y JUSTIFICACIÓN
    # ==========================================
    add_h1("1. INTRODUCCIÓN, CONTEXTO Y JUSTIFICACIÓN (“¿POR QUÉ Y PARA QUÉ?”)")
    
    add_h2("1.1 Antecedentes y Problemática Operativa Inicial (“¿Por qué?”)")
    add_p(
        "Antes del desarrollo del Sistema Fénix, la gestión del suministro de combustible (diésel y gasolina), el transporte "
        "en camiones cisterna ('Marimbas'), el movimiento de acarreos y el control de insumos en Grupo Trujano se realizaba "
        "mediante procesos manuales basados en vales de papel, reportes informales por mensajes de texto y carpetas dispersas de Microsoft Excel. "
        "Esta metodología provocaba serias deficiencias operativas y financieras:"
    )
    add_bullet("Dispersión y pérdida de vales de surtimiento físicos en campo y estaciones de servicio.", "Pérdida de Información: ")
    add_bullet("Cargas facturadas por estaciones de servicio que no coincidían con lo realmente recibido en tanques u obras.", "Falta de Conciliación: ")
    add_bullet("Imposibilidad de atribuir con exactitud el consumo de litros por máquina, frente de trabajo o ingeniero responsable.", "Opacidad en Costos: ")
    add_bullet("Incapacidad de detectar si un mismo ticket o factura CFDI era registrado dos veces en la contabilidad.", "Riesgo de Duplicidad: ")
    add_bullet("Dificultad para identificar fugas, mermas indebidas en trasvases o desviaciones de volumen en pipas.", "Mermas No Explicadas: ")
    add_bullet("Desconexión entre el consumo de combustible y la productividad de la maquinaria pesada en obra.", "Falta de Rendimiento: ")

    add_h2("1.2 Misión y Propósito Fundamental (“¿Para qué?”)")
    add_p(
        "El Sistema Fénix fue concebido como una plataforma digital integral de control operativo, contable y ambiental "
        "diseñada para centralizar y auditar el ciclo de vida completo del combustible dentro de Grupo Trujano. "
        "Sus objetivos fundamentales son:"
    )
    add_bullet("Garantizar la coincidencia matemática exacta al centavo entre la solicitud, la factura del proveedor y el consumo entregado.", "1. Auditoría Financiera Total: ")
    add_bullet("Establecer un registro inalterable con folios únicos, estampa de tiempo, usuario y auditoría de cambios para cada litro.", "2. Trazabilidad Inalterable: ")
    add_bullet("Implementar techos presupuestales diarios multiplicados por días trabajados reales para evitar sobrecostos.", "3. Control Presupuestal Automatizado: ")
    add_bullet("Efectuar el cruce de datos entre el emisor (gasolinería/tanque) y el receptor (pipa/obra) para validar transferencias.", "4. Modelo de Conciliación en Pareja: ")
    add_bullet("Reducir a 0ms la búsqueda de unidades y autocompletar responsables para agilizar la operación en campo.", "5. Eficiencia en Captura: ")

    # ==========================================
    # SECCIÓN 2: PLAN DE TRABAJO, HITOS Y METAS DEL PROYECTO
    # ==========================================
    add_h1("2. PLAN DE TRABAJO, HITOS Y METAS DEL PROYECTO FÉNIX")
    add_p(
        "El desarrollo e implementación del Sistema Fénix se estructura en un Plan de Trabajo de 7 Fases. "
        "A continuación se presenta el estado de avance, los entregables producidos y las metas proyectadas:"
    )

    style_table(
        doc.add_table(rows=0, cols=4),
        [Inches(1.2), Inches(2.0), Inches(2.1), Inches(1.2)],
        ["Fase / Etapa", "Objetivo / Meta", "Entregables Técnicos Producidos", "Estatus"],
        [
            [
                "Fase 1",
                "Diagnóstico, Modelado de BD PostgreSQL y Alineación ISO",
                "• Esquema relacional PostgreSQL `fenix_db` (16 tablas).\n• Documentación de arquitectura ISO 9001 / 14001.\n• Definición de modelo de conciliación de 2 vías.",
                "✅ COMPLETADO (100%)"
            ],
            [
                "Fase 2",
                "Portal de Captura Operativa (Puerto 5001)",
                "• `app_captura.py` con autocompletado en 0ms.\n• Servicio `bitacora_pdf_service.py` para lectura inteligente.\n• Captura masiva Excel Levet/JDJ con algoritmo $O(1)$.",
                "✅ COMPLETADO (100%)"
            ],
            [
                "Fase 3",
                "Centro de Mando Administrativo (Puerto 5002)",
                "• `app_admin.py` con regla normada 6D/5D.\n• Generadores ejecutivos de Excel y PDF con firmas.\n• Módulo CFDI XML y Complementos de Pago SAT (Folio 58914).",
                "✅ COMPLETADO (100%)"
            ],
            [
                "Fase 4",
                "Motor de Automatización en n8n e IA Gemini 1.5 Flash",
                "• Ingestión automática de correos IMAP de proveedores.\n• Guardado en Google Drive y BD de facturas.\n• Webhook de conciliación en vivo y agente IA para WhatsApp.",
                "✅ COMPLETADO (100%)"
            ],
            [
                "Fase 5",
                "Módulos Especializados: Jalisco, Acarreos, Mezcla y Tags",
                "• Módulo Jalisco con vales y fotos.\n• Conciliación de acarreos y mezcla con fotos obligatorias vs Plantas.\n• Imputación de casetas de telepeaje Tags a obras.",
                "✅ COMPLETADO (100%)"
            ],
            [
                "Fase 6",
                "Gobierno Corporativo y Bloqueo de Información",
                "• Implementación de Triggers de congelamiento de periodos.\n• Matriz de permisos RBAC por usuario.\n• Log inalterable `catalogos.audit_log` y protocolo de desbloqueo.",
                "✅ EN PRODUCCIÓN (100%)"
            ],
            [
                "Fase 7 (Futura)",
                "PWA Offline-First, IoT y Visión Artificial OCR",
                "• PWA con IndexedDB local para sincronización en zonas sin red.\n• Flujómetros digitales IoT en pipas Marimba y tanques Pegaso.\n• Módulo OCR para lectura de tickets con la cámara del celular.",
                "🚀 HITOS SIGUIENTES"
            ]
        ]
    )

    # ==========================================
    # SECCIÓN 3: MOTOR DE AUTOMATIZACIÓN INTEGRAL CON n8n E IA
    # ==========================================
    add_h1("3. MOTOR DE AUTOMATIZACIÓN INTEGRAL CON n8n E INTELIGENCIA ARTIFICIAL (GEMINI 1.5 FLASH)")
    add_p(
        "El servidor de automatización **n8n** constituye la capa de integración de procesos en segundo plano de Grupo Trujano. "
        "Conecta de forma transparente las fuentes externas (correos de proveedores, Google Drive, WhatsApp Meta API) "
        "con la base de datos PostgreSQL y el Centro de Mando Fénix Admin (Puerto 5002)."
    )

    add_h2("3.1 Flujo 01: Ingestión Automática de Facturas por Correo IMAP y Respaldo en Google Drive")
    add_p("Fichero de flujo: `n8n/workflows/01_ingestion_email_drive_facturas_diesel.json`.")
    add_bullet("Monitorea la bandeja de correo electrónico institucional vía IMAP (puerto 993 SSL) filtrando exclusivamente remitentes oficiales como DERIVADOS DE PETROLEO CASTILLA (facturaciondpc2@gmail.com / RFC DPC180725R47) con patrones de asunto de CFDI de combustible.", "1. Trigger IMAP Automático: ")
    add_bullet("Descarga los archivos adjuntos (XML CFDI 4.0 y PDF de la factura) y los organiza dinámicamente en carpetas de Google Drive estructuradas por semana (ej. SEM_34_factura.pdf).", "2. Respaldo en Google Drive: ")
    add_bullet("Lee el archivo XML del CFDI y extrae con precisión quirúrgica: Serie, Folio, Fecha, UUID de 36 caracteres, Litros Facturados, Precio Unitario, Subtotal, IVA e Importe Total.", "3. Extracción de Datos XML CFDI: ")
    add_bullet("Inserta automáticamente el registro en la base de datos PostgreSQL (tabla diesel.facturas) con el estatus inicial 'PENDIENTE_OBRA'.", "4. Registro en PostgreSQL: ")
    add_bullet("Envía una notificación por Webhook al Centro de Mando Admin Fénix (http://localhost:5002/api/admin/diesel/webhook_nueva_factura). La factura aparece instantáneamente en el tab '🧾 Facturas' para la Asignación Humana de Obra Destino con 1-clic.", "5. Notificación al Admin (Puerto 5002): ")

    add_h2("3.2 Flujo 02: Conciliación Automática Factura vs Cargas de Obra y Semáforo en Tiempo Real")
    add_p("Fichero de flujo: `n8n/workflows/02_conciliacion_diesel_factura_vs_cargas.json`.")
    add_bullet("Expone un endpoint Webhook REST: POST /webhook/fenix-conciliacion-diesel.", "1. Endpoint Webhook: ")
    add_bullet("Suma los litros facturados por el proveedor y los compara contra la suma de cargas individuales registradas en campo por la pipa Marimba y los operadores en la obra asignada.", "2. Comparativo de Volúmenes: ")
    add_bullet("Audita que cada carga individual cuente con la foto de evidencia obligatoria (medidor de marimba, manguera a máquina, horómetro).", "3. Auditoría de Evidencia: ")
    add_bullet("Retorna el balance y genera el Semáforo de Control en tiempo real:\n  • 🟢 CONCILIADO: Coincidencia matemática exacta entre factura y cargas.\n  • 🟡 SALDO EN TANQUE/PIPA: Volumen facturado pendiente por repartir en la pipa o tanque.\n  • 🔴 MERMA / EXCESO: Discrepancia no explicada que activa alertas contables.", "4. Generación de Semáforo: ")

    add_h2("3.3 Flujo 03: Ingestión de WhatsApp con Inteligencia Artificial Multimodal (Gemini 1.5 Flash)")
    add_p("Permite el procesamiento de mensajes de texto y fotografías de tickets enviados por los choferes y operadores al grupo de WhatsApp corporativo.")
    add_bullet("Webhook de Meta Developers apuntando a /webhook/whatsapp.", "1. Webhook Trigger: ")
    add_bullet("Si el mensaje incluye imagen de ticket o marcador, descarga el archivo binario.", "2. Descarga Multimodal: ")
    add_bullet("Pasa el texto y/o la imagen al modelo Google Gemini 1.5 Flash en n8n mediante un System Prompt especializado que clasifica la transacción en 'pegaso', 'marimba' u 'obra', resuelve los códigos de catálogos (ej. MT, L3M, EX-01, FR-01) y devuelve un objeto JSON estructurado.", "3. Agente de IA Gemini 1.5 Flash: ")
    add_bullet("Un nodo Switch evalúa la categoría devuelta e inserta directamente en la tabla correspondiente de PostgreSQL (o en la bandeja de revisión si requiere intervención manual).", "4. Router e Inserción en BD: ")

    add_h2("3.4 Flujo 04: Cierre Diario, Alertas Nocturnas a las 8:00 PM y Expansión Futura")
    add_bullet("Un disparador Cron ejecuta automáticamente un barrido todas las noches a las 8:00 PM para verificar que todas las cargas del día hayan sido conciliadas y que no existan excedentes presupuestales.", "Cierre Diario Nocturno: ")
    add_bullet("Envío de notificaciones por WhatsApp / Telegram / Email a los administradores si se detectan mermas o solicitudes sin factura respaldada.", "Alertas Automáticas: ")
    add_bullet("Respuestas automáticas bidireccionales por WhatsApp Business informando al ingeniero el estatus de aprobación de su solicitud de diésel. Integración por Webhooks con sistemas contables/ERP (CONTPAQi / SAP / COI).", "Ampliación Proyectada: ")

    add_diagram(
        "Arquitectura del Motor de Automatizaciones en n8n",
        " ┌────────────────────────────────────────────────────────────────────────┐\n"
        " │                         FUENTES EXTERNAS DE DATOS                       │\n"
        " │   [Correo IMAP Castilla]     [WhatsApp Meta API]      [Google Drive]   │\n"
        " └───────────────────┬──────────────────────┬────────────────────┬────────┘\n"
        "                     │                      │                    │\n"
        "                     ▼                      ▼                    ▼\n"
        " ┌────────────────────────────────────────────────────────────────────────┐\n"
        " │                      SERVIDOR DE AUTOMATIZACIÓN n8n                    │\n"
        " │                                                                        │\n"
        " │  ┌────────────────────────┐  ┌──────────────────────────────────────┐  │\n"
        " │  │ Flujo 01: Ingestión    │  │ Flujo 03: Agente IA Gemini 1.5 Flash │  │\n"
        " │  │ Facturas IMAP/Drive    │  │ (Clasifica WhatsApp y Fotos Tickets) │  │\n"
        " │  └───────────┬────────────┘  └──────────────────┬───────────────────┘  │\n"
        " │              │                                  │                      │\n"
        " │              ▼                                  ▼                      │\n"
        " │  ┌──────────────────────────────────────────────────────────────────┐  │\n"
        " │  │ Flujo 02: Motor de Conciliación y Semáforo en Tiempo Real        │  │\n"
        " │  │ (🟢 Exacto | 🟡 Saldo Pipa | 🔴 Merma/Exceso)                   │  │\n"
        " │  └───────────────────────────┬──────────────────────────────────────┘  │\n"
        " └──────────────────────────────┼─────────────────────────────────────────┘\n"
        "                                │\n"
        "                                ▼\n"
        " ┌────────────────────────────────────────────────────────────────────────┐\n"
        " │                   POSTGRESQL (fenix_db) & ADMIN 5002                   │\n"
        " │             [Notificación a Fénix Admin para Asignación 1-Clic]        │\n"
        " └────────────────────────────────────────────────────────────────────────┘"
    )

    # ==========================================
    # SECCIÓN 4: SISTEMA DE CONCILIACIÓN MULTINIVEL DE 2 VÍAS
    # ==========================================
    add_h1("4. SISTEMA DE CONCILIACIÓN MULTINIVEL DE 2 VÍAS Y GOBIERNO CORPORATIVO")
    add_p(
        "El núcleo arquitectónico del Sistema Fénix opera bajo un **Modelo de Conciliación de 2 Vías a través de Niveles**. "
        "A diferencia de los sistemas tradicionales que confían en una sola fuente de reporte, Fénix exige que cada transferencia "
        "de volumen sea declarada de manera independiente por ambas partes (Emisor y Receptor), efectuando cruces automáticos en cada nivel."
    )

    add_h2("4.1 Estructura por Niveles de Conciliación")

    add_h3("• NIVEL 1: Distribuidor de Combustible (Gasolinería / Proveedor) vs Operadores (Tanque / Pipa)")
    add_p(
        "En el primer nivel, la gasolinería proveedora (ej. Gasolinera Huixquilucan / Levet / JDJ) emite el reporte de carga "
        "y la factura formal. Por su parte, el Operador del Tanque Pegaso o el Chofer de la Pipa 'Marimba' registra la entrada física del combustible "
        "recibido. El sistema efectúa el Cruce Nivel 1: Litros Facturados por el Distribuidor = Litros Ingresados al Tanque/Pipa."
    )

    add_h3("• NIVEL 2: Cargas Individuales (Operadores de Pipa/Tanque) vs Cargas de Máquinas (Ingeniero de Obra)")
    add_p(
        "En el segundo nivel se audita la distribución fina en campo. El operador de la pipa/tanque declara los litros despachados "
        "a cada frente de trabajo. Simultáneamente, el Ingeniero o Responsable de Obra registra el volumen exacto recibido por cada máquina "
        "individual (equipo económico, horómetro/odómetro y fotografía obligatoria). El sistema efectúa el Cruce Nivel 2: Litros Despachados por Pipa/Tanque = Suma de Cargas Individuales en Maquinaria de Obra."
    )

    add_h3("• NIVEL 3: Cargas Individuales y Repartos vs Facturas Emitidas (Auditoría Contable)")
    add_p(
        "El sistema vincula la suma de consumos acumulados por máquina e ingeniero contra las facturas fiscales (CFDI XML) "
        "y estados de cuenta del distribuidor. Se valida el precio por litro, el IVA aplicable y los Complementos de Pago del SAT, "
        "detectando discrepancias de centavos o volumen no amparado."
    )

    add_h3("• NIVEL 4: Gobierno Corporativo y Bloqueo Definitivo de Información")
    add_p(
        "Una vez verificado que los Cruces Nivel 1, 2 y 3 coinciden al 100%, el equipo de Administración y Gobierno Corporativo "
        "ejecuta la acción de **CIERRE Y BLOQUEO DE INFORMACIÓN**. A partir de este momento, la base de datos PostgreSQL **congela** "
        "todos los registros del periodo conciliado. Ningún usuario operativo (operadores o ingenieros) puede modificar, eliminar "
        "o agregar datos de manera retroactiva. La información queda sellada para la emisión de reportes ejecutivos a la Alta Dirección."
    )

    add_diagram(
        "Estructura Multinivel de Conciliación de 2 Vías y Gobierno Corporativo",
        " ┌────────────────────────────────────────────────────────────────────────┐\n"
        " │                 DISTRIBUIDOR DE COMBUSTIBLE (PROVEEDOR)                │\n"
        " │                      (Factura CFDI / Estado de Cuenta)                 │\n"
        " └───────────────────────────────────┬────────────────────────────────────┘\n"
        "                                     │ [CRUCE NIVEL 1]\n"
        "                                     ▼\n"
        " ┌────────────────────────────────────────────────────────────────────────┐\n"
        " │             OPERADORES DE TANQUE PEGASO Y PIPA 'MARIMBA'               │\n"
        " │                      (Registro de Entradas y Salidas)                  │\n"
        " └───────────────────────────────────┬────────────────────────────────────┘\n"
        "                                     │ [CRUCE NIVEL 2]\n"
        "                                     ▼\n"
        " ┌────────────────────────────────────────────────────────────────────────┐\n"
        " │                INGENIEROS Y RESPONSABLES DE OBRA                       │\n"
        " │          (Cargas Individuales por Máquina + Foto + Horómetro)          │\n"
        " └───────────────────────────────────┬────────────────────────────────────┘\n"
        "                                     │ [CRUCE NIVEL 3: Contable al Centavo]\n"
        "                                     ▼\n"
        " ┌────────────────────────────────────────────────────────────────────────┐\n"
        " │                   GOBIERNO CORPORATIVO / ADMINISTRACIÓN                 │\n"
        " │            [REVISIÓN FINAL Y BLOQUEO DEFINITIVO DE INFORMACIÓN]        │\n"
        " │           (Información congelada / Solo modificable por SuperAdmin)    │\n"
        " └───────────────────────────────────┬────────────────────────────────────┘\n"
        "                                     │\n"
        "                                     ▼\n"
        "                      📊 REPORTES EJECUTIVOS A DIRECTIVOS"
    )

    # ==========================================
    # SECCIÓN 5: MATRIZ DE ROLES Y SEGURIDAD RBAC
    # ==========================================
    add_h1("5. MATRIZ DE ROLES, NIVELES DE ACCESO Y SEGURIDAD EN LA BASE DE DATOS")
    add_p(
        "Para garantizar la integridad de los datos, el cumplimiento ISO 9001/14001 y evitar manipulaciones no autorizadas, "
        "el Sistema Fénix 2.0 implementa una **Matriz de Control de Acceso Basado en Roles (RBAC)** con 4 niveles jerárquicos estrictos:"
    )

    style_table(
        doc.add_table(rows=0, cols=4),
        [Inches(1.2), Inches(1.5), Inches(2.3), Inches(1.5)],
        ["Nivel de Acceso", "Rol de Usuario", "Permisos Operativos y Funciones En Base de Datos", "Alcance de Edición / Bloqueo"],
        [
            [
                "Nivel 1: Básico",
                "Operadores de Maquinaria / Choferes",
                "• Captura básica de carga individual asignada a su unidad.\n• Registro obligatorio de Horómetro/Kilometraje.\n• Subida obligatoria de FOTO EVIDENCIA del ticket/marcador.",
                "INSERT únicamente en registros propios del día. Sin acceso a consulta global ni edición."
            ],
            [
                "Nivel 2: Operativo",
                "Operador de Marimba / Pipa / Tanque",
                "• Captura de entradas de combustible desde gasolinerías.\n• Registro de despachos y cargas enviadas a cada obra.\n• Subida de fotos de marcadores de tanque y remisiones.",
                "INSERT y UPDATE limitado al día corriente. No puede modificar registros pasados."
            ],
            [
                "Nivel 3: Supervisión",
                "Ingenieros / Responsables de Obra",
                "• Solicitud semanal de presupuesto de diésel.\n• Petición de autorizaciones extra (gasolina/diésel).\n• Registro de EPP/PPE, reportes mecánicos/piezas y reporte de obra.\n• Supervisión de cargas de sus equipos.\n• Revisión de Acarreos y Mezclas Asfálticas (verificación de fotos de notas/boletas y conciliación vs Plantas).",
                "INSERT y SELECT de sus obras asignadas. Modificación permitida solo antes del cierre semanal."
            ],
            [
                "Nivel 4: Ejecutivo / Gobierno Corporativo",
                "Administradores / Auditores / Directivos",
                "• Conciliación contable masiva de facturas CFDI vs cargas.\n• Edición de catálogos maestros y cuotas diarias (6D/5D).\n• **BLOQUEO Y CIERRE DEFINITIVO DE PERIODOS**.\n• Generación de reportes institucionales Excel/PDF.\n• Consulta de la tabla inalterable catalogos.audit_log.",
                "FULL ACCESS (SELECT, INSERT, UPDATE, DELETE, LOCK). Permiso especial exclusivo para desbloqueo."
            ]
        ]
    )

    # ==========================================
    # SECCIÓN 6: CONCILIACIÓN DE ACARREOS Y MEZCLA ASFÁLTICA
    # ==========================================
    add_h1("6. CONCILIACIÓN ESPECIALIZADA DE ACARREOS Y MEZCLA ASFÁLTICA CONTRA PLANTAS")
    add_p(
        "El control de materiales, fresado y mezcla asfáltica sigue un procedimiento riguroso de conciliación cruzada "
        "entre las Plantas de Asfalto corporativas (Huixquilucan / Pegaso), los transportistas (Sindicatos/Camiones) "
        "y los Ingenieros de Obra recepcionistas."
    )

    add_bullet("La Planta de Asfalto genera la nota de remisión digital y física con el peso/tonelaje exacto ($t$) o cubicaje ($m^3$) de la mezcla producida.", "1. Salida de Planta: ")
    add_bullet("El chofer del camión traslada el material al tramo en obra.", "2. Transporte: ")
    add_bullet("El Ingeniero de Obra recibe el camión, captura los datos de la nota en el Portal 5001 y sube **OBLIGATORIAMENTE LA FOTOGRAFÍA CLARA Y LEGIBLE DE LA NOTA / BOLETA**.", "3. Recepción en Obra + Foto Obligatoria: ")
    add_bullet("El sistema Fénix cruza las toneladas emitidas por la Planta vs las toneladas recibidas en Obra vs las boletas amparadas en la factura del Sindicato/Transportista.", "4. Conciliación Automática en Fénix: ")

    add_diagram(
        "Flujo de Conciliación de Mezcla Asfáltica (Planta vs Obra + Foto Nota)",
        " ┌──────────────────────────┐         ┌──────────────────────────┐\n"
        " │ PLANTA DE ASFALTO        │         │ INGENIERO DE OBRA        │\n"
        " │ (Huixquilucan / Pegaso)  │         │ (Recepción en Tramo)     │\n"
        " └────────────┬─────────────┘         └────────────┬─────────────┘\n"
        "              │                                    │\n"
        "              │ Emite Mezcla                       │ Recibe Camión\n"
        "              │ y Nota de Salida                   │ y Revisa Nota\n"
        "              ▼                                    ▼\n"
        " ┌──────────────────────────┐         ┌──────────────────────────┐\n"
        " │ REGISTRO DE PLANTA       │         │ CAPTURA EN PORTAL 5001   │\n"
        " │ (Toneladas Producidas)   │         │ + FOTO OBLIGATORIA NOTA  │\n"
        " └────────────┬─────────────┘         └────────────┬─────────────┘\n"
        "              │                                    │\n"
        "              └─────────────────┬──────────────────┘\n"
        "                                │\n"
        "                                ▼\n"
        " ┌───────────────────────────────────────────────────────────────┐\n"
        " │                  MOTOR DE CONCILIACIÓN FÉNIX                  │\n"
        " │     [Valida: Toneladas Planta = Toneladas Obra + Foto Nota]   │\n"
        " └────────────┬──────────────────────────────────────────────────┘\n"
        "              │\n"
        "              ▼\n"
        " 🔒 APROBACIÓN Y BLOQUEO CORPORATIVO"
    )

    # ==========================================
    # SECCIÓN 7: VISIÓN A FUTURO Y HOJA DE RUTA
    # ==========================================
    add_h1("7. VISIÓN A FUTURO Y HOJA DE RUTA DE EVOLUCIÓN TECNOLÓGICA")
    add_p(
        "El Sistema Fénix 2.0 sienta las bases para una transformación digital continua. La visión a futuro contempla "
        "convertir el sistema en una plataforma autónoma e inteligente respaldada por las siguientes innovaciones:"
    )

    add_h2("7.1 Aplicación Móvil PWA y Cliente Nativo Offline-First")
    add_p(
        "Dado que muchas obras de infraestructura se ejecutan en zonas con cobertura de red nula o intermitente, "
        "se desarrollará la evolución a una Progressive Web App (PWA) e integración nativa móvil con motor de base de datos "
        "local (IndexedDB / SQLite local en el dispositivo). "
        "Los operadores capturarán las transacciones localmente y los Service Workers sincronizarán automáticamente "
        "con el servidor PostgreSQL central tan pronto como el dispositivo detecte señal de red."
    )

    add_h2("7.2 Integración IoT y Telemetría Automática en Sensores")
    add_bullet("Instalación de flujómetros digitales calibrados conectados por IoT en la manguera de despacho de la pipa 'Marimba', registrando automáticamente cada descarga en la BD.", "Flujómetros Digitales en Pipas: ")
    add_bullet("Sensores ultrasónicos de nivel en el Tanque Pegaso (20,000 L) y Tanque Huixquilucan para monitoreo continuo de inventarios en tiempo real y detección automática de fugas.", "Medición de Tanques Fijos: ")
    add_bullet("Conexión con dispositivos GPS/CAN-Bus en maquinaria pesada para correlacionar horómetros y kilómetros reales con los litros suministrados.", "Telemetría de Maquinaria: ")

    add_h2("7.3 Reconocimiento Óptico de Caracteres (OCR) en Visión Artificial")
    add_p(
        "Módulo de procesamiento de imágenes que permitirá a los choferes fotocopiar el ticket de la gasolinería "
        "o la boleta de acarreo con la cámara de su celular. El motor OCR extraerá automáticamente el folio, la fecha, los litros, "
        "el costo total y el número económico, eliminando el tecleo manual."
    )

    # ==========================================
    # SECCIÓN 8: ARQUITECTURA DE LA BASE DE DATOS RELACIONAL
    # ==========================================
    add_h1("8. ARQUITECTURA DE LA BASE DE DATOS RELACIONAL (`fenix_db`)")
    add_p(
        "El soporte de almacenamiento persistente del Sistema Fénix 2.0 es una base de datos relacional PostgreSQL 16 "
        "alojada localmente (`localhost:5432`). Garantiza cumplimiento de propiedades ACID (Atomicidad, Consistencia, Aislamiento, Durabilidad) "
        "y un estricto esquema relacional dividido por dominios operacionales (schemas)."
    )

    add_h2("8.1 Esquema Relacional de Tablas Maestras")

    # Table 1: Diesel Scheme
    add_h3("A) Esquema Diésel (`diesel`)")
    add_p("Concentra la gestión de solicitudes, despachos, facturas y complementos de pago para combustible pesado.")
    style_table(
        doc.add_table(rows=0, cols=4),
        [Inches(1.8), Inches(1.2), Inches(1.0), Inches(2.5)],
        ["Nombre de Tabla", "Columna / Campo", "Tipo de Dato", "Restricciones / Descripción"],
        [
            ["diesel.consumos", "id", "BIGINT", "PRIMARY KEY, AUTOINCREMENT"],
            ["diesel.consumos", "folio_conciliacion", "TEXT", "UNIQUE, NOT NULL. Identificador de cruce"],
            ["diesel.consumos", "fecha", "DATE / TEXT", "NOT NULL. Fecha del despacho"],
            ["diesel.consumos", "semana", "INTEGER", "NOT NULL. Semana ISO del año"],
            ["diesel.consumos", "origen", "TEXT", "Punto de emisión (ej. Gasolinera / Tanque Pegaso)"],
            ["diesel.consumos", "obra_destino", "TEXT", "FK -> catalogos.obras(nombre)"],
            ["diesel.consumos", "equipo_economico", "TEXT", "FK -> catalogos.equipos(numero_economico)"],
            ["diesel.consumos", "litros", "NUMERIC(12,2)", "NOT NULL. Cantidad suministrada"],
            ["diesel.consumos", "costo_por_litro", "NUMERIC(10,2)", "Precio unitario del diésel"],
            ["diesel.consumos", "importe_total", "NUMERIC(14,2)", "NOT NULL. Litros × Costo/L"],
            ["diesel.consumos", "responsable", "TEXT", "Ingeniero a cargo de la obra"],
            ["diesel.solicitudes", "id", "INTEGER", "PRIMARY KEY, AUTOINCREMENT"],
            ["diesel.solicitudes", "semana", "INTEGER", "NOT NULL. Semana solicitada"],
            ["diesel.solicitudes", "litros_solicitados", "NUMERIC(12,2)", "NOT NULL. Volumen requerido"],
            ["diesel.solicitudes", "estatus", "TEXT", "DEFAULT 'Pendiente' (Aprobado / Rechazado)"],
            ["diesel.facturas", "id", "INTEGER", "PRIMARY KEY, AUTOINCREMENT"],
            ["diesel.facturas", "folio_factura", "TEXT", "NOT NULL. Folio impreso del proveedor"],
            ["diesel.facturas", "uuid_cfdi", "TEXT", "UUID de 36 caracteres del SAT"],
            ["diesel.facturas", "importe_total", "NUMERIC(14,2)", "NOT NULL. Monto total con IVA"]
        ]
    )

    # Table 2: Gasolina Scheme
    add_h3("B) Esquema Gasolina (`gasolina`)")
    add_p("Controla la flotilla ligera, el autocompletado en 0ms y el concilio masivo desde archivos Excel.")
    style_table(
        doc.add_table(rows=0, cols=4),
        [Inches(1.8), Inches(1.2), Inches(1.0), Inches(2.5)],
        ["Nombre de Tabla", "Columna / Campo", "Tipo de Dato", "Restricciones / Descripción"],
        [
            ["gasolina.consumos", "id", "BIGINT", "PRIMARY KEY, AUTOINCREMENT"],
            ["gasolina.consumos", "folio_conciliacion", "TEXT", "UNIQUE, NOT NULL"],
            ["gasolina.consumos", "fecha", "DATE / TEXT", "NOT NULL"],
            ["gasolina.consumos", "semana", "INTEGER", "NOT NULL. Semana ISO"],
            ["gasolina.consumos", "placa", "TEXT", "Placa del vehículo o 'S/P'"],
            ["gasolina.consumos", "vehiculo", "TEXT", "Marca, modelo y número económico"],
            ["gasolina.consumos", "conductor", "TEXT", "Conductor responsable asignado"],
            ["gasolina.consumos", "obra_destino", "TEXT", "Obra o centro de costo"],
            ["gasolina.consumos", "litros", "NUMERIC(10,2)", "NOT NULL. Litros despachados"],
            ["gasolina.consumos", "importe_total", "NUMERIC(12,2)", "NOT NULL. Importe cobrado"],
            ["gasolina.autorizaciones_maestro", "placa", "TEXT", "PRIMARY KEY. Utilizada para autocompletado 0ms"],
            ["gasolina.autorizaciones_maestro", "vehiculo", "TEXT", "Nombre registrado del vehículo"],
            ["gasolina.autorizaciones_maestro", "conductor", "TEXT", "Conductor habitual"],
            ["gasolina.autorizaciones_maestro", "obra_asignada", "TEXT", "Obra por defecto"]
        ]
    )

    # Table 3: Catalogos Scheme
    add_h3("C) Esquema Catálogos y Auditoría (`catalogos`)")
    add_p("Mantiene el padrón maestro corporativo y la bitácora inalterable de cambios.")
    style_table(
        doc.add_table(rows=0, cols=4),
        [Inches(1.8), Inches(1.2), Inches(1.0), Inches(2.5)],
        ["Nombre de Tabla", "Columna / Campo", "Tipo de Dato", "Restricciones / Descripción"],
        [
            ["catalogos.responsables", "id", "INTEGER", "PRIMARY KEY, AUTOINCREMENT"],
            ["catalogos.responsables", "nombre", "TEXT", "NOT NULL, UNIQUE. Nombre del Ingeniero"],
            ["catalogos.responsables", "dias_trabajados", "INTEGER", "NOT NULL. Regla de negocio (6 ó 5 Días)"],
            ["catalogos.responsables", "autorizado_diario", "NUMERIC(10,2)", "NOT NULL. Cuota diaria en Litros"],
            ["catalogos.obras", "codigo", "TEXT", "PRIMARY KEY. Clave corta de la obra"],
            ["catalogos.obras", "nombre", "TEXT", "NOT NULL, UNIQUE. Nombre oficial"],
            ["catalogos.equipos", "numero_economico", "TEXT", "PRIMARY KEY. Ej. 'EX-01'"],
            ["catalogos.equipos", "descripcion", "TEXT", "Descripción de la máquina / vehículo"],
            ["catalogos.audit_log", "id", "BIGINT", "PRIMARY KEY, AUTOINCREMENT"],
            ["catalogos.audit_log", "tabla_afectada", "TEXT", "Nombre de la tabla modificada"],
            ["catalogos.audit_log", "registro_id", "TEXT", "ID del registro alterado"],
            ["catalogos.audit_log", "usuario", "TEXT", "Usuario que ejecutó la acción"],
            ["catalogos.audit_log", "accion", "TEXT", "'INSERT', 'UPDATE' o 'DELETE'"],
            ["catalogos.audit_log", "valor_anterior", "TEXT / JSON", "Estado previo a la modificación"],
            ["catalogos.audit_log", "valor_nuevo", "TEXT / JSON", "Estado posterior a la modificación"],
            ["catalogos.audit_log", "fecha_hora", "TIMESTAMP", "DEFAULT CURRENT_TIMESTAMP. Inalterable"]
        ]
    )

    # ==========================================
    # SECCIÓN 9: ARQUITECTURA DE SOFTWARE Y CÓDIGO FUENTE
    # ==========================================
    add_h1("9. ARQUITECTURA DE SOFTWARE Y CÓDIGO FUENTE")
    add_p(
        "El Sistema Fénix 2.0 utiliza una arquitectura desacoplada de doble portal que separa "
        "las tareas de alta velocidad en campo de las funciones de auditoría contable y dirección en oficina."
    )

    add_h2("9.1 Stack Tecnológico Seleccionado")
    add_bullet("Python 3.12 como lenguaje central, elegido por su robustness, velocidad de procesamiento analítico y ecosistema de datos.", "Lenguaje de Backend: ")
    add_bullet("Flask (micro-framework WSGI) administrando rutas REST API, renderización de plantillas y middlewares de autenticación.", "Framework Web: ")
    add_bullet("HTML5 semántico, CSS3 con diseño 'Aesthetic Glassmorphism' (modo oscuro de alto contraste) y JavaScript puro (Vanilla JS).", "Frontend / UI: ")
    add_bullet("Librería OpenPyXL para lectura y construcción de hojas de cálculo con fórmulas dinámicas y estilos corporativos.", "Generación Excel: ")
    add_bullet("Librería ReportLab para la maquetación de reportes ejecutivos en PDF en formato horizontal landscape con firmas.", "Generación PDF: ")
    add_bullet("Librería pdfplumber para la extracción inteligente de datos tabulares desde archivos PDF de bitácoras de campo.", "Lectura de Documentos: ")

    add_h2("9.2 Módulos y Archivos del Código Fuente Principal")
    add_p("Desglose de los scripts principales que integran el sistema:")

    add_bullet(
        "Servidor de Captura Operativa (Puerto 5001). Contiene 2,484 líneas de código Python. "
        "Maneja los endpoints para la captura de Diésel, Gasolina, Jalisco, Solicitudes y Acarreos. "
        "Incluye los algoritmos de normalización de textos y la interfaz de lectura masiva de Excel.",
        "app_captura.py: "
    )
    add_bullet(
        "Centro de Mando Administrativo (Puerto 5002). Núcleo de control de 12,954 líneas de código. "
        "Gestiona la consolidación de dashboards, el cálculo presupuestal semanal (6D vs 5D), la validación de facturas CFDI/XML, "
        "el módulo de telepeaje Tags, la edición de catálogos maestras y la generación de reportes ejecutivos.",
        "app_admin.py: "
    )
    add_bullet(
        "Servicio de extracción de datos en PDF de bitácoras diarias. Parsea automáticamente columnas de "
        "obra, equipo, litros y kilometraje desde archivos PDF adjuntos, validando duplicados contra la base de datos.",
        "bitacora_pdf_service.py: "
    )
    add_bullet(
        "Motor de conciliación O(1). Carga los consumos registrados y efectúa comparativos masivos "
        "contra los estados de cuenta presentados por los proveedores de combustible (Levet / JDJ / Mobil).",
        "motor_agente_conciliacion.py: "
    )
    add_bullet(
        "Generador especializado de reportes formales en PDF ('Acta de Conciliación Semanal') "
        "con tablas alineadas, cabeceras en color corporativo y secciones de firmas para los auditores.",
        "generador_acta_conciliacion.py: "
    )
    add_bullet(
        "Archivos de procesamiento por lotes para el arranque simultáneo de los servicios en el servidor: "
        "INICIAR_FENIX.bat (Lanzador principal), INICIAR_ADMIN.bat (Portal 5002), INICIAR_CAPTURA.bat (Portal 5001) e INICIAR_N8N.bat (Motor de automatización).",
        "Lanzadores BAT: "
    )

    # ==========================================
    # SECCIÓN 10: MANUAL OPERATIVO PASO A PASO
    # ==========================================
    add_h1("10. MANUAL OPERATIVO Y FUNCIONAMIENTO PASO A PASO")
    add_p(
        "El sistema opera bajo un entorno multimodular accesible mediante navegador web. A continuación se documenta "
        "el funcionamiento paso a paso de cada portal y pestaña."
    )

    add_h2("10.1 Portal de Captura Operativa (`http://localhost:5001`)")

    add_h3("1. Pestaña Diésel (`captura_diesel.html`)")
    add_p("Permite el registro de despachos de diésel entregados por la pipa 'Marimba' o tanques fijos a la maquinaria.")
    add_bullet("El usuario selecciona la fecha, la obra de destino, el equipo económico (ej. EX-01) y los litros despachados.", "Captura Individual: ")
    add_bullet("El usuario arrastra un archivo PDF de bitácora diaria. El sistema invoca `bitacora_pdf_service.py`, lee las filas automáticamente y las muestra en pantalla pre-llenadas para su confirmación inmediata.", "Lectura Inteligente de PDF: ")

    add_h3("2. Pestaña Gasolina (`captura_gasolina.html`)")
    add_bullet("Al ingresar la placa del vehículo, un script en Vanilla JS consulta en memoria el padrón `gasolina.autorizaciones_maestro` y rellena al instante (0ms) el Vehículo, el Conductor y la Obra por defecto.", "Sub-pestaña 1 (Individual con Autocompletado 0ms): ")
    add_bullet("Permite arrastrar archivos Excel mensuales suministrados por gasolinerías (ej. CONTROL JDJ). El sistema separa los registros en semanas ISO (Semana 26 a 31), realiza una búsqueda $O(1)$ de duplicados y marca cada fila como '✔ CONCILIADO' (ya existente) o '🆕 NUEVO' (pendiente). Al hacer clic en 'Guardar Masivo', inserta cientos de registros en lote en menos de 1 segundo.", "Sub-pestaña 2 (Captura Masiva Excel Levet/JDJ): ")

    add_h3("3. Pestañas Jalisco, Solicitudes, Acarreos y Mezcla")
    add_bullet("Captura de vales de combustible y vales de caja para obras en Jalisco con carga de evidencia fotográfica.", "Jalisco: ")
    add_bullet("Formulario de petición de saldo en el cual los ingenieros solicitan volumen semanal antes de surtir.", "Solicitudes: ")
    add_bullet("Registro de viajes de acarreo calculando el cubicaje ($m^3$) según el camión y material transportado.", "Acarreos: ")
    add_bullet("Monitoreo de toneladas de mezcla asfáltica producidas en planta y aplicadas en tramos carreteros.", "Mezcla: ")

    add_h2("10.2 Centro de Mando Administrativo (`http://localhost:5002`)")

    add_h3("1. Pestaña Resumen / Dashboard (`admin_resumen.html`)")
    add_p("Panel ejecutivo que consolida en tiempo real los indicadores clave (KPIs): litros totales consumidos, gasto financiero acumulado, porcentaje de facturación conciliada y desglose por obra.")

    add_h3("2. Pestaña Reporte Semanal por Ingeniero (`admin_diesel.html`)")
    add_p(
        "Genera el reporte normado de consumo presupuestal. El sistema aplica strictly la distinción "
        "de días trabajados según la configuración del catálogo `catalogos.responsables`:"
    )

    add_callout(
        "Fórmula Normada de Presupuesto Semanal (Regla de Días Trabajados)",
        "• SECCIÓN 1: INGENIEROS DE 6 DÍAS (Apolinar, Francisco Javier, Ing. Diego Carreola, Jack, Luis)\n"
        "  Fórmula: Autorización Semanal = Autorizado Diario × 6 Días\n\n"
        "• SECCIÓN 2: INGENIEROS DE 5 DÍAS (Dayanne, Edgar, Samuel)\n"
        "  Fórmula: Autorización Semanal = Autorizado Diario × 5 Días\n\n"
        "El sistema calcula el Consumo Real vs la Autorización Semanal y determina la Variación / Excedente. "
        "Permite exportar el informe oficial en Excel con fórmulas vivas y en PDF horizontal con firmas autorizadas."
    )

    add_h3("3. Pestaña Facturas & Conciliación SAT (`admin_subir_facturas.html`)")
    add_p("Módulo contable para la carga de archivos XML (CFDI 4.0) y PDF de facturas y Complementos de Pago del SAT (ej. Complemento Folio 58914 por $316,944.71 MXN). Actualiza automáticamente el estatus del pago a 'PAGADA', 'PARCIAL' o 'PENDIENTE'.")

    add_h3("4. Pestañas Telepeaje Tags y Catálogos Maestros")
    add_bullet("Conciliación de pases por casetas de cobro asignando el importe exacto a la obra correspondiente.", "Telepeaje Tags: ")
    add_bullet("Gestión del padrón de Responsables (configurando cuotas y días 6D/5D), Obras, Equipos y consulta del log inalterable de auditoría catalogos.audit_log.", "Catálogos Maestros: ")

    add_h2("10.3 Flujo Operativo Completo en 6 Etapas (Del WhatsApp al Martes de Conciliación)")
    add_p("La operación regular de combustible sigue un flujo secuencial normado:")
    add_bullet("El ingeniero o responsable de obra envía su petición en el grupo de WhatsApp o el portal de solicitudes.", "Etapa 1 (Solicitud): ")
    add_bullet("La administración verifica en Fénix que el volumen no exceda la cuota del responsable según sus días trabajados (6D vs 5D).", "Etapa 2 (Validación Presupuestal): ")
    add_bullet("La gasolinería surte al camión cisterna ('La Marimba') y emite la factura CFDI correspondiente.", "Etapa 3 (Surtimiento y Facturación): ")
    add_bullet("La Marimba traslada el diésel a la obra y abastece tanque por tanque a la maquinaria pesada.", "Etapa 4 (Reparto en Obra): ")
    add_bullet("El capturista registra en el Portal 5001 los litros recibidos por cada equipo económico.", "Etapa 5 (Captura en Fénix): ")
    add_bullet("Todos los martes se ejecuta el cruce obligatorio de 3 columnas ('Tríptico de Diésel'): Columna A (Lo Autorizado) vs Columna B (Lo Facturado por Gasolinería) vs Columna C (Lo Repartido y Registrado en Máquinas).", "Etapa 6 (Conciliación del Martes): ")

    # ==========================================
    # SECCIÓN 11: EVOLUCIÓN HISTÓRICA Y VERSIONES
    # ==========================================
    add_h1("11. EVOLUCIÓN HISTÓRICA, VERSIONES Y LOGROS ALCANZADOS")
    add_p(
        "El proyecto ha transitado por dos etapas fundamentales de desarrollo que transformaron "
        "un prototipo inicial en un sistema de clase empresarial."
    )

    style_table(
        doc.add_table(rows=0, cols=3),
        [Inches(1.5), Inches(2.2), Inches(2.8)],
        ["Atributo / Característica", "Versión 1.0 (Prototipo Legacy)", "Versión 2.0 (Producción Actual)"],
        [
            ["Motor de Base de Datos", "Supabase (Cloud) / SQLite estático", "PostgreSQL 16 On-Premise (fenix_db)"],
            ["Velocidad de Captura", "Búsqueda manual en listas desplegables", "Autocompletado instantáneo en 0ms"],
            ["Conciliación con Proveedores", "Revisión manual renglón por renglón", "Motor de conciliación masiva Excel O(1)"],
            ["Regla de Días Trabajados", "Tratamiento homogéneo sin distinción", "División estricta en 6 Días vs 5 Días"],
            ["Lectura de Documentos", "Sin procesamiento de archivos", "Servicio de lectura inteligente de PDF"],
            ["Facturación y SAT", "Manejo básico de facturas simples", "Soporte de CFDI XML y Complementos de Pago"],
            ["Módulos Especiales", "Solo Diésel y Gasolina básica", "Integración de Jalisco, Acarreos, Mezcla y Tags"],
            ["Normatividad y Auditoría", "Sin registro de cambios", "Log inalterable catalogos.audit_log (ISO 9001)"]
        ]
    )

    # ==========================================
    # SECCIÓN 12: PROBLEMAS PRESENTADOS Y SOLUCIONES
    # ==========================================
    add_h1("12. PROBLEMAS PRESENTADOS Y SOLUCIONES DE INGENIERÍA APLICADAS")
    add_p(
        "Durante el diseño, desarrollo y despliegue del Sistema Fénix 2.0 se resolvieron "
        "desafíos complejos de software y datos. A continuación se documenta la matriz de problemas e ingeniería aplicada:"
    )

    style_table(
        doc.add_table(rows=0, cols=3),
        [Inches(1.8), Inches(2.2), Inches(2.5)],
        ["Problema Presentado", "Causa Raíz / Desafío", "Solución de Ingeniería Implementada"],
        [
            [
                "Duplicidad de Cargas de Gasolina",
                "Estados de cuenta mensuales presentaban cargas repetidas o dobles capturas de choferes.",
                "Creación del algoritmo de hashing O(1) en 'motor_agente_conciliacion.py' que compara folios, fechas y montos en tiempo récord, bloqueando duplicados."
            ],
            [
                "Incoherencia en Presupuestos de Ingenieros",
                "Ingenieros con jornadas de 5 días recibían presupuesto de 6 días, generando falsos faltantes.",
                "Parametrización del campo 'dias_trabajados' en 'catalogos.responsables' y reescritura de los generadores de Excel/PDF en 'app_admin.py'."
            ],
            [
                "Dificultad de Lectura en Bitácoras PDF",
                "Formato de PDF escaneado con tablas desalineadas impedía la extracción de datos.",
                "Desarrollo de 'bitacora_pdf_service.py' utilizando 'pdfplumber' y expresiones regulares adaptativas para extraer celdas desalineadas."
            ],
            [
                "Discrepancia en Nombres de Obras y Placas",
                "Capturistas escribían nombres con variaciones (ej. 'Toluca', 'MÉXICO-TOLUCA', 'Obra Toluca').",
                "Implementación de funciones de normalización de cadenas ('normalizar_obra_nombre') en Python y conversión automática a mayúsculas."
            ],
            [
                "Gestión de Complementos de Pago SAT",
                "Facturas liquidadas en varios pagos no reflejaban el saldo real en la contabilidad.",
                "Incorporación de la tabla 'diesel.complementos_pago' y parser XML para vincular UUIDs del SAT y actualizar estatus a 'PAGADA' o 'PARCIAL'."
            ],
            [
                "Lentitud en la Interfaz Web con Miles de Filas",
                "Carga masiva de datos congelaba el navegador en la pestaña de gasolina.",
                "Migración a renderizado eficiente en cliente con Vanilla JS y búsquedas pre-indexadas en memoria."
            ]
        ]
    )

    # ==========================================
    # SECCIÓN 13: ALINEACIÓN NORMATIVA ISO 9001 E ISO 14001
    # ==========================================
    add_h1("13. ALINEACIÓN NORMATIVA ISO 9001 (CALIDAD) E ISO 14001 (AMBIENTAL)")
    add_p(
        "El Sistema Fénix 2.0 constituye la evidencia técnica y documental ante auditores externos "
        "para sostener la certificación de Grupo Trujano en los estándares internacionales de calidad y medio ambiente."
    )

    add_h2("13.1 Puntos de Control para ISO 9001:2015 (Sistema de Gestión de Calidad)")
    add_bullet("Validación matemática en el 'Tríptico de Diésel' asegurando cero diferencias entre lo facturado y lo suministrado.", "Sección 8.4 (Control de Procesos y Servicios Suministrados Externamente): ")
    add_bullet("Trazabilidad total desde el folio de la gasolinería hasta la máquina individual que consumió el insumo.", "Sección 8.5.2 (Identificación y Trazabilidad): ")
    add_bullet("Registro inalterable de auditoría en la tabla 'catalogos.audit_log' que cumple con los requerimientos de información documentada inalterable.", "Sección 7.5 (Información Documentada): ")

    add_h2("13.2 Puntos de Control para ISO 14001:2015 (Sistema de Gestión Ambiental)")
    add_bullet("Monitoreo continuo de trasvases entre tanques fijos, pipas 'Marimba' y maquinaria para detectar mermas o fugas en tuberías/mangueras.", "Sección 8.1 (Planificación y Control Operativo): ")
    add_bullet("Control estricto de cuotas diarias de combustible por obra, promoviendo el consumo eficiente y la reducción de huella de carbono.", "Sección 6.1.2 (Aspectos Ambientales): ")

    # Save document with fallback for open file lock
    output_path = r"c:\Users\JOSE\Desktop\Proyecto fenix\Documento_Tecnico_y_Operativo_Sistema_Fenix_2_0_Actualizado.docx"
    try:
        doc.save(output_path)
        print(f"Document generated successfully at: {output_path}")
    except PermissionError:
        output_path_alt = r"c:\Users\JOSE\Desktop\Proyecto fenix\Documento_Tecnico_y_Operativo_Sistema_Fenix_v2_Completo.docx"
        doc.save(output_path_alt)
        print(f"Document generated successfully at: {output_path_alt}")

if __name__ == "__main__":
    create_fenix_documentation()
