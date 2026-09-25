# 🦅 SISTEMA FÉNIX 2.0 — Plataforma Integral de Control Operativo, Automatización e Inteligencia Financiera

> **Grupo Trujano** — Sistema Empresarial de Auditoría y Conciliación Multinivel de Combustible, Acarreos, Mezcla Asfáltica, Telepeaje Tags y Control Presupuestal con Integración de Inteligencia Artificial (Google Gemini 1.5 Flash) y Motor de Automatización n8n.

---

## 📋 Tabla de Contenidos
- [1. Visión General y Propósito del Sistema](#1-visión-general-y-propósito-del-sistema)
- [2. Arquitectura de Software y Portales](#2-arquitectura-de-software-y-portales)
- [3. Motor de Automatizaciones n8n e Inteligencia Artificial](#3-motor-de-automatizaciones-n8n-e-inteligencia-artificial)
- [4. Modelo de Conciliación Multinivel de 2 Vías y Gobierno Corporativo](#4-modelo-de-conciliación-multinivel-de-2-vías-y-gobierno-corporativo)
- [5. Estructura y Respaldo de la Base de Datos (`fenix_db`)](#5-estructura-y-respaldo-de-la-base-de-datos-fenix_db)
- [6. Matriz de Roles y Seguridad RBAC](#6-matriz-de-roles-y-seguridad-rbac)
- [7. Guía de Instalación, Inicio y Sincronización](#7-guía-de-instalación-inicio-y-sincronización)
- [8. Mapa del Repositorio y Documentación Incluida](#8-mapa-del-repositorio-y-documentación-incluida)
- [9. Alineación Normativa e Hitos del Proyecto](#9-alineación-normativa-e-hitos-del-proyecto)

---

## 1. Visión General y Propósito del Sistema

El **Sistema Fénix 2.0** fue desarrollado para erradicar las ineficiencias, opacidades y mermas en el suministro y consumo de combustible (diésel y gasolina), movimiento de acarreos, recepción de mezcla asfáltica y control de casetas de telepeaje Tags en los diferentes frentes de obra de **Grupo Trujano**.

### ¿Por qué y Para qué se creó Fénix?
- **Auditoría Financiera al Centavo:** Garantiza la coincidencia exacta entre lo autorizado, lo facturado por la estación de servicio y lo recibido en tanques/maquinaria.
- **Trazabilidad Inalterable:** Otorga folios únicos, sellos de tiempo, firma de usuario y registro de cambios para cada litro.
- **Cero Tolerancia a Mermas Indebidas:** Detecta transferencias no explicadas entre gasolinerías, pipas cisterna ("Marimbas"), tanques fijos ("Pegaso") y maquinaria de obra.
- **Eficiencia en Campo:** Autocompletado de vehículos y obras en 0ms y lectura inteligente de bitácoras en PDF.

---

## 2. Arquitectura de Software y Portales

El sistema opera bajo un esquema de **Doble Portal Independiente** para optimizar la velocidad en campo y la seguridad administrativa:

```text
 ┌────────────────────────────────────────────────────────────────────────┐
 │                         ESTRUCTURA DE PORTALES FÉNIX                    │
 ├───────────────────────────────────┬────────────────────────────────────┤
 │  PORTAL DE CAPTURA OPERATIVA      │  CENTRO DE MANDO ADMINISTRATIVO    │
 │  Puerto: 5001 (`app_captura.py`)  │  Puerto: 5002 (`app_admin.py`)     │
 ├───────────────────────────────────┼────────────────────────────────────┤
 │ • Alta instantánea de cargas      │ • Dashboard de KPIs en vivo        │
 │ • Autocompletado en 0ms           │ • Aplicación de regla 6D vs 5D     │
 │ • Servicio OCR / PDF Bitácoras    │ • Conciliación de facturas SAT     │
 │ • Carga masiva de Excel O(1)      │ • Bloqueo de periodos congelados   │
 └───────────────────────────────────┴────────────────────────────────────┘
```

---

## 3. Motor de Automatizaciones n8n e Inteligencia Artificial

Fénix integra un servidor **n8n** (`http://localhost:5678`) con **Google Gemini 1.5 Flash** para procesar información sin intervención humana manual:

```text
 ┌────────────────────────────────────────────────────────────────────────┐
 │                         FUENTES EXTERNAS DE DATOS                       │
 │   [Correo IMAP Castilla]     [WhatsApp Meta API]      [Google Drive]   │
 └───────────────────┬──────────────────────┬────────────────────┬────────┘
                     │                      │                    │
                     ▼                      ▼                    ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │                      SERVIDOR DE AUTOMATIZACIÓN n8n                    │
 │                                                                        │
 │  ┌────────────────────────┐  ┌──────────────────────────────────────┐  │
 │  │ Flujo 01: Ingestión    │  │ Flujo 03: Agente IA Gemini 1.5 Flash │  │
 │  │ Facturas IMAP/Drive    │  │ (Clasifica WhatsApp y Fotos Tickets) │  │
 │  └───────────┬────────────┘  └──────────────────┬───────────────────┘  │
 │              │                                  │                      │
 │              ▼                                  ▼                      │
 │  ┌──────────────────────────────────────────────────────────────────┐  │
 │  │ Flujo 02: Motor de Conciliación y Semáforo en Tiempo Real        │  │
 │  │ (🟢 Exacto | 🟡 Saldo Pipa | 🔴 Merma/Exceso)                   │  │
 │  └───────────┬──────────────────────────────────────────────────────┘  │
 └──────────────┼─────────────────────────────────────────────────────────┘
                │
                ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │                   POSTGRESQL (fenix_db) & ADMIN 5002                   │
 │             [Notificación a Fénix Admin para Asignación 1-Clic]        │
 └────────────────────────────────────────────────────────────────────────┘
```

1. **Flujo 01 (`01_ingestion_email_drive_facturas_diesel.json`):** Monitorea correos IMAP de proveedores (ej. *Derivados de Petróleo Castilla*), descarga adjuntos XML CFDI 4.0/PDF a **Google Drive** por semana, e inserta en PostgreSQL para asignación en 1-clic.
2. **Flujo 02 (`02_conciliacion_diesel_factura_vs_cargas.json`):** Webhook REST para comparación automática de volúmenes facturados vs entregados en obra, generando un **Semáforo de Control (🟢🟡🔴)**.
3. **Flujo 03 (WhatsApp & Gemini 1.5 Flash AI):** Recibe imágenes de tickets y textos por WhatsApp, clasifica la transacción con inteligencia artificial e inserta la carga en la base de datos.

---

## 4. Modelo de Conciliación Multinivel de 2 Vías y Gobierno Corporativo

Cada litro de combustible y metro cúbico de material debe declararse de forma independiente por el **Emisor** y el **Receptor**:

1. **Nivel 1 (Distribuidor vs Pipa/Tanque):** Factura del proveedor vs Entrada registrada en Pipa Marimba / Tanque Pegaso.
2. **Nivel 2 (Pipa/Tanque vs Maquinaria de Obra):** Despacho en pipa vs Cargas individuales capturadas por el Ingeniero de Obra (con foto obligatoria).
3. **Nivel 3 (Auditoría Fiscal):** Cargas acumuladas vs Archivos XML CFDI y Complementos de Pago del SAT (ej. Complemento Folio 58914 por $316,944.71 MXN).
4. **Nivel 4 (Gobierno Corporativo y Bloqueo):** Congelamiento definitivo del periodo mediante **Triggers de PostgreSQL** que rechazan cualquier modificación retroactiva.

---

## 5. Estructura y Respaldo de la Base de Datos (`fenix_db`)

El sistema utiliza **PostgreSQL 16** (`fenix_db`) con esquemas altamente normalizados. Todos los dumps completos de la base de datos se encuentran empaquetados en la carpeta `database/`:

- 🐘 **`database/fenix_postgres_full.sql`**: Dump SQL completo de PostgreSQL (185 tablas, esquemas `diesel`, `gasolina`, `catalogos`, `acarreos`, `mezcla`, `tags`, `usuarios`, `transportes`, `n8n` y registros de semillas).
- 📁 **`database/dump_fenix_v2.db.sql`**: Dump SQL de respaldo en formato SQLite.
- 📜 **`database/exportar_base_datos_completa.py`**: Script automatizado para regenerar los respaldos SQL.

---

## 6. Matriz de Roles y Seguridad RBAC

| Nivel de Acceso | Rol de Usuario | Permisos Operativos | Alcance de Edición / Bloqueo |
| :--- | :--- | :--- | :--- |
| **Nivel 1: Básico** | Operadores / Choferes | Captura de cargas con Horómetro y Foto obligatoria. | INSERT solo en registros propios del día. |
| **Nivel 2: Operativo** | Operadores de Pipa / Tanque | Entradas de combustible y despachos a obras. | INSERT y UPDATE limitado al día corriente. |
| **Nivel 3: Supervisión** | Ingenieros de Obra | Presupuestos 6D/5D, autorizaciones extra, reportes de obra, acarreos y mezclas. | INSERT y SELECT en obras asignadas antes del cierre. |
| **Nivel 4: Ejecutivo** | Admins / Directivos | Conciliación masiva, edición de catálogos, **CIERRE Y BLOQUEO DE PERIODOS**. | FULL ACCESS (SELECT, INSERT, UPDATE, DELETE, LOCK). |

---

## 7. Guía de Instalación, Inicio y Sincronización

### Prerrequisitos
- Python 3.10+
- PostgreSQL 16
- Node.js & n8n (opcional para automatizaciones)

### Pasos de Inicio
1. **Clonar el repositorio:**
   ```powershell
   git clone https://github.com/Jara235/proyectofenix.git
   cd proyectofenix
   ```
2. **Restaurar la Base de Datos PostgreSQL:**
   ```powershell
   psql -U postgres -d fenix_db -f database/fenix_postgres_full.sql
   ```
3. **Iniciar los Servicios (Ejecutables en 1-clic):**
   - 🚀 **`INICIAR_FENIX.bat`**: Arranca ambos portales (Puerto 5001 y Puerto 5002) en simultáneo.
   - 🤖 **`INICIAR_N8N.bat`**: Inicia el servidor n8n local.
   - 💾 **`GUARDAR_Y_SUBIR_GIT.bat`**: Guarda, crea commit con estampa de tiempo y sube todo a GitHub con 1-clic.

---

## 8. Mapa del Repositorio y Documentación Incluida

```text
Proyecto fenix/
├── 📄 README.md                                   <- Presentación Ejecutiva Principal
├── 📄 GUARDAR_Y_SUBIR_GIT.bat                     <- Script de Respaldo y Sync GitHub
├── 📄 INICIAR_FENIX.bat                           <- Lanzador de Portales 5001 y 5002
├── 📄 Documento_Tecnico_y_Operativo_Sistema_Fenix_v2_Completo.docx <- Documento Maestro en Word
├── 📁 database/                                   <- Dumps SQL de la Base de Datos
│   ├── fenix_postgres_full.sql                   <- Backup Completo PostgreSQL 185 tablas
│   ├── dump_fenix_v2.db.sql                      <- Backup SQLite
│   └── exportar_base_datos_completa.py            <- Script de Regeneración
├── 📁 documentacion/                              <- Guías Técnicas y Normativas
│   ├── GUIA_PREPARACION_JUNTA_Y_PREGUNTAS.md      <- Respuestas y Cuestionario Estratégico
│   ├── HISTORIAL_CONVERSACIONES_Y_DECISIONES.md   <- Bitácora Técnica de Decisiones
│   └── documento_procedimiento_sistema_fenix_iso.md <- Alineación ISO 9001/14001
├── 📁 n8n/                                        <- Workflows de Automatización e IA
│   └── workflows/                                 <- Flujos JSON de IMAP, Drive y Gemini
├── 📄 app_admin.py                                <- Backend Portal Administrativo (5002)
├── 📄 app_captura.py                              <- Backend Portal Operativo (5001)
└── 📄 bitacora_pdf_service.py                     <- Servicio OCR / Lectura de PDF
```

---

## 9. Alineación Normativa e Hitos del Proyecto

- **ISO 9001:2015 (Gestión de la Calidad):** Control estricto de proveedores, trazabilidad inalterable en `catalogos.audit_log` y procedimientos estandarizados de conciliación.
- **ISO 14001:2015 (Gestión Ambiental):** Balance de masa de hidrocarburos, detección temprana de fugas y monitoreo de emisiones por consumo por hora/km.

---
*Desarrollado con excelencia técnica por la Dirección de Tecnología y Operaciones de Grupo Trujano.*
