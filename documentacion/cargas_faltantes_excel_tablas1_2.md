# ⛽ Cargas de Excel (Tablas 1 y 2 - Semana 30) vs. Base de Datos
## Análisis de Cargas Presentes en el Archivo Excel que Faltan o Coinciden en el Sistema

### 📊 Resumen Estadístico
- **Total Cargas en Tabla 1 (J.D.J. Gasolina):** `52 cargas` | `$93,997.86 MXN`
- **Total Cargas en Tabla 2 (TRD San Miguel Gasolina):** `12 cargas` | `$790,735.08 MXN`
- **Total Cargas Tablas 1 y 2 Combinadas:** `64 cargas` | `$884,732.94 MXN`
- **Cargas Coincidentes con la Base de Datos:** `34 cargas`
- ⚠️ **Cargas Presentes en Excel pero FALTANTES en la Base de Datos:** `30 cargas` | **Monto Faltante: `$843,706.51 MXN`**

---
### 🔴 1. Cargas del Excel (Tablas 1 y 2) que NO ESTÁN en la Base de Datos
> [!WARNING]
> Estas son las cargas registradas en la plantilla oficial de Excel de la Semana 30 que **aún no han sido capturadas/inyectadas en la Base de Datos**:

| # | Tabla Excel | Fecha | Responsable / Conductor | Centro de Trabajo / Obra | Unidad / Equipo | Placa | Proveedor | Importe Excel ($) |
|--:|:------------|:------|:------------------------|:-------------------------|:----------------|:------|:----------|------------------:|
| 1 | Tabla 1 (J.D.J.) | 2026-07-25 | DIEGO CARREOLA | BACHEO TOLUCA Y C. VICENTE LOMBARDO | MITSUBISHI L1200 | **`NYZ829C`** | LEVET | **$922.74** |
| 2 | Tabla 1 (J.D.J.) | 2026-07-20 | TOMAS ARANDA PROSPERO | BACHEO TOLUCA Y C. VICENTE LOMBARDO | DODGE RAM 4000 (3/2) | **`LF05470`** | MOBILE | **$2,000.00** |
| 3 | Tabla 1 (J.D.J.) | 2026-07-25 | JAVIER PEREZ DÍAZ | OBRA MÉXICO TOLUCA |  | **`MHL755A`** | LEVET | **$500.00** |
| 4 | Tabla 1 (J.D.J.) | 2026-07-24 | BRYAN GABRIEL CHAVEZ ALVAREZ | TRANSPORTES FLOTILLA | CHEVROLET TORNADO | **`NUZ948C`** | LEVET | **$200.00** |
| 5 | Tabla 1 (J.D.J.) | 2026-07-25 | BRYAN GABRIEL CHAVEZ ALVAREZ | TRANSPORTES FLOTILLA | CHEVROLET TORNADO | **`NUZ948C`** | LEVET | **$200.00** |
| 6 | Tabla 1 (J.D.J.) | 2026-07-20 | BRYAN GABRIEL CHAVEZ ALVAREZ | TRANSPORTES FLOTILLA | MOTORES LOWBOY | **`S/P`** | LEVET | **$500.00** |
| 7 | Tabla 1 (J.D.J.) | 2026-07-25 | BRYAN GABRIEL CHAVEZ ALVAREZ | TRANSPORTES FLOTILLA | MOTORES LOWBOY | **`S/P`** | LEVET | **$500.00** |
| 8 | Tabla 1 (J.D.J.) | 2026-07-21 | JOSÉ CABELLO /JACK | ESTIMACIONES /PLANTA PEGASO |  | **`LHB176D`** | LEVET | **$850.00** |
| 9 | Tabla 1 (J.D.J.) | 2026-07-25 | JOSÉ CABELLO /JACK | ESTIMACIONES /PLANTA PEGASO |  | **`LHB176D`** | LEVET | **$650.00** |
| 10 | Tabla 1 (J.D.J.) | 2026-07-23 | SAMUEL ORTEGA SILVA | CORPORATIVO | MITSUBISHI L200 | **`NZT266B`** | MOBILE | **$1,000.00** |
| 11 | Tabla 1 (J.D.J.) | 2026-07-20 | HENRY | CORPORATIVO |  | **`S/P`** | LEVET | **$15,565.22** |
| 12 | Tabla 1 (J.D.J.) | 2026-07-20 | HENRY | CORPORATIVO |  | **`S/P`** | MOBILE | **$5,700.00** |
| 13 | Tabla 1 (J.D.J.) | 2026-07-21 | HENRY | CORPORATIVO |  | **`S/P`** | LEVET | **$3,508.20** |
| 14 | Tabla 1 (J.D.J.) | 2026-07-22 | HENRY | CORPORATIVO |  | **`S/P`** | LEVET | **$7,653.77** |
| 15 | Tabla 1 (J.D.J.) | 2026-07-22 | HENRY | CORPORATIVO |  | **`S/P`** | MOBILE | **$1,800.00** |
| 16 | Tabla 1 (J.D.J.) | 2026-07-23 | HENRY | CORPORATIVO |  | **`S/P`** | LEVET | **$3,299.00** |
| 17 | Tabla 1 (J.D.J.) | 2026-07-23 | HENRY | CORPORATIVO |  | **`S/P`** | MOBILE | **$2,500.00** |
| 18 | Tabla 1 (J.D.J.) | 2026-07-24 | HENRY | CORPORATIVO |  | **`S/P`** | LEVET | **$700.00** |
| 19 | Tabla 1 (J.D.J.) | 2026-07-24 | HENRY | CORPORATIVO |  | **`S/P`** | MOBILE | **$2,000.00** |
| 20 | Tabla 1 (J.D.J.) | 2026-07-25 | HENRY | CORPORATIVO |  | **`S/P`** | LEVET | **$4,272.74** |
| 21 | Tabla 2 (TRD SAN MIGUEL) | 2026-07-13 | CARLOS REYES TRUJANO | MINA TABERNILLAS | TOYOTA TACOMA | **`33K849`** | LEVET | **$2,149.96** |
| 22 | Tabla 2 (TRD SAN MIGUEL) | 2026-07-16 | CARLOS REYES TRUJANO | MINA TABERNILLAS | TOYOTA TACOMA | **`33K849`** | LEVET | **$386,067.00** |
| 23 | Tabla 2 (TRD SAN MIGUEL) | 2026-07-15 | LAZARO PINAL RIOS | MINA TABERNILLAS | MITSUBISHI L200 | **`MHL757A`** | LEVET | **$1,500.00** |
| 24 | Tabla 2 (TRD SAN MIGUEL) | 2026-07-13 | ABNER OSORIO BARTOLO | MINA ZUMPAHUACAN | MITSUBISHI L200 | **`NYZ828C`** | LEVET | **$1,500.00** |
| 25 | Tabla 2 (TRD SAN MIGUEL) | 2026-07-13 | ISAAC GONZALEZ GONZALEZ | MINA ZUMPAHUACAN | MITSUBISHI L200 | **`NYZ839C`** | LEVET | **$1,500.28** |
| 26 | Tabla 2 (TRD SAN MIGUEL) | 2026-07-14 | JESUS MARIN GARCIA | MINA CUAJOMAC | CHEVORLET | **`PCU8771`** | LEVET | **$1,300.06** |
| 27 | Tabla 2 (TRD SAN MIGUEL) | 2026-07-13 | MINA TABERNILLAS | MINA CUAJOMAC |  | **`S/P`** | LEVET | **$5,150.24** |
| 28 | Tabla 2 (TRD SAN MIGUEL) | 2026-07-14 | MINA TABERNILLAS | MINA CUAJOMAC |  | **`S/P`** | LEVET | **$2,650.30** |
| 29 | Tabla 2 (TRD SAN MIGUEL) | 2026-07-15 | MINA TABERNILLAS | MINA CUAJOMAC |  | **`S/P`** | LEVET | **$1,500.00** |
| 30 | Tabla 2 (TRD SAN MIGUEL) | 2026-07-16 | MINA TABERNILLAS | MINA CUAJOMAC |  | **`S/P`** | LEVET | **$386,067.00** |

---

### 🟢 2. Cargas del Excel (Tablas 1 y 2) que SÍ COINCIDEN con la Base de Datos
| # | Tabla Excel | Fecha | Responsable (Excel ➡️ BD) | Placa (Excel ➡️ BD) | Importe Excel ($) | Importe BD ($) | Folio BD |
|--:|:------------|:------|:--------------------------|:--------------------|------------------:|---------------:|:---------|
| 1 | Tabla 1 (J.D.J.) | 2026-07-22 | ING. ANTONIO IBAÑEZ ➡️ **ING. ANTONIO IBAÑEZ** | `LHB188D` ➡️ **`LHB188D`** | **$1,984.99** | **$1,984.93** | `GAS-ADM-30-017` |
| 2 | Tabla 1 (J.D.J.) | 2026-07-21 | JUAN CARLOS NAZAR CHAVEZ ➡️ **JUAN CARLOS NAZAR** | `PCW9238` ➡️ **`PCW9391`** | **$1,158.20** | **$1,499.98** | `GAS-ADM-30-002` |
| 3 | Tabla 1 (J.D.J.) | 2026-07-23 | JUAN CARLOS NAZAR CHAVEZ ➡️ **None** | `PCW9238` ➡️ **`PCW9238`** | **$350.00** | **$349.99** | `GAS-XX-30-003` |
| 4 | Tabla 1 (J.D.J.) | 2026-07-24 | JUAN CARLOS NAZAR CHAVEZ ➡️ **None** | `PCW9238` ➡️ **`MOTORES LOWBOY`** | **$500.00** | **$499.92** | `GAS-XX-30-031` |
| 5 | Tabla 1 (J.D.J.) | 2026-07-21 | EDGAR VELAZQUEZ ESQUIVEL ➡️ **ABNER OSORIO BARTOLO** | `9391` ➡️ **`MITSUBISHI L200 NYZ828C`** | **$1,500.00** | **$1,500.00** | `GAS-ADM-30-011` |
| 6 | Tabla 1 (J.D.J.) | 2026-07-20 | DIEGO CARREOLA ➡️ **ISAAC GONZALEZ GONZALEZ** | `NYZ829C` ➡️ **`NYZ839C`** | **$1,500.00** | **$1,498.15** | `GAS-XX-30-036` |
| 7 | Tabla 1 (J.D.J.) | 2026-07-25 | TOMAS ARANDA PROSPERO ➡️ **Cristian Reyes** | `LF05470` ➡️ **`LH49730`** | **$1,500.00** | **$1,500.20** | `GAS-MT-30-001` |
| 8 | Tabla 1 (J.D.J.) | 2026-07-20 | JAVIER PEREZ DÍAZ ➡️ **JAVIER PEREZ DÍAZ** | `MHL758A` ➡️ **`MHL758A`** | **$1,510.00** | **$1,510.05** | `GAS-MT-30-027` |
| 9 | Tabla 1 (J.D.J.) | 2026-07-22 | JAVIER PEREZ DÍAZ ➡️ **JAVIER PEREZ DÍAZ** | `MHL758A` ➡️ **`MHL758A`** | **$1,084.02** | **$1,083.84** | `GAS-MT-30-024` |
| 10 | Tabla 1 (J.D.J.) | 2026-07-22 | JAVIER PEREZ DÍAZ ➡️ **None** | `MHL755A` ➡️ **`MHL755A`** | **$860.27** | **$860.21** | `GAS-ADM-30-015` |
| 11 | Tabla 1 (J.D.J.) | 2026-07-22 | JAVIER PEREZ DÍAZ ➡️ **CARLOS ALARCON** | `` ➡️ **`EQUIPO MENOR`** | **$300.00** | **$299.86** | `GAS-MT-30-016` |
| 12 | Tabla 1 (J.D.J.) | 2026-07-20 | CRISTIAN REYES GAMORA ➡️ **CRISTIAN REYES GAMORA** | `LH49730` ➡️ **`LH49730`** | **$2,500.00** | **$2,499.94** | `GAS-MT-30-026` |
| 13 | Tabla 1 (J.D.J.) | 2026-07-23 | CRISTIAN REYES GAMORA ➡️ **LAZARO PINAL RIOS** | `LH49730` ➡️ **`MHL757A`** | **$1,500.00** | **$1,499.98** | `GAS-ADM-30-022` |
| 14 | Tabla 1 (J.D.J.) | 2026-07-20 | APOLINAR REYES BOLAINA ➡️ **APOLINAR REYES BOLAINA** | `NYZ971C` ➡️ **`NYZ971C`** | **$1,397.00** | **$1,410.02** | `GAS-L3M-30-035` |
| 15 | Tabla 1 (J.D.J.) | 2026-07-23 | APOLINAR REYES BOLAINA ➡️ **APOLINAR REYES BOLAINA** | `NYZ971C` ➡️ **`NYZ971C`** | **$1,102.00** | **$1,101.92** | `GAS-XX-30-004` |
| 16 | Tabla 1 (J.D.J.) | 2026-07-20 | APOLINAR REYES BOLAINA ➡️ **None** | `` ➡️ **`EQUIPO MENOR`** | **$1,000.00** | **$999.84** | `GAS-L3M-30-028` |
| 17 | Tabla 1 (J.D.J.) | 2026-07-20 | LEONCIO MARTINEZ PASCACIO ➡️ **LEONCIO MARTINEZ PASCACIO** | `NYZ790C` ➡️ **`NYZ790C`** | **$1,487.00** | **$1,487.62** | `GAS-L3M-30-033` |
| 18 | Tabla 1 (J.D.J.) | 2026-07-20 | CARMELO ALVAREZ ANICETO ➡️ **CARMELO ALVAREZ ANICETO** | `LH49746` ➡️ **`LH49746`** | **$3,000.00** | **$2,999.96** | `GAS-L3M-30-025` |
| 19 | Tabla 1 (J.D.J.) | 2026-07-23 | CARMELO ALVAREZ ANICETO ➡️ **CARMELO ALVAREZ ANICETO** | `LH49746` ➡️ **`LH49746`** | **$1,000.00** | **$999.84** | `GAS-XX-30-006` |
| 20 | Tabla 1 (J.D.J.) | 2026-07-20 | DIEGO FERNANDEZ SANTIAGO ➡️ **DIEGO FERNANDEZ SANTIAGO** | `PBT1229` ➡️ **`PBT1229`** | **$1,262.22** | **$1,262.15** | `GAS-L3M-30-029` |
| 21 | Tabla 1 (J.D.J.) | 2026-07-23 | DIEGO FERNANDEZ SANTIAGO ➡️ **DIEGO FERNANDEZ SANTIAGO** | `PBT1229` ➡️ **`PBT1229`** | **$847.00** | **$846.93** | `GAS-ADM-30-005` |
| 22 | Tabla 1 (J.D.J.) | 2026-07-22 | DAMIAN ANTONIO PUINI ➡️ **DAMIAN ANTONIO PUINI** | `PCU7482` ➡️ **`PCU7482`** | **$1,000.00** | **$999.98** | `GAS-PAH-30-018` |
| 23 | Tabla 1 (J.D.J.) | 2026-07-24 | DAMIAN ANTONIO PUINI ➡️ **DAMIAN ANTONIO PUINI** | `PCU7482` ➡️ **`PCU7482`** | **$500.00** | **$494.25** | `GAS-ADM-30-008` |
| 24 | Tabla 1 (J.D.J.) | 2026-07-20 | CLEMENTE SANABRIA ➡️ **CLEMENTE SANABRIA** | `LHB184D` ➡️ **`RAM 1200`** | **$2,109.00** | **$2,109.96** | `GAS-XX-30-032` |
| 25 | Tabla 1 (J.D.J.) | 2026-07-22 | CLEMENTE SANABRIA ➡️ **CLEMENTE SANABRIA** | `LHB184D` ➡️ **`LHB184D`** | **$1,924.49** | **$1,924.41** | `GAS-XX-30-019` |
| 26 | Tabla 1 (J.D.J.) | 2026-07-20 | BRYAN GABRIEL CHAVEZ ALVAREZ ➡️ **SAMUEL ORTEGA SILVA** | `NUZ948C` ➡️ **`NZT266B`** | **$1,000.00** | **$999.98** | `GAS-ADM-30-009` |
| 27 | Tabla 1 (J.D.J.) | 2026-07-20 | ROBERTO ORTEGA ➡️ **ROBERTO ORTEGA** | `MNX601B` ➡️ **`MNX601B`** | **$800.00** | **$800.01** | `GAS-XX-30-034` |
| 28 | Tabla 1 (J.D.J.) | 2026-07-22 | PAOLA JARAMILLO ➡️ **Paola Jaramillo** | `` ➡️ **`LLY085A`** | **$700.00** | **$699.98** | `GAS-ADM-30-021` |
| 29 | Tabla 1 (J.D.J.) | 2026-07-20 | SAMUEL ORTEGA SILVA ➡️ **SAMUEL ORTEGA SILVA** | `NZT266B` ➡️ **`NZT266B`** | **$1,200.00** | **$1,200.02** | `GAS-ADM-30-012` |
| 30 | Tabla 1 (J.D.J.) | 2026-07-22 | SAMUEL ORTEGA SILVA ➡️ **SAMUEL ORTEGA SILVA** | `NZT266B` ➡️ **`NZT266B`** | **$800.00** | **$766.13** | `GAS-XX-30-023` |
| 31 | Tabla 1 (J.D.J.) | 2026-07-24 | CRISTOBAL SILVA ➡️ **None** | `LKC794D` ➡️ **`LKC794D`** | **$1,500.00** | **$1,499.96** | `GAS-XX-30-007` |
| 32 | Tabla 1 (J.D.J.) | 2026-07-22 | HENRY ➡️ **ALBERTO HERNANDEZ DE JESUS** | `NXP4918` ➡️ **`NXP4918`** | **$800.00** | **$800.01** | `GAS-ADM-30-020` |
| 33 | Tabla 2 (TRD SAN MIGUEL) | 2026-07-14 | ARMANDO COLIN MORENO ➡️ **None** | `PAT8298` ➡️ **`LHB180D`** | **$1,121.34** | **$1,121.15** | `GAS-ADM-30-014` |
| 34 | Tabla 2 (TRD SAN MIGUEL) | 2026-07-14 | ARMANDO COLIN MORENO ➡️ **None** | `` ➡️ **`EQUIPO MENOR`** | **$228.90** | **$228.90** | `GAS-XX-30-013` |