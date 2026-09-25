# 📜 HISTORIAL DE VERSIONES Y CONTROL DE CÓDIGO FUENTE — SISTEMA FÉNIX 2.0
Fecha de Snapshot: 2026-08-04 12:24:44

---

## 🚀 VERSIÓN 2.0 (ACTUAL - AGOSTO 2026)
### 1. Módulo de Gasolina:
- **Captura Masiva y Conciliación desde Excel (Levet / JDJ)**:
  - Carga drag-and-drop de archivos Excel (`CONTROL JDJ PROVISIONAL`).
  - Separación automática de cargas mensuales por semanas ISO (`Semana 26` a `Semana 31`).
  - Detección automática de duplicados vs nuevos registros contra `gasolina.consumos`.
  - Guardado en lote en la base de datos PostgreSQL.
- **Autocompletado Inmediato (0ms)**: Relleno automático de Obra, Conductor y Vehículo al seleccionar Placa.

### 2. Módulo de Diésel y Centro de Mando Admin:
- **Distinción de Días Trabajados por Ingeniero (6 Días vs 5 Días)**:
  - **Sección 6 Días** (`APOLINAR`, `FRANCISCO JAVIER`, `ING. DIEGO CARREOLA`, `JACK`, `LUIS`): Multiplicador `Aut. Diario × 6`.
  - **Sección 5 Días** (`DAYANNE`, `EDGAR`, `SAMUEL`): Multiplicador `Aut. Diario × 5`.
  - Reportes ejecutivos dinámicos en **Excel** y **PDF**.
- **Conciliación de Complementos de Pago SAT (CFDI)**:
  - Procesamiento de Complemento Folio 58914 ($316,944.71 MXN).
  - Verificación de 44 folios fiscales y actualización de estatus a `PAGADA`/`PARCIAL`.

### 3. Módulos Operativos Integrados:
- **Jalisco**: Captura y comprobantes de obras foráneas.
- **Acarreos y Fresado**: Viajes, cubicaje de camiones y boletas.
- **Mezcla Asfáltica**: Control de producción y tiradas.
- **Tags / Telepeaje**: Estado de cuenta y afectación de casetas (Pásalo, IAVE, etc.).

---

## 📦 VERSIÓN 1.0 (LEGACY)
- Captura manual básica individual de consumos.
- Reportes planos sin división de días trabajados.
- Ausencia de conciliación masiva Excel para gasolinerías.
