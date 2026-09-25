# 🎯 GUÍA DE PREPARACIÓN PARA JUNTA TÉCNICA Y CUESTIONARIO ESTRATÉGICO

---

## 1. Respuestas Preparadas para la Junta

### 1.1 Disponibilidad y Horarios
- **Lunes:** A partir de las **2:00 PM**.
- **Jueves:** Jornada disponible / flexible.
- **Viernes:** Jornada disponible / flexible.
- **Carga Semanal:** **15 a 20 horas semanales** de dedicación enfocada en desarrollo, mantenimiento, soporte e integración de Fénix.

---

### 1.2 Guion de la Demostración en Vivo (Demo de 5 a 10 Minutos)

1. **Paso 1: Explicación de la Arquitectura de Doble Portal**
   - **Portal 5001 (Operativo):** Para choferes, operadores y capturistas en obra.
   - **Portal 5002 (Administrativo):** Para contadores, auditores y directivos.
2. **Paso 2: Captura en Vivo con Autocompletado (0ms) y Lectura de PDF**
   - Muestra la captura de Gasolina ingresando una placa y viendo cómo autocompleta en 0ms.
   - Muestra la subida de un PDF de bitácora en la pestaña Diésel y la extracción automática.
3. **Paso 3: Módulo de Google Drive e Ingestión n8n**
   - Muestra cómo n8n recibe el correo de la gasolinería (XML CFDI + PDF), lo guarda automáticamente en la carpeta correspondiente de Google Drive por semana (`SEM_{X}_factura.pdf`) e inserta la factura en PostgreSQL.
   - Muestra la notificación en el Portal 5002 para la asignación de obra con 1-clic.
4. **Paso 4: Vaciado Masivo de Excel (Algoritmo $O(1)$)**
   - Carga el Excel de la gasolinería (`CONTROL JDJ PROVISIONAL.xlsx`), mostrando la separación por semanas ISO y el vaciado masivo en menos de 1 segundo.
5. **Paso 5: Generación del Reporte Oficial en Excel y PDF**
   - Genera el reporte semanal aplicando la **regla normada de 6 Días vs 5 Días**, exportando en Excel (fórmulas vivas) y PDF (landscape con firmas).

---

### 1.3 Homologación Metodológica de Desarrollo

- **Control de Versiones y Rollbacks:**
  - El proyecto se gestiona mediante **Git** en la rama `main` con respaldos en `codigo_fuente_y_versiones`.
  - Ante un problema, se ejecuta `git checkout` o `git revert` para restaurar el código.
  - La base de datos opera bajo transacciones SQL (ACID) y respaldos periódicos en `database/` (`fenix_postgres_full.sql`).

- **Metodología de Validación Empírica en 3 Niveles:**
  1. *Sintaxis y Compilación:* Verificación estática en Python.
  2. *Logs de Servidor en Tiempo Real:* Monitoreo de la consola de Flask (puertos 5001/5002) para capturar tracebacks o errores HTTP.
  3. *Verificación de Salidas:* Ejecución de pruebas SQL que verifican que los montos matemáticos en Excel/PDF cuadren al centavo.

- **Relación de Obras e Historial:**
  - En la base de datos cada obra posee un **`codigo` inmutable (Primary Key / Foreign Key)** (ej. `BT`, `L3M`, `MT`).
  - Si se actualiza el nombre visible de la obra, el historial de consumos permanece seguro e intacto.
  - El backend cuenta con un normalizador de texto (`normalizar_obra_nombre`) que convierte variaciones de texto al código oficial.

- **Cierre y Bloqueo de Periodo:**
  - El bloqueo está protegido **directamente en PostgreSQL mediante Triggers (disparadores SQL)**. Al cerrar un periodo (`periodo_bloqueado = TRUE`), la base de datos rechaza cualquier `UPDATE`, `INSERT` o `DELETE`.
  - La interfaz gráfica inhabilita los botones de edición y muestra un candado 🔒.
  - Solo un **Superadministrador** puede reabrir un periodo dejando registro en `catalogos.audit_log`.

---

## 2. Cuestionario Estratégico para Evaluar el Sistema del Otro Equipo

| Categoría | Pregunta Estratégica | Propósito de la Pregunta |
| :--- | :--- | :--- |
| **1. Arquitectura y Stack** | ¿En qué stack tecnológico está construido su sistema y qué motor de base de datos utilizan (PostgreSQL, MySQL, SQL Server, Oracle)? ¿Está en la nube u On-Premise? | Determinar la facilidad de comunicación técnica e infraestructura compartida. |
| **2. Catálogos Maestros** | ¿Cómo gestionan los catálogos maestros de Obras y Equipos? ¿Manejan un código único o clave corta para cada máquina? | Identificar la necesidad de crear una tabla puente para que ambos sistemas hablen el mismo idioma. |
| **3. Modelo de Conciliación** | En la parte de combustible y acarreos, ¿cómo realizan el cruce de información? ¿Hacen conciliación de 2 o 3 vías (Factura vs Pipa vs Maquinaria)? | Evaluar el nivel de rigor en auditoría de mermas y trasvases en campo. |
| **4. Automatización e Ingestión** | ¿Cómo ingresan las facturas de proveedores? ¿Tienen algún proceso automatizado para procesar XML/PDF o se capturan manualmente? | Destacar el valor del Motor n8n e IA Gemini 1.5 Flash de Fénix que automatiza este proceso. |
| **5. Conexión y APIs** | ¿Su sistema cuenta con servicios web, REST APIs expuestas o Webhooks? ¿Se conecta con algún ERP contable (CONTPAQi, SAP, COI)? | Definir el mecanismo de integración de datos sin necesidad de intercambiar archivos Excel manuales. |
| **6. Cierre y Gobierno de Datos** | ¿Cómo manejan el cierre contable semanal/mensual? ¿El sistema de ustedes bloquea registros pasados para evitar modificaciones? | Alinear los estándares de seguridad y auditoría ISO 9001. |
| **7. Estrategia de Coexistencia** | Viendo que ambos sistemas tienen fortalezas, ¿cuál ven como el flujo ideal? ¿Ven a Fénix como el módulo especializado de campo que envíe datos validados a su sistema central? | Posicionar a Fénix como el especialista operativo sin entrar en conflicto con el sistema de ellos. |
