# 📘 GUÍA DE PUESTA EN MARCHA: AUTOMATIZACIONES EN n8n PARA DIÉSEL FÉNIX

Esta guía explica cómo importar, configurar y activar los dos flujos de trabajo de n8n para la ingestión de facturas por correo de **DERIVADOS DE PETROLEO CASTILLA** y la conciliación automática contra las cargas de obra en el **Sistema Fénix 2.0**.

---

## 📧 Configuración Específica del Proveedor de Combustible

El flujo está preconfigurado para filtrar y procesar automáticamente los correos con las siguientes características:

* **Remitente:** `DERIVADOS DE PETROLEO CASTILLA <facturaciondpc2@gmail.com>`
* **RFC Emisor:** `DPC180725R47`
* **Patrón de Asunto:** `Ha recibido un CFDI (FACTURA) para J.D.J. EQUIPO Y CONSTRUCCIONES`
* **Adjuntos:** XML del CFDI 4.0 / 3.3 y PDF de la Factura (ej. `DPC180725R47_C...`).

---

## 📂 Archivos de Flujos Disponibles

1. **`01_ingestion_email_drive_facturas_diesel.json`**:
   - Monitorea la bandeja de correo filtrando exclusivamente remitentes como `facturaciondpc2@gmail.com` y asuntos de CFDI.
   - Descarga y respalda automáticamente los PDFs y XMLs en Google Drive organizados por semana (`SEM_{X}_factura.pdf`).
   - Lee el XML CFDI y extrae Serie, Folio, Litros, Precio Unitario, Subtotal, IVA, UUID e Importe Total.
   - Registra la factura en PostgreSQL (`diesel.facturas`) con estatus `PENDIENTE_OBRA`.
   - Notifica al **Centro de Mando / Administración Fénix (Puerto 5002)** para la **Asignación Humana de Obra Destino** en 1-clic.

2. **`02_conciliacion_diesel_factura_vs_cargas.json`**:
   - Webhook endpoint: `POST /webhook/fenix-conciliacion-diesel`
   - Realiza la suma de facturas vs la suma de cargas de obra en campo.
   - Audita el cumplimiento de fotos de evidencia (cuenta litros de marimba, manguera a máquina, horómetro del operador).
   - Devuelve el balance y semáforo en tiempo real (🟢 Exacto, 🟡 Saldo en Tanque, 🔴 Merma/Exceso).

---

## ⚙️ Pasos para Configurar en tu Instancia de n8n

### Paso 1: Importar los Flujos en n8n
1. Abre tu panel de n8n (ej. `http://localhost:5678` o tu instancia en Railway/Docker/Cloud).
2. Haz clic en **Workflows** > **Add Workflow** (o el menú de los 3 puntos `...` arriba a la derecha).
3. Selecciona **Import from File** y elige:
   - `n8n/workflows/01_ingestion_email_drive_facturas_diesel.json`
   - `n8n/workflows/02_conciliacion_diesel_factura_vs_cargas.json`

---

### Paso 2: Configurar Credenciales en n8n

#### A. Credencial de Correo (IMAP / Gmail):
- En el nodo **Trigger: Correo Facturas Diésel (Castilla)**, selecciona o crea una nueva credencial **IMAP Email**:
  - **Host**: `imap.gmail.com`
  - **Puerto**: `993` (SSL/TLS activo)
  - **Usuario**: Tu correo receptor (donde te llegan los correos de `facturaciondpc2@gmail.com`)
  - **Contraseña**: Tu contraseña de aplicación (App Password de 16 caracteres de Google)
  - **Filtro configurado:** `FROM facturaciondpc2@gmail.com`

#### B. Credencial de Google Drive (OAuth2):
- En el nodo **Google Drive: Guardar PDF en Carpeta Diésel**:
  - Conecta tu cuenta de Google Drive empresarial.
  - Coloca el ID de la carpeta destino de Drive en el campo `parents`.

#### C. Credencial de Base de Datos PostgreSQL:
- En los nodos de **Postgres**:
  - **Host**: `localhost` (o IP/URL del servidor Postgres)
  - **Database**: `fenix_db`
  - **User**: `postgres`
  - **Port**: `5432`

---

### Paso 3: Conexión con el Módulo de Administración Fénix
- El webhook notificador del Flujo 01 envía los eventos directamente a:
  `http://localhost:5002/api/admin/diesel/webhook_nueva_factura`
- Tan pronto entra la factura, aparece instantáneamente en el **Módulo de Administración** (`http://localhost:5002/admin/diesel`) dentro del tab **`🧾 Facturas`** en la barra superior de **Aprobación de Obra**.

---

## 🎯 Ciclo Operativo de Conciliación

```
1. DERIVADOS DE PETROLEO CASTILLA (facturaciondpc2@gmail.com) envía correo con CFDI
                                       │
                                       ▼
2. n8n detecta el correo, descarga PDF/XML, respalda en Drive e inserta en Postgres
                                       │
                                       ▼
3. En el Módulo de Administración (Puerto 5002):
   El Auditor visualiza la factura y con 1-clic selecciona la OBRA DESTINO
                                       │
                                       ▼
4. n8n / Fénix calcula en vivo el balance:
   Litros Facturados (Castilla) VS Suma de Cargas en Obra (Marimba / Operadores)
                                       │
                                       ▼
5. Semáforo en Vivo: 🟢 CONCILIADO | 🟡 SALDO EN TANQUE/PIPA | 🔴 MERMA / EXCESO
```
