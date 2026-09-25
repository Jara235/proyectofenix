# 📜 BITÁCORA DE CONVERSACIONES, DECISIONES TÉCNICAS Y EVOLUCIÓN HISTÓRICA — SISTEMA FÉNIX 2.0

> **Documento Oficial de Registro de Decisiones de Arquitectura de Software, Migración de Base de Datos y Automatizaciones.**

---

## 1. Cronología de Desarrollo y Decisiones de Arquitectura

### 📍 Fase 1: Transición de Fénix 1.0 (Legacy) a Fénix 2.0
- **Diagnóstico:** Fénix 1.0 operaba como prototipo en Supabase / SQLite con listas desplegables lentas y sin validación estricta de días trabajados.
- **Decisión:** Migración a **PostgreSQL 16 On-Premise (`fenix_db`)** para garantizar soberanía de datos, tiempo de respuesta < 50ms y soporte de Triggers de base de datos para bloqueo de información.
- **Modelado de Esquemas:** Separación de la base de datos en esquemas lógicos: `catalogos`, `diesel`, `gasolina`, `acarreos`, `mezcla`, `tags`, `usuarios`, `transportes`, `n8n`.

---

### 📍 Fase 2: Regla Normada Presupuestal de Días Trabajados (6D vs 5D)
- **Problemática:** Los presupuestos semanales de combustible se calculaban multiplicando por 6 días para todos los ingenieros indiscriminadamente, generando falsos sobrecostos.
- **Decisión:** Implementación de la distinción estricta en la tabla `catalogos.responsables`:
  - **Ingenieros de 6 Días:** Apolinar, Francisco Javier, Ing. Diego Carreola, Jack, Luis ($\text{Presupuesto Semanal} = \text{Cuota Diaria} \times 6$).
  - **Ingenieros de 5 Días:** Dayanne, Edgar, Samuel ($\text{Presupuesto Semanal} = \text{Cuota Diaria} \times 5$).
- **Impacto:** Eliminación inmediata del desvío presupuestal en reportes semanales.

---

### 📍 Fase 3: Optimización Algorítmica de Captura y Conciliación Masiva
- **Problemática:** La revisión de los reportes mensuales de gasolinerías (ej. Gasolinera Levet y JDJ) tomaba días de trabajo manual renglón por renglón.
- **Decisión:**
  - Desarrollo en `app_captura.py` de la búsqueda $O(1)$ mediante diccionarios y hash sets en memoria.
  - Implementación de la función de separación de Semanas ISO (Semanas 26 a 37).
  - Resultado: Procesamiento de más de 1,200 registros de cargas masivas en **menos de 1 segundo**.

---

### 📍 Fase 4: Integración del Motor de Automatización n8n e IA Multimodal
- **Decisión de Arquitectura:** Desplegar un servidor **n8n** local (`http://localhost:5678`) integrado con el modelo **Google Gemini 1.5 Flash**.
- **Flujos Construidos:**
  1. **Ingestión Email IMAP -> Google Drive -> PostgreSQL:** Captura automática de facturas CFDI XML 4.0 de *Derivados de Petróleo Castilla*, guardado en carpetas semanales en Drive y notificación Webhook al Portal Admin (5002) para asignación de obra en 1-clic.
  2. **Motor de Conciliación en Vivo:** Webhook REST que compara litros facturados vs litros consumidos en maquinaria, emitiendo un **Semáforo de Control (🟢 Exacto, 🟡 Saldo Pipa, 🔴 Merma/Exceso)**.
  3. **Agente IA WhatsApp Gemini 1.5 Flash:** Lectura automática de fotos de tickets y texto enviadas por choferes al grupo de WhatsApp.

---

### 📍 Fase 5: Gobierno Corporativo y Bloqueo Inquebrantable de Datos
- **Decisión:** Implementación de Triggers en PostgreSQL sobre `diesel.consumos` y `gasolina.consumos`.
- **Mecanismo:** Cuando un periodo es auditado y cerrado (`periodo_bloqueado = TRUE`), PostgreSQL rechaza cualquier sentencia `UPDATE`, `INSERT` o `DELETE`, garantizando la auditoría bajo estándares **ISO 9001:2015**.

---

## 2. Registro de Incidencias Técnicas Resueltas

| Incidencia Detectada | Causa Raíz Identificada | Solución de Ingeniería Aplicada |
| :--- | :--- | :--- |
| **Error `PermissionError: [Errno 13]` al generar el Word** | El archivo `.docx` estaba abierto en Microsoft Word en Windows, bloqueando el reescrito del archivo en disco. | Implementación de un bloque `try/except` en `generar_documento_word.py` que genera automáticamente un archivo alternativo de salida (ej. `_Homologacion.docx`). |
| **Incoherencia en nombres de Obras al conciliar** | Capturistas en campo escribían nombres como *"Toluca"*, *"Bacheo Toluca"* o *"Obra Toluca"*. | Implementación de la función `normalizar_obra_nombre` que mapea cadenas de texto a la clave primaria inmutable `codigo` de la obra (PK/FK). |
| **Advertencia de archivo grande en GitHub (>50MB)** | La base de datos o archivos pesados binarios intentaron subirse directamente. | Configuración estricta del archivo `.gitignore` y exportación de la base de datos a scripts de volcado de texto SQL (`database/fenix_postgres_full.sql`). |
