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
    add_title("DOCUMENTACIÓN TÉCNICA, AUTOMATIZACIÓN n8n Y GUÍA DE HOMOLOGACIÓN: SISTEMA FÉNIX 2.0")
    add_subtitle("Manual de Arquitectura de Software, Motor de Automatizaciones n8n con IA (Gemini 1.5 Flash), Sistema de Conciliación de 2 Vías, Matriz RBAC, Plan de Trabajo con Metas y Guía Estratégica para Junta Técnica")

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
            ["Guía de Homologación", "Respuestas Preparadas para la Junta e Interrogatorio Estratégico"],
            ["Alcance Normativo", "Certificación ISO 9001:2015 (Calidad) e ISO 14001:2015 (Ambiental)"]
        ]
    )

    add_callout(
        "Directiva de Documentación Profesional Exhaustiva",
        "El presente documento técnico integra la arquitectura completa del Sistema Fénix 2.0: "
        "desde la justificación estratégica, la matriz de permisos RBAC y el modelo de conciliación de 2 vías, "
        "hasta el desglose detallado del Motor de Automatizaciones en n8n, el Plan de Trabajo con Metas "
        "y la **Guía Preparatoria para la Junta de Homologación con el Equipo de Ingeniería**."
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

    # ==========================================
    # SECCIÓN 14: GUÍA Y PREPARACIÓN PARA JUNTA DE HOMOLOGACIÓN
    # ==========================================
    add_h1("14. GUÍA PREPARATORIA PARA JUNTA DE HOMOLOGACIÓN Y CUESTIONARIO ESTRATÉGICO")
    add_p(
        "Esta sección consolida las respuestas técnicas para la junta con el equipo de ingeniería "
        "y el cuestionario estructurado para evaluar el sistema existente del otro equipo."
    )

    add_h2("14.1 Respuestas Preparadas para la Junta")
    
    add_h3("1. Disponibilidad de Tiempo y Horarios")
    add_bullet("Lunes a partir de las 2:00 PM.", "Días Disponibles: ")
    add_bullet("Jueves y Viernes en jornada flexible.", "Días Completos: ")
    add_bullet("15 a 20 horas de dedicación enfocada por semana.", "Carga Semanal: ")

    add_h3("2. Guion de la Demostración en Vivo de Fénix")
    add_bullet("Mostrar Portal Operativo 5001 y Centro de Mando Admin 5002.", "Paso A: Doble Portal: ")
    add_bullet("Demostrar autocompletado en 0ms por placa y extracción automática desde bitácoras PDF.", "Paso B: Captura Rápida: ")
    add_bullet("Explicar cómo n8n recibe el correo de la gasolinería, descarga PDF/XML a Google Drive e inserta en la BD.", "Paso C: Módulo Google Drive + n8n: ")
    add_bullet("Mostrar la sub-pestaña de gasolina masiva cargando el Excel 'CONTROL JDJ' con separación de semanas ISO y búsqueda O(1).", "Paso D: Vaciado Masivo Excel: ")
    add_bullet("Generación del informe en Excel con fórmulas vivas y PDF horizontal con firmas.", "Paso E: Reportes Oficiales: ")

    add_h3("3. Homologación Metodológica de Desarrollo")
    add_bullet("El proyecto se gestiona con Git en la rama `main`. Ante un fallo, se ejecuta `git checkout` o `git revert` para restaurar el código. La BD cuenta con transacciones ACID y backups diarios en `respaldos_backups`.", "Control de Versiones y Rollbacks: ")
    add_bullet("Verificación en 3 niveles: 1) Análisis sintáctico en Python, 2) Inspección de logs HTTP y consola de Flask en tiempo real, 3) Pruebas SQL y revisión de archivos Excel/PDF al centavo.", "Validación de Resultados: ")
    add_bullet("Las cargas se vinculan mediante el código inmutable de la obra (`codigo` PK / FK). Si se cambia el nombre visible, el historial permanece intacto.", "Relación de Obras e Historial: ")
    add_bullet("El cierre está protegido **directamente en PostgreSQL mediante Triggers (disparadores SQL)** que cancelan cualquier `UPDATE/DELETE` en periodos congelados (`periodo_bloqueado = TRUE`), además del bloqueo visual en pantalla.", "Cierre y Bloqueo de Datos: ")

    add_h2("14.2 Cuestionario Estratégico para Evaluar el Sistema del Otro Equipo")
    add_p("Preguntas clave organizadas por dominio técnico para dirigir la junta de homologación:")

    style_table(
        doc.add_table(rows=0, cols=3),
        [Inches(1.8), Inches(2.2), Inches(2.5)],
        ["Categoría / Dominio", "Pregunta Estratégica Sugerida", "Propósito / Objetivo de la Pregunta"],
        [
            [
                "1. Arquitectura y Stack",
                "¿En qué stack tecnológico está construido su sistema y qué motor de base de datos utilizan (PostgreSQL, MySQL, SQL Server, Oracle)? ¿Está en la nube u On-Premise?",
                "Determinar la facilidad de comunicación técnica e infraestructura compartida."
            ],
            [
                "2. Estandarización de Catálogos",
                "¿Cómo gestionan los catálogos maestros de Obras y Equipos? ¿Manejan un código único o clave corta para cada máquina?",
                "Identificar la necesidad de crear una tabla puente para que ambos sistemas hablen el mismo idioma."
            ],
            [
                "3. Modelo de Conciliación",
                "En la parte de combustible y acarreos, ¿cómo realizan el cruce de información? ¿Hacen conciliación de 2 o 3 vías (Factura vs Pipa vs Maquinaria)?",
                "Evaluar el nivel de rigor en auditoría de mermas y trasvases en campo."
            ],
            [
                "4. Automatización e Ingestión",
                "¿Cómo ingresan las facturas de proveedores? ¿Tienen algún proceso automatizado para procesar XML/PDF o se capturan manualmente?",
                "Destacar el valor del Motor n8n e IA Gemini 1.5 Flash de Fénix que automatiza este proceso."
            ],
            [
                "5. Conexión y APIs",
                "¿Su sistema cuenta con servicios web, REST APIs expuestas o Webhooks? ¿Se conecta con algún ERP contable (CONTPAQi, SAP, COI)?",
                "Definir el mecanismo de integración de datos sin necesidad de intercambiar archivos Excel manuales."
            ],
            [
                "6. Cierre y Gobierno de Datos",
                "¿Cómo manejan el cierre contable semanal/mensual? ¿El sistema de ustedes bloquea registros pasados para evitar modificaciones?",
                "Alinear los estándares de seguridad y auditoría ISO 9001."
            ],
            [
                "7. Estrategia de Coexistencia",
                "Viendo que ambos sistemas tienen fortalezas, ¿cuál ven como el flujo ideal? ¿Ven a Fénix como el módulo especializado de campo que envíe datos validados a su sistema central?",
                "Posicionar a Fénix como el especialista operativo sin entrar en conflicto con el sistema de ellos."
            ]
        ]
    )

    # Save document with fallback for open file lock
    output_path = r"c:\Users\JOSE\Desktop\Proyecto fenix\Documento_Tecnico_y_Operativo_Sistema_Fenix_v2_Completo.docx"
    try:
        doc.save(output_path)
        print(f"Document generated successfully at: {output_path}")
    except PermissionError:
        output_path_alt = r"c:\Users\JOSE\Desktop\Proyecto fenix\Documento_Tecnico_y_Operativo_Sistema_Fenix_v2_Homologacion.docx"
        doc.save(output_path_alt)
        print(f"Document generated successfully at: {output_path_alt}")

if __name__ == "__main__":
    create_fenix_documentation()
