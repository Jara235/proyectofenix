# 🗺️ PLAN GENERAL DEL PROYECTO FÉNIX 2.0
**Estrategia de Transformación Digital, Control de Combustibles y Preparación para Certificación ISO 9001 & ISO 14001**

---

## 🚀 1. RESUMEN EJECUTIVO Y OBJETIVOS ESTRATÉGICOS

El **Proyecto Fénix 2.0** es la solución tecnológica central para **Grupo Trujano**, orientada a digitalizar, auditar y controlar en tiempo real el consumo de hidrocarburos (Diésel y Gasolina), acarreos, producción de mezcla asfáltica y telepeaje.

### 🏆 Objetivos Institucionales:
1. **Alineación ISO 9001 (Sistema de Gestión de Calidad)**:
   - Errores cero en facturación y pago de combustibles.
   - Conciliación matemática al centavo del **Tríptico de Diésel** (Solicitado en WhatsApp vs Facturado por Gasolinería en Marimba vs Repartido por Maquinaria).
   - Trazabilidad y no duplicidad de cargas mediante el **Motor de Conciliación Masiva Fénix**.
2. **Alineación ISO 14001 (Sistema de Gestión Ambiental)**:
   - Medición y reducción del consumo de combustibles fósiles.
   - Control de rendimiento (Litros/Hora y Litros/Km) para la detección temprana de fugas, robo o fallas de mantenimiento contaminantes.

---

## 📊 2. ESTADO DE AVANCE POR FASES Y MÓDULOS

```mermaid
gantt
    title Plan General del Proyecto Fénix 2.0
    dateFormat  YYYY-MM-DD
    section Fase 1: Cimientos
    Arquitectura Doble Portal & PostgreSQL :done, p1, 2026-06-01, 2026-06-15
    section Fase 2: Diésel y SAT
    Captura Maquinaria, Facturas CFDI & Complementos SAT :done, p2, 2026-06-16, 2026-07-15
    Distinción Días Trabajados 6D vs 5D :done, p2b, 2026-07-16, 2026-07-25
    section Fase 3: Gasolina Masiva
    Captura Individual, Topes & Captura Masiva Excel Levet :done, p3, 2026-07-26, 2026-08-04
    section Fase 4: Operaciones
    Acarreos, Fresado, Mezcla Asfáltica & Telepeaje Tags :done, p4, 2026-07-01, 2026-08-04
    section Fase 5: Automatización
    Pestaña Conciliación Martes & Bot WhatsApp N8N :active, p5, 2026-08-05, 2026-08-25
    section Fase 6: ISO 14001
    Horómetros Lts/Hr & Indicadores CO2 :planned, p6, 2026-08-26, 2026-09-20
```

---

### ✅ **FASE 1: Cimientos y Arquitectura Base (COMPLETADA)**
- [x] **Doble Portal Integrado**: Portal de Captura Operativa (`http://localhost:5001`) y Centro de Mando Administrativo (`http://localhost:5002`).
- [x] **Base de Datos Centralizada PostgreSQL (`fenix_db`)**: Implementación de esquemas relacionales `diesel`, `gasolina`, `catalogos`, `tags`, `acarreos`, `mezcla`.
- [x] **Log de Auditoría Inalterable**: Registro de acciones en `catalogos.audit_log` para cumplimiento de norma ISO 9001.

---

### ✅ **FASE 2: Módulo de Diésel, Facturación CFDI y Reglas 6D/5D (COMPLETADA)**
- [x] **Captura de Maquinaria Pesada**: Registro de cargas por equipo económico y obra destino.
- [x] **Extracción de PDF/Bitácoras**: Lector inteligente de reportes en PDF.
- [x] **Conciliación de Complementos de Pago SAT**: Procesamiento de archivos PDF/XML CFDI, verificación de UUIDs y estatus de pago (`PAGADA`, `PARCIAL`).
- [x] **Regla de Autorización Semanal de Ingenieros**: Clasificación de responsables en **Sección 6 Días** (`Aut. Diario × 6`) vs **Sección 5 Días** (`Aut. Diario × 5`) en reportes ejecutivos de Excel y PDF.

---

### ✅ **FASE 3: Módulo de Gasolina y Captura Masiva/Conciliación Excel (COMPLETADA)**
- [x] **Captura Individual con Autocompletado 0ms**: Autocompletado inteligente de Obra, Conductor y Vehículo al seleccionar Placa o `S/P` (Equipos Menores).
- [x] **Captura Masiva Excel de Gasolinerías (Levet/JDJ)**:
  - Carga drag-and-drop de archivos Excel mensuales (`CONTROL JDJ PROVISIONAL`).
  - Separación automática por semanas ISO (`Semana 26`, `Semana 27`, `Semana 28`, `Semana 29`, `Semana 30`, `Semana 31`).
  - Motor de conciliación automática: detección de registros `✔ CONCILIADOS` vs `🆕 NUEVOS`.
  - Inserción masiva en lote a la base de datos con un clic.

---

### ✅ **FASE 4: Operaciones de Acarreos, Fresado, Mezcla Asfáltica y Telepeaje (COMPLETADA)**
- [x] **Acarreos y Fresado**: Registro de viajes, cubicaje de camiones y boletas por obra.
- [x] **Mezcla Asfáltica**: Control de producción y tiradas de mezcla por planta.
- [x] **Telepeaje Tags**: Conciliación de movimientos de casetas (Pásalo, IAVE, Viapass).

---

## 🔮 3. HOJA DE RUTA Y TAREAS A FUTURO (ROADMAP ISO)

Para llevar el sistema al estándar de **Certificación ISO 9001 e ISO 14001**, se establece la siguiente hoja de ruta de implementación a futuro:

### 🔜 **FASE 5: Automatización del Flujo Real y Conciliación Semanal (Corto Plazo - Agosto 2026)**

#### 1. Pestaña de "Conciliación Semanal de los Martes" (Tríptico de Diésel):
- **Objetivo**: Crear una pestaña dedicada en el portal administrativo que realice el cruce automático en 3 columnas:
  - `Columna A`: Total Solicitado / Autorizado en WhatsApp por Obra.
  - `Columna B`: Total Facturado por la Gasolinería a la Marimba.
  - `Columna C`: Total Repartido por la Marimba y Registrado por Maquinaria en Fénix.
- **Beneficio ISO 9001**: Emisión automática del Acta de Conciliación Semanal con cálculo instantáneo de mermas o diferencias.

#### 2. Integración de Bot de WhatsApp (N8N / Telegram API):
- **Objetivo**: Conectar un webhook que reciba las solicitudes de los ingenieros y los reportes diarios de la Marimba directamente desde el grupo de WhatsApp, rellenando la base de datos sin necesidad de captura manual.
- **Beneficio ISO 9001**: Eliminación del error humano y captura en tiempo real.

---

### 🍃 **FASE 6: Eficiencia Energética, Horómetros y Gestión Ambiental (Mediano Plazo - Septiembre 2026)**

#### 1. Módulo de Horómetros, Kilometraje y Rendimiento ($Lts/Hr$ y $Lts/Km$):
- **Objetivo**: Capturar la lectura del horómetro de la máquina o kilometraje al momento de cada carga de combustible.
- **Cálculo de Desempeño**:
  $$\text{Rendimiento} = \frac{\text{Litros Suministrados}}{\text{Horas Máquina Trabajadas}}$$
- **Beneficio ISO 14001**: Emisión de alertas cuando una máquina supere su consumo estándar por hora, detectando fallas mecánicas, necesidad de afinar motores o fuga no autorizada de combustible.

#### 2. Módulo de Indicadores Ambientales e Impresión de Huella de Carbono ($CO_2$):
- **Objetivo**: Convertir el total de litros de diésel y gasolina consumidos en toneladas de $CO_2$ emitidas, utilizando factores de emisión normados por SEMARNAT.
- **Beneficio ISO 14001**: Reporte de Desempeño Ambiental para auditorías de sostenibilidad de Grupo Trujano.

---

## 🗄️ 4. INVENTARIO DE RECURSOS, RESPALDOS Y FORMATOS DEL PROYECTO

| Recurso / Archivo | Tipo de Recurso | Propósito en el Proyecto |
| :--- | :---: | :--- |
| `GC-COMB-003` a `GC-COMB-006` | Formatos Físicos | Control de vales de diésel, planta, tanque pegaso y operadores. |
| `GC-COMB-3.1` | Excel Maestro | Planilla consolidada de control de combustible Grupo Trujano. |
| `fenix_v2_schema.sql` | Estructura BD | Dump oficial del esquema PostgreSQL de la base de datos `fenix_db`. |
| `CONTROL JDJ PROVISIONAL (1).xlsx` | Insumo Conciliación | Archivo de cargas de gasolinería Levet utilizado para prueba y producción masiva. |
| `manual_operativo_sistema_fenix.md` | Documentación | Manual de Operación y Procesos para certificaciones ISO. |

---

## 🎯 CONCLUSIÓN
El **Sistema Fénix 2.0** cuenta con los cimientos técnicos, la base de datos PostgreSQL robusta y los módulos operativos clave para soportar la operación diaria de **Grupo Trujano**. La ejecución de las Fases 5 y 6 completará el ciclo de automatización y auditoría requerido para lograr la **Certificación Internacional ISO 9001 e ISO 14001**.
