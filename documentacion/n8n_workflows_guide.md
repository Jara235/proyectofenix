# Guía Técnica: Configuración de Flujos en n8n con IA (Gemini 1.5 Flash)

Esta guía detalla los pasos para configurar los dos flujos de trabajo principales en tu servidor **n8n** para procesar los reportes de WhatsApp del grupo, analizarlos con la IA y guardarlos en tu base de datos de **Supabase**.

---

## 🚀 Flujo 1: Recepción, Análisis con Gemini e Inserción en Tiempo Real

Este flujo se activa cada vez que llega un mensaje de WhatsApp (texto o imagen con ticket).

```
[Webhook WhatsApp] ──► [Validar Mensaje] ──► [Gemini Multimodal Node] 
                                                    │ (Clasifica y Extrae JSON)
                                                    ▼
[Supabase: Insertar] ◄── [Router de Categoría] ◄── [Resolver IDs Catálogos]
```

### Paso 1: Nodo Webhook (WhatsApp Trigger)
* **Tipo:** Webhook (HTTP POST).
* **Ruta:** `/webhook/whatsapp`.
* **Seguridad:** En la consola de Meta Developers, configura tu webhook de WhatsApp para apuntar a la URL de tu Railway (`https://tu-n8n.up.railway.app/webhook/whatsapp`). Añade un **Verify Token** (ej. `FenixToken2026`) para validar la petición.

### Paso 2: Nodo de Descarga de Medios (Opcional - Si hay Imagen)
Si el mensaje contiene una foto (ticket o medidor), la WhatsApp API envía un `media_id`. 
* Usa un nodo **HTTP Request** para llamar a la API de WhatsApp: `GET https://graph.facebook.com/v19.0/{{$json.media_id}}` (añadiendo tu Bearer Token en cabeceras).
* Esto descargará el archivo binario de la imagen para pasarlo al nodo de Gemini.

### Paso 3: Nodo de Gemini 1.5 Flash (AI Agent Multimodal)
Configura el nodo de Gemini (a través del **Google Gemini Chat Model** de n8n) con el siguiente **System Prompt** para asegurar que devuelva datos estructurados en formato JSON:

```text
Eres el clasificador oficial de combustible de Grupo Trujano para el "Proyecto Fénix". 
Tu tarea es analizar el mensaje de texto recibido en el grupo de WhatsApp (y la imagen adjunta, si existe) y extraer los datos estructurados en un objeto JSON limpio.

Clasifica el mensaje en una de estas 3 bitácoras:
1. "pegaso": Reportes de entradas/salidas del Tanque Pegaso.
2. "marimba": Reportes de entradas/salidas de la Marimba (Pipa M-01 / Mamba).
3. "obra": Reportes de recepción en obra y consumo de combustible de las máquinas.

Catálogos de validación:
- Obras válidas: "MT" (México-Toluca), "L3M" (Lerma - Tres Marías), "CL" (Chamapa-Lechería).
- Equipos válidos: "FR-01", "CP-01", "EX-01", "RT-01", "MG-01", "PT-01", "PP-01", "CM-01", "CR-01", "OTRO".

Reglas de extracción:
- Si es "pegaso": Identifica tipo_movimiento ("Entrada", "Salida a Marimba" o "Salida Directa Máquina"). Las entradas son de "Gasolinera Huixquilucan".
- Si es "marimba": Identifica tipo_movimiento ("Entrada desde Pegaso", "Entrada desde Gasolinera" o "Salida a Obra").
- Si es "obra": Identifica fuente ("Marimba M-01" o "Pegaso Directo"). Extrae litros, costo_por_litro, horas_trabajadas o kilometraje si se mencionan.

Devuelve estrictamente un objeto JSON con este formato (no agregues bloques de código markdown ni texto adicional):
{
  "categoria": "pegaso" | "marimba" | "obra" | "desconocido",
  "datos": {
    "tipo_movimiento": "NombreMovimiento",
    "litros": 0.0,
    "costo_por_litro": 0.0,
    "obra_codigo": "MT" | "L3M" | "CL" (null si no aplica),
    "equipo_codigo": "EX-01" (etc, null si no aplica),
    "horas_trabajadas": 0.0 (null si no aplica),
    "kilometraje": 0.0 (null si no aplica),
    "fuente": "Marimba M-01" | "Pegaso Directo" (solo para obra),
    "origen_destino": "Gasolinera Huixquilucan" | "Tanque Pegaso" (solo para Pegaso/Marimba),
    "observaciones": "Resumen rápido del texto"
  }
}
```

### Paso 4: Nodo Supabase (Búsqueda de IDs e Inserción)
1. **Paso Intermedio (HTTP o Supabase Node):** Consulta los UUIDs de la Obra y el Equipo usando los códigos extraídos (`obra_codigo` y `equipo_codigo`) mediante consultas `SELECT` en las tablas `fenix_obras` y `fenix_equipos`.
2. **Nodo de Router (Switch):** Evalúa la propiedad `categoria` devuelta por Gemini:
   - Si es `'pegaso'` ➡️ Inserta en la tabla `fenix_bitacora_pegaso`.
   - Si es `'marimba'` ➡️ Inserta en la tabla `fenix_bitacora_marimba`.
   - Si es `'obra'` ➡️ Inserta en la tabla `fenix_bitacora_obra`.
   - Si es `'desconocido'` o hay error ➡️ Inserta en `fenix_whatsapp_inbox` con `procesado = false` para revisión manual.

---

## ⏰ Flujo 2: Cierre Diario, Reporte de Conciliación y Alertas

Este flujo se ejecuta de forma automática todas las noches a las 8:00 PM.

```
[Cron Trigger 8:00 PM] ──► [Query Supabase del Día] ──► [Gemini Consolidador] 
                                                                │ (Redacta Resumen)
                                                                ▼
[WhatsApp: Enviar Reporte] ◄── [Email / Notification] ◄── [Guardar Resumen]
```

### Paso 1: Trigger Cron
* **Programación:** Todos los días a las 20:00 (8:00 PM) hora local.

### Paso 2: Nodos de Supabase (Lectura de Bitácoras)
Realiza 3 consultas a Supabase filtrando por la fecha actual (`fecha = CURRENT_DATE`):
* `SELECT * FROM fenix_bitacora_pegaso`
* `SELECT * FROM fenix_bitacora_marimba`
* `SELECT * FROM fenix_bitacora_obra`

### Paso 3: Nodo de Conciliación (Código Javascript en n8n)
Antes de enviar los datos al LLM, sumamos los litros y calculamos las diferencias matemáticas en un nodo **Code (JS)** de n8n:
```javascript
// Obtener resultados de los nodos de lectura anteriores
const pegaso = $('Supabase_Pegaso').all();
const marimba = $('Supabase_Marimba').all();
const obra = $('Supabase_Obra').all();

// Sumar flujos de transferencia
const pegasoAMarimba = pegaso.filter(r => r.json.tipo_movimiento === 'Salida a Marimba').reduce((a,c) => a + c.json.litros_salida, 0);
const marimbaDePegaso = marimba.filter(r => r.json.tipo_movimiento === 'Entrada desde Pegaso').reduce((a,c) => a + c.json.litros_entrada, 0);
const diffPegasoMarimba = pegasoAMarimba - marimbaDePegaso;

const marimbaAObra = marimba.filter(r => r.json.tipo_movimiento === 'Salida a Obra').reduce((a,c) => a + c.json.litros_salida, 0);
const obraDeMarimba = obra.filter(r => r.json.fuente === 'Marimba M-01').reduce((a,c) => a + c.json.litros_recibidos, 0);
const diffMarimbaObra = marimbaAObra - obraDeMarimba;

return {
  json: {
    pegasoAMarimba,
    marimbaDePegaso,
    diffPegasoMarimba,
    marimbaAObra,
    obraDeMarimba,
    diffMarimbaObra,
    totalDiferencia: Math.abs(diffPegasoMarimba) + Math.abs(diffMarimbaObra)
  }
};
```

### Paso 4: Nodo Gemini (Generador de Reporte Ejecutivo)
Envía las métricas sumadas y las diferencias al LLM con el siguiente prompt:
```text
Redacta un reporte ejecutivo diario de combustible para el administrador basado en estos resultados de hoy:
- Diferencia Pegaso a Mamba: {{ $json.diffPegasoMarimba }} Litros.
- Diferencia Mamba a Obras: {{ $json.diffMarimbaObra }} Litros.
- Total Diferencia General: {{ $json.totalDiferencia }} Litros.

Escribe el reporte en un tono profesional, claro y conciso. Si la diferencia es 0, felicita al equipo por el control perfecto. Si hay diferencias, indica los litros faltantes y genera una advertencia para auditar las bitácoras físicas de inmediato.
```

### Paso 5: Notificación
Envía el reporte generado por Gemini:
1. **Vía Email:** A la bandeja de tu hermana.
2. **Vía WhatsApp:** Envía el texto a su chat personal de WhatsApp usando el nodo de WhatsApp en n8n para que tenga el resumen del día directamente en su teléfono celular en cuanto cierre la jornada.

---

## 🧠 Configuración Detallada de Prompts IA en n8n (Gemini 1.5 Flash)

A continuación, se presentan las especificaciones exactas para los nodos de IA encargados de las tareas complejas de **OCR de flujómetros analógicos** y **extracción de listas de estimados**.

### 📸 1. Lectura Multimodal de Flujómetros Analógicos (OCR)

Cuando un operador envía una fotografía del medidor de flujo de la pipa (Marimba M-01) o del Tanque Pegaso, el flujo de n8n descarga la imagen y la pasa como entrada binaria al nodo **Google Gemini Chat Model** (o Gemini Multimodal Node).

#### Prompt de Sistema para OCR Multimodal:
```text
Eres un asistente experto en digitalización industrial de Grupo Trujano para el "Proyecto Fénix". 
Tu tarea es examinar la fotografía adjunta, que muestra un medidor de flujo analógico mecánico (comúnmente de marca Fill-Rite, Series 900 o similar).

Sigue estas reglas estrictas para la lectura visual:
1. Identifica el contador de números rotatorios principal (las ruedas mecánicas blancas con números negros, o viceversa, que registran los litros despachados en el servicio actual).
2. Lee los dígitos de izquierda a derecha. Si hay ceros a la izquierda (ej. "0040"), extrae el valor neto numérico (40).
3. Ignora el totalizador acumulativo secundario (números pequeños que no vuelven a cero y suelen estar en la parte inferior o superior).
4. Ignora cualquier texto del medidor como "SERIES 900 METER", "Tuthill", "Fill-Rite", "RESET TO ZERO", o "US GALLONS".
5. Si la imagen está demasiado borrosa o no se ve el contador, pon el campo "litros_leidos" como null y especifica la razón en "incidencia".

Devuelve exclusivamente un objeto JSON estructurado:
{
  "litros_leidos": 0.0, // El número de litros leído (ej: 40.0, 250.0). Pon null si no es legible.
  "confianza": "alta" | "media" | "baja",
  "incidencia": "Descripción del estado de la lectura o por qué es de baja confianza"
}
```

---

### 📋 2. Extracción de Listas de Estimados Semanales de Ingenieros

Los ingenieros de obra envían un texto formateado al inicio de la semana con la planeación del consumo por máquina. El nodo **Google Gemini Chat Model** en n8n se configura para extraer esta información estructurada en lote.

#### Prompt de Sistema para Procesamiento de Estimados Semanales:
```text
Eres el extractor oficial de solicitudes de combustible de Grupo Trujano. Tu labor es procesar el mensaje de texto recibido que contiene la lista de estimados semanales dada por el ingeniero de obra y convertirlo en un arreglo JSON estructurado para insertarlo en Supabase.

Catálogos de validación de Maquinaria (Códigos económicos oficiales):
- "PER-200" (Perfiladora Wirtgen F-200)
- "VOG-03" (Vögele-03)
- "HAMM" (Tándem Hamm)
- "DINA" (Neumático Dinapac)
- "BAR-01" (Barredora Broce Broom)
- "RET-02" (Retroexcavadora)
- "PET-02" (Petrolizadora)
- "CAM-02" (Camión Impacto)
- "COM-01" (Compresor Ingersoll Rand)
- "TL-01" (Torre de Luces Maxilight)
- "CP-01" (Compactador)
- "EX-01" (Excavadora)

Catálogo de Obras:
- "MT" (México-Toluca)
- "L3M" (Lerma - Tres Marías)
- "CL" (Chamapa-Lechería)
- "LT" (Lerma-Tenango)

Instrucciones de extracción:
1. Identifica la fecha o semana mencionada. Si se menciona "Lunes 15 de junio 2026", usa la fecha "2026-06-15" como semana_fecha.
2. Identifica la Obra asociada al listado (ej: "Obra México-Toluca" -> "MT").
3. Para cada elemento de la lista numerada, extrae el código económico del equipo que corresponda según el catálogo, y los litros de combustible estimados asignados.
4. Si se detallan propósitos especiales (ej. "Vogele-03: 100 lts equipo, 20 lts limpieza"), suma los litros totales asignados a esa máquina (120 lts).

Devuelve exclusivamente un arreglo JSON con el siguiente formato de objetos (sin bloques de código markdown ni texto adicional):
[
  {
    "semana_fecha": "YYYY-MM-DD",
    "obra_codigo": "MT",
    "equipo_codigo": "VOG-03",
    "litros_estimados": 120.0
  },
  ...
]
```

#### Inserción de Estimados en Supabase desde n8n:
El nodo posterior de Supabase ejecuta un bucle o una inserción en lote (Bulk Insert) usando el arreglo JSON retornado por Gemini. La tabla destino es `fenix_estimados_semanales`. Utiliza la columna `obra_codigo` y `equipo_codigo` en combinación con subconsultas para resolver los UUIDs correspondientes.

