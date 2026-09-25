# 🚀 DOCUMENTO DE METAS, VISIÓN FUTURA Y PLAN DE DESARROLLO APP MÓVIL
**De Producto Mínimo Viable (MVP) a Aplicación Móvil de Campo con Conciliación de Dos Vías (Dual-Way) y Roles RBAC**
**Sistema Fénix 2.0 — Grupo Trujano**

---

| CONTROL DE DOCUMENTO | DATOS DE REGISTRO |
| :--- | :--- |
| **Código del Documento** | `PL-IT-002-VISION-APP` |
| **Título** | Hoja de Ruta, Metas de Desarrollo App Móvil de Campo y Conciliación Bireccional |
| **Versión** | `2.0` (Agosto 2026) |
| **Aplica Para** | Desarrollo Fénix Mobile, Control de Accesos por Rol (RBAC) y Certificaciones ISO |

---

## 🎯 1. DIAGNÓSTICO ACTUAL: DEL MVP A LA APP MÓVIL DE CAMPO

### 1.1 Estado Actual (Producto Mínimo Viable - MVP):
Hasta este momento, el **Sistema Fénix 2.0** opera como un **MVP (Producto Mínimo Viable)** exitoso que ha logrado:
- Centralizar la base de datos PostgreSQL (`fenix_db`).
- Automatizar la lectura masiva de Excel de gasolinerías (Levet/JDJ) en 0.3 segundos.
- Generar reportes ejecutivos en Excel y PDF con la división normada de **6 Días vs 5 Días** trabajados por ingeniero.
- Realizar la conciliación de facturas y Complementos de Pago CFDI del SAT.

### 1.2 La Siguiente Gran Meta: "Fénix Mobile App" (Captura Directa en Campo):
Para eliminar la captura manual diferida, la meta estratégica del proyecto es evolucionar el MVP hacia una **Aplicación Móvil PWA (Progressive Web App) / App de Campo**, donde cada operador en el frente de obra capture la información en el instante preciso en que ocurre el evento.

---

## 🔒 2. ARQUITECTURA DE SEGURIDAD: CONTROL DE ACCESO BASADO EN ROLES (RBAC)

En la futura **App Móvil de Campo Fénix**, cada usuario accederá mediante credenciales únicas y tendrá una interfaz **estrictamente limitada** al rol operativo que desempeña, evitando distracciones y garantizando la confidencialidad de la información.

```
                                  ┌────────────────────────────────┐
                                  │      APP MÓVIL FÉNIX 2.0       │
                                  └───────────────┬────────────────┘
                                                  │
             ┌────────────────────────────────────┼────────────────────────────────────┐
             ▼                                    ▼                                    ▼
┌─────────────────────────┐          ┌─────────────────────────┐          ┌─────────────────────────┐
│  ROL 1: CHOFER MARIMBA  │          │  ROL 2: RESIDENTE OBRA  │          │   ROL 3: ADMINISTRADOR  │
│ • Entrada: Carga Gas.   │          │ • Solicitud Diésel      │          │ • Dashboards & KPIs     │
│ • Salida: Suministro    │          │ • Confirmación Cargas   │          │ • Conciliación Martes   │
│   a Maquinaria          │          │ • Horómetros / Km       │          │ • Reportes ISO 9001/14k │
└─────────────────────────┘          └─────────────────────────┘          └─────────────────────────┘
```

### 👤 Matriz de Permisos por Rol:

1. **Rol 1: Chofer / Operador de la Marimba (Pipa Cisterna)**:
   - **Acceso Permitido**: *Exclusivamente* el módulo de **Conciliación de Dos Vías (Diésel)**.
   - **Restricción**: No puede ver precios globales, facturas contables ni información de otros módulos o frentes.

2. **Rol 2: Residente / Responsable de Obra**:
   - **Acceso Permitido**: Generar solicitudes de combustible para su obra, confirmar la recepción de diésel en sus máquinas y registrar lecturas de horómetros/kilometraje.

3. **Rol 3: Chófer de Acarreos / Checador de Campo**:
   - **Acceso Permitido**: Registrar boletas de viajes de fresado/material y cubicaje de camiones.

4. **Rol 4: Administrador / Director / Auditor ISO**:
   - **Acceso Permitido**: Vista completa del Centro de Mando, aprobación de presupuestos, conciliación de los Martes y reportes oficiales.

---

## 🔄 3. CONCILIACIÓN DE DOS VÍAS (DUAL-WAY RECONCILIATION)

El núcleo de la App Móvil para el **Chofer de la Marimba** es el **Mapeo en Bucle Cerrado (Closed-Loop Fuel Tracking)**.

```mermaid
flowchart LR
    A[Gasolinería / Proveedor] -->|1. Entrada: Ticket/Factura Carga Pipa| B(MARIMBA / PIPA)
    B -->|2. Salida: Despacho a Tanque de Máquina| C[Maquinaria Pesada en Obra]
    
    subgraph CONCILIACIÓN DE DOS VÍAS (SISTEMA FÉNIX)
        B1(Litros Recibidos en Tanque Móvil) <--> B2(Suma de Litros Entrega a Máquinas)
    end
    
    B1 & B2 --> D{¿Diferencia == 0?}
    D -->|Sí| E[✔ Balance Correcto / Aprobado]
    D -->|No| F[⚠️ ALERTA DE MERMA / DESVÍO - ISO 14001]
```

### 📋 Las Dos Vías de Captura del Chofer de la Marimba:

#### 📥 VÍA 1: ENTRADA (Lo que Recibe la Marimba):
- El chofer llega a la gasolinería o planta proveedora.
- Registra en la App: Fecha, Estación de Servicio, Litros cargados al tanque móvil de la Marimba y fotografía del ticket/remisión.
- *Resultado*: Se incrementa el saldo disponible en el "Tanque Móvil Marimba".

#### 📤 VÍA 2: SALIDA (Lo que Entrega la Marimba):
- El chofer acude a la obra y despacha combustible a cada máquina.
- Registra en la App: Selección del Equipo Económico (ej. *Pavimentadora PV-01*), Obra, Litros despachados y fotografía del contador/ticket de la pistola de despacho.
- *Resultado*: Se descuenta del saldo del "Tanque Móvil Marimba" y se le asigna el consumo a la máquina correspondiente.

#### ⚖️ Conciliación Automática:
$$	ext{Litros Faltantes / Merma} = 	ext{Litros Entrada (Gasolinería)} - \sum 	ext{Litros Salida (Máquinas)}$$
Si existe una discrepancia no justificada, el sistema emite una **Alerta de Merma Anómala** (cumpliendo con el control ambiental de hidrocarburos de la norma **ISO 14001**).

---

## 📅 4. HOJA DE RUTA Y METAS A FUTURO (ROADMAP ISO)

```mermaid
gantt
    title Hoja de Ruta: De MVP a App Móvil y Certificación ISO
    dateFormat  YYYY-MM-DD
    section Fase 1: MVP Web
    Portals 5001/5002 & BD PostgreSQL :done, p1, 2026-06-01, 2026-08-04
    section Fase 2: App Móvil
    Diseño PWA & Módulo Chofer Marimba (2 Vías) :active, p2, 2026-08-05, 2026-08-30
    Autenticación por Roles (RBAC) :planned, p3, 2026-08-20, 2026-09-10
    section Fase 3: ISO 9001/14001
    Módulo Horómetros (Lts/Hr) & Huella CO2 :planned, p4, 2026-09-11, 2026-09-30
    Auditoría Externa de Certificación ISO :planned, p5, 2026-10-01, 2026-10-20
```

---

## 🌐 5. OPCIONES PARA COMPARTIR Y PUBLICAR EL SISTEMA EN LA RED / INTERNET

Para que otras personas dentro de la empresa o directivos fuera de la oficina puedan ingresar a las páginas y servidores de Fénix, existen 2 modalidades recomendadas:

### 🏠 Opción A: Acceso en Red Local (WiFi / LAN de la Empresa)
Sin necesidad de instalar programas adicionales, cualquier persona conectada al mismo WiFi o red de la oficina puede entrar ingresando la **IP Local de la computadora principal**:
- **Portal de Captura**: `http://192.168.68.100:5001`
- **Centro de Mando Admin**: `http://192.168.68.100:5002`

### 🌍 Opción B: Acceso Global desde Internet mediante un Link Seguro (ngrok / Cloudflare Tunnel)
Si se requiere que directivos o ingenieros en campo entren desde cualquier lugar fuera de la oficina mediante un enlace web (ej. `https://fenix-trujano.ngrok-free.app`), se puede habilitar un túnel seguro gratuito mediante **ngrok** o **Cloudflare Tunnel**:
1. Se ejecuta `ngrok http 5001` en la consola.
2. Genera un enlace público encriptado SSL (`https://...`).
3. Ese link se comparte por WhatsApp o correo para acceso remoto inmediato.

---

## 📝 CONCLUSIÓN
Este documento de metas formaliza la ruta de escalabilidad del **Sistema Fénix 2.0**. El archivo en formato Markdown (`.md`) es **100% compatible para convertirse directamente a un documento de Microsoft Word (`.docx`)** o integrarse al manual de procesos para las auditorías de **ISO 9001 e ISO 14001**.
