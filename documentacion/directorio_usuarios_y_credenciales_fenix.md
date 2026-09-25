# 🔐 DIRECTORIO OFICIAL DE CUENTAS DE USUARIO Y MATRIZ DE ACCESO
**Esquema de Base de Datos `usuarios` — Sistema Fénix 2.0**
**Grupo Trujano — Alineación ISO 9001:2015 & ISO 14001:2015**

---

| CONTROL DOCUMENTAL | DATOS DE REGISTRO |
| :--- | :--- |
| **Código del Documento** | `REG-SEG-003-CRED` |
| **Título** | Directorio de Cuentas de Usuario y Matriz de Accesos por Módulo |
| **Esquema de BD** | `usuarios` (`usuarios.cuentas` y `usuarios.permisos_modulos`) |
| **Versión** | `2.0` (Agosto 2026) |
| **Clasificación de Seguridad** | 🛑 **CONFIDENCIAL / USO INTERNO EXCLUSIVO** |

---

## 🔒 AVISO DE SEGURIDAD
> [!IMPORTANT]
> **Por políticas de seguridad de la información y normatividad ISO 27001 / ISO 9001, las contraseñas de acceso NO se publican en este documento.**
> Las contraseñas de primer ingreso son entregadas de forma confidencial a cada titular por el Administrador de Sistemas.

---

## 🔑 TABLA MAESTRA DE CUENTAS DE USUARIO Y PERMISOS POR MÓDULO

| ID | Usuario | Nombre del Titular | Puesto / Área | Rol Principal | Páginas / Módulos Autorizados | Nivel de Permiso |
| :---: | :--- | :--- | :--- | :---: | :--- | :---: |
| **1** | `admin` | Administrador General Fénix | Dirección de Operaciones | `ADMIN` | **TODAS LAS PÁGINAS**: Centro de Mando, Resumen, Diésel, Gasolina, Facturas, Tags, Jalisco, Catálogos. | **TOTAL** *(Crear, Editar, Aprobar, Eliminar, Exportar)* |
| **2** | `consulta` | Usuario Lectura / Auditoría | Auditoría Interna / ISO | `CONSULTA` | **PÁGINAS DEL CENTRO DE MANDO**: Resumen, Diésel, Gasolina, Facturas, Tags, Jalisco, Catálogos. | **SOLO LECTURA** *(Sin edición, sin botones de guardado ni exportación)* |
| **3** | `chofer_marimba` | Operador Pipa / Marimba | Distribución de Diésel | `CHOFER_MARIMBA` | **MÓDULO MARIMBA (CAMPO)**: Carga de Gasolinería a Pipa y Despacho a Maquinaria. | **CAPTURA DE DOS VÍAS** *(Llenado de Entradas y Despachos)* |
| **4** | `residente_obra` | Ingeniero Residente de Obra | Supervisión de Campo | `RESIDENTE_OBRA` | **SOLICITUDES Y RECEPCIÓN**: Petición de saldo por obra y confirmación de diésel en máquinas. | **CAPTURA LIMITADA** *(Solo su obra asignada)* |
| **5** | `capturista_gasolina` | Capturista de Gasolina | Mesa de Control Gasolinerías | `CAPTURISTA` | **CAPTURA Y CONCILIACIÓN DE GASOLINA**: Captura por Placa y Captura Masiva Excel (Levet/JDJ). | **CAPTURA / CONCILIACIÓN** *(Módulo de Gasolina)* |
| **6** | `capturista_acarreos` | Checador de Acarreos y Fresado | Control de Materiales | `CAPTURISTA` | **MÓDULO DE ACARREOS Y MEZCLA**: Registro de viajes, cubicaje de camiones y boletas. | **CAPTURA DE CAMPO** *(Acarreos y Mezcla)* |

---
*Documento oficial de control de accesos para el Sistema Fénix 2.0.*
