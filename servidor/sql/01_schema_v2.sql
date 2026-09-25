-- ============================================================
-- Proyecto Fénix v2 — Esquema de Base de Datos
-- Grupo Trujano
-- PostgreSQL 15
-- Archivo: 01_schema_v2.sql
-- Se ejecuta automáticamente al crear la BD por primera vez
-- ============================================================

-- Extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "pgcrypto";   -- para gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS "pg_trgm";    -- búsqueda de texto difuso

-- ============================================================
-- 1. USUARIOS Y ROLES
-- ============================================================

CREATE TYPE rol_usuario AS ENUM (
    'operador_tanque',
    'chofer_pipa',
    'ingeniero',
    'directivo',
    'admin'
);

CREATE TABLE fenix_usuarios (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre          VARCHAR(150) NOT NULL,
    email           VARCHAR(200) UNIQUE NOT NULL,
    password_hash   TEXT NOT NULL,            -- bcrypt
    rol             rol_usuario NOT NULL,
    activo          BOOLEAN DEFAULT TRUE,
    creado_en       TIMESTAMPTZ DEFAULT NOW(),
    actualizado_en  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE fenix_sesiones (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id      UUID NOT NULL REFERENCES fenix_usuarios(id) ON DELETE CASCADE,
    token           TEXT UNIQUE NOT NULL,
    expira_en       TIMESTAMPTZ NOT NULL,
    creado_en       TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_sesiones_token ON fenix_sesiones(token);

-- ============================================================
-- 2. CATÁLOGOS
-- ============================================================

-- Tipos de obra
CREATE TYPE tipo_obra AS ENUM ('obra', 'planta_asfalto', 'otro');

CREATE TABLE fenix_obras (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre          VARCHAR(200) NOT NULL,
    iniciales       VARCHAR(10) UNIQUE NOT NULL,  -- MT, LT, CL, PAP, etc.
    tipo            tipo_obra DEFAULT 'obra',
    responsable_id  UUID REFERENCES fenix_usuarios(id),
    activa          BOOLEAN DEFAULT TRUE,
    creado_en       TIMESTAMPTZ DEFAULT NOW()
);

-- Tipo de medida del equipo para rendimiento
CREATE TYPE unidad_rendimiento AS ENUM ('L/h', 'km/L');

CREATE TABLE fenix_equipos (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    economico               VARCHAR(20) UNIQUE NOT NULL,  -- RT-01, VG-01, etc.
    tipo_unidad             VARCHAR(100) NOT NULL,         -- Retroexcavadora, Pavimentadora, etc.
    marca                   VARCHAR(100),
    modelo                  VARCHAR(100),
    anio_fabricacion        INT,
    num_serie               VARCHAR(100),
    dueno                   VARCHAR(200),                  -- empresa dueña del equipo
    rendimiento_nuevo       DECIMAL(8,2),                  -- L/h o km/L cuando era nuevo
    unidad_medida           unidad_rendimiento DEFAULT 'L/h',
    obra_asignada_id        UUID REFERENCES fenix_obras(id),
    operador_nombre         VARCHAR(200),
    activo                  BOOLEAN DEFAULT TRUE,
    creado_en               TIMESTAMPTZ DEFAULT NOW(),
    actualizado_en          TIMESTAMPTZ DEFAULT NOW(),
    -- Rendimiento ajustado calculado automáticamente
    GENERATED ALWAYS AS (
        -- No se puede usar GENERATED con lógica compleja en PG;
        -- se usará una VISTA para el rendimiento ajustado
        NULL
    ) STORED
);

-- Quitar la columna generada inválida y usar una vista:
ALTER TABLE fenix_equipos DROP COLUMN IF EXISTS rendimiento_ajustado;

-- Vista de rendimiento ajustado (fórmula del Excel Maestro: desgaste 1% anual)
CREATE OR REPLACE VIEW v_equipos_rendimiento AS
SELECT
    e.*,
    (EXTRACT(YEAR FROM NOW()) - COALESCE(e.anio_fabricacion, EXTRACT(YEAR FROM NOW()) - 10)) AS edad_anios,
    CASE
        WHEN e.unidad_medida = 'L/h'
            THEN ROUND(e.rendimiento_nuevo * (1 + (
                (EXTRACT(YEAR FROM NOW()) - COALESCE(e.anio_fabricacion, EXTRACT(YEAR FROM NOW()) - 10)) * 0.01
            )), 2)
        WHEN e.unidad_medida = 'km/L'
            THEN ROUND(e.rendimiento_nuevo / (1 + (
                (EXTRACT(YEAR FROM NOW()) - COALESCE(e.anio_fabricacion, EXTRACT(YEAR FROM NOW()) - 10)) * 0.01
            )), 2)
    END AS rendimiento_ajustado
FROM fenix_equipos e;

-- Gasolineras del grupo
CREATE TABLE fenix_gasolineras (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre      VARCHAR(200) NOT NULL,
    ubicacion   VARCHAR(300),
    email       VARCHAR(200),             -- para enviarles autorizaciones
    activa      BOOLEAN DEFAULT TRUE,
    creado_en   TIMESTAMPTZ DEFAULT NOW()
);

-- Tanques fijos de diésel
CREATE TABLE fenix_tanques (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre          VARCHAR(200) NOT NULL,   -- "Tanque Pegaso"
    capacidad_lts   DECIMAL(10,2),           -- 20000
    obra_id         UUID REFERENCES fenix_obras(id),
    operador_id     UUID REFERENCES fenix_usuarios(id),
    activo          BOOLEAN DEFAULT TRUE,
    creado_en       TIMESTAMPTZ DEFAULT NOW()
);

-- Pipas / Marimbas
CREATE TABLE fenix_pipas (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre          VARCHAR(200) NOT NULL,   -- "Marimba M-01"
    capacidad_lts   DECIMAL(10,2),
    placas          VARCHAR(20),
    chofer_id       UUID REFERENCES fenix_usuarios(id),
    activa          BOOLEAN DEFAULT TRUE,
    creado_en       TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- 3. MOVIMIENTOS (CONCILIACIÓN EN PAREJA)
-- ============================================================

CREATE TYPE lado_movimiento AS ENUM ('EMISOR', 'RECEPTOR');
CREATE TYPE tipo_punto AS ENUM ('gasolinera', 'tanque', 'pipa', 'obra', 'planta', 'directo');
CREATE TYPE estado_conciliacion AS ENUM (
    'huerfano',        -- solo 1 lado reportado
    'pareado',         -- ambos lados reportados
    'conciliado',      -- litros coinciden dentro del umbral
    'discrepancia',    -- litros difieren más del umbral
    'merma_aceptada'   -- diferencia justificada (contexto del agente IA)
);

CREATE TABLE fenix_movimientos (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    -- Enlace entre el registro del emisor y el del receptor
    par_id              UUID NOT NULL,               -- mismo UUID para los 2 registros de la misma transacción
    lado                lado_movimiento NOT NULL,     -- EMISOR o RECEPTOR

    -- Quién registra
    usuario_id          UUID NOT NULL REFERENCES fenix_usuarios(id),
    fecha               DATE NOT NULL,
    hora                TIME NOT NULL,

    -- Folio con patrón {OBRA}-{SEMANA}-{CONSECUTIVO}
    folio_ticket        VARCHAR(30),

    -- Origen del movimiento
    origen_tipo         tipo_punto NOT NULL,
    origen_tanque_id    UUID REFERENCES fenix_tanques(id),
    origen_pipa_id      UUID REFERENCES fenix_pipas(id),
    origen_gasolinera_id UUID REFERENCES fenix_gasolineras(id),
    origen_obra_id      UUID REFERENCES fenix_obras(id),

    -- Destino del movimiento
    destino_tipo        tipo_punto NOT NULL,
    destino_tanque_id   UUID REFERENCES fenix_tanques(id),
    destino_pipa_id     UUID REFERENCES fenix_pipas(id),
    destino_obra_id     UUID REFERENCES fenix_obras(id),
    destino_equipo_id   UUID REFERENCES fenix_equipos(id),

    -- Datos del movimiento
    litros              DECIMAL(10,2) NOT NULL,
    costo_por_litro     DECIMAL(8,2),
    importe             DECIMAL(12,2) GENERATED ALWAYS AS (litros * costo_por_litro) STORED,

    -- Datos del receptor en campo
    operador_nombre     VARCHAR(200),
    
    -- Conciliación
    estado_conciliacion estado_conciliacion DEFAULT 'huerfano',
    diferencia_litros   DECIMAL(10,2),               -- calculado al conciliar
    contexto_ia         TEXT,                        -- clasificación del Agente Conciliador
    observaciones       TEXT,

    -- Sincronización offline
    sync_pendiente      BOOLEAN DEFAULT FALSE,
    dispositivo_id      VARCHAR(100),                -- ID del dispositivo que lo generó offline
    creado_en           TIMESTAMPTZ DEFAULT NOW(),
    actualizado_en      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_mov_par_id         ON fenix_movimientos(par_id);
CREATE INDEX idx_mov_fecha          ON fenix_movimientos(fecha);
CREATE INDEX idx_mov_usuario        ON fenix_movimientos(usuario_id);
CREATE INDEX idx_mov_estado         ON fenix_movimientos(estado_conciliacion);
CREATE INDEX idx_mov_sync           ON fenix_movimientos(sync_pendiente) WHERE sync_pendiente = TRUE;

-- ============================================================
-- 4. HORAS DE MAQUINARIA (Registro Diario)
-- ============================================================

CREATE TABLE fenix_registro_diario_maquinaria (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fecha           DATE NOT NULL,
    equipo_id       UUID NOT NULL REFERENCES fenix_equipos(id),
    obra_id         UUID NOT NULL REFERENCES fenix_obras(id),
    usuario_id      UUID NOT NULL REFERENCES fenix_usuarios(id),
    horas_trabajadas DECIMAL(5,2) DEFAULT 0,
    kilometraje     DECIMAL(10,2) DEFAULT 0,
    observaciones   TEXT,
    creado_en       TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (fecha, equipo_id, obra_id)
);

-- ============================================================
-- 4.1 EVIDENCIAS FOTOGRÁFICAS (Tickets, Firmas, Odómetros)
-- ============================================================

CREATE TYPE tipo_evidencia AS ENUM ('ticket_gasolinera', 'odometro', 'firma', 'foto_maquina', 'otro');

CREATE TABLE fenix_evidencias (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tabla_relacionada VARCHAR(100) NOT NULL,    -- ej. 'fenix_movimientos', 'fenix_registro_diario_maquinaria'
    registro_id       UUID NOT NULL,            -- el ID del registro en esa tabla
    url_archivo       TEXT NOT NULL,            -- URL en Cloud Storage (ej. bucket local o S3)
    tipo_evidencia    tipo_evidencia DEFAULT 'otro',
    subido_por        UUID REFERENCES fenix_usuarios(id),
    creado_en         TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_evidencias_relacion ON fenix_evidencias(tabla_relacionada, registro_id);

-- ============================================================
-- 5. FACTURAS DE GASOLINERA
-- ============================================================

CREATE TYPE estado_factura AS ENUM (
    'recibida',        -- llegó por email
    'procesada',       -- el Agente Lector extrajo los datos
    'cruzada',         -- coincide con un movimiento
    'discrepancia',    -- no coincide
    'ignorada'
);

CREATE TABLE fenix_facturas_gasolinera (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    gasolinera_id       UUID REFERENCES fenix_gasolineras(id),
    fecha_factura       DATE,
    folio_factura       VARCHAR(100),
    litros              DECIMAL(10,2),
    importe_total       DECIMAL(12,2),
    tipo_combustible    VARCHAR(50) DEFAULT 'Diésel',
    archivo_url         TEXT,               -- ruta/URL del PDF o XML
    estado              estado_factura DEFAULT 'recibida',
    movimiento_id       UUID REFERENCES fenix_movimientos(id),  -- cruce exitoso
    diferencia_litros   DECIMAL(10,2),
    datos_extraidos_ia  JSONB,              -- lo que extrajo el Agente Lector
    creado_en           TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- 6. SOLICITUDES Y AUTORIZACIONES DE DIÉSEL
-- ============================================================

CREATE TYPE estado_solicitud AS ENUM (
    'borrador',
    'enviada',
    'en_revision',
    'autorizada',
    'rechazada',
    'enviada_gasolinera'
);

-- Cabecera de solicitud semanal
CREATE TABLE fenix_solicitudes_semanales (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    semana_inicio   DATE NOT NULL,          -- Lunes de la semana solicitada
    obra_id         UUID NOT NULL REFERENCES fenix_obras(id),
    solicitante_id  UUID NOT NULL REFERENCES fenix_usuarios(id),
    estado          estado_solicitud DEFAULT 'borrador',
    observaciones   TEXT,
    creado_en       TIMESTAMPTZ DEFAULT NOW(),
    actualizado_en  TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (semana_inicio, obra_id)
);

-- Detalle por equipo
CREATE TABLE fenix_solicitud_equipos (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    solicitud_id        UUID NOT NULL REFERENCES fenix_solicitudes_semanales(id) ON DELETE CASCADE,
    equipo_id           UUID NOT NULL REFERENCES fenix_equipos(id),
    actividad_esperada  TEXT,
    creado_en           TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(solicitud_id, equipo_id)
);

-- Detalle atómico por día (Solicitado y Autorizado)
CREATE TABLE fenix_solicitud_dia (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    solicitud_equipo_id UUID NOT NULL REFERENCES fenix_solicitud_equipos(id) ON DELETE CASCADE,
    fecha               DATE NOT NULL,
    litros_solicitados  DECIMAL(8,2) DEFAULT 0,
    litros_autorizados  DECIMAL(8,2),  -- Modificado por el directivo
    creado_en           TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(solicitud_equipo_id, fecha)
);

-- Registro de autorización por directivo (el "pase" enviado a la gasolinera)
CREATE TABLE fenix_autorizaciones (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    solicitud_id        UUID NOT NULL REFERENCES fenix_solicitudes_semanales(id),
    directivo_id        UUID NOT NULL REFERENCES fenix_usuarios(id),
    -- Punto de carga autorizado (de dónde carga físicamente)
    punto_carga_tipo    tipo_punto,
    tanque_id           UUID REFERENCES fenix_tanques(id),
    pipa_id             UUID REFERENCES fenix_pipas(id),
    gasolinera_id       UUID REFERENCES fenix_gasolineras(id),
    -- Estado del envío a gasolinera
    enviado_gasolinera  BOOLEAN DEFAULT FALSE,
    fecha_envio         TIMESTAMPTZ,
    email_destino       VARCHAR(200),       -- email de la gasolinera
    pdf_url             TEXT,               -- URL del PDF generado
    notas_directivo     TEXT,
    creado_en           TIMESTAMPTZ DEFAULT NOW()
);

-- Detalle atómico de los topes diarios autorizados globalmente para ese pase
CREATE TABLE fenix_autorizacion_dia (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    autorizacion_id     UUID NOT NULL REFERENCES fenix_autorizaciones(id) ON DELETE CASCADE,
    fecha               DATE NOT NULL,
    tope_litros         DECIMAL(10,2) NOT NULL,
    creado_en           TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(autorizacion_id, fecha)
);

-- ============================================================
-- 7. CONCILIACIÓN — RESULTADOS
-- ============================================================

CREATE TYPE tipo_cruce AS ENUM ('cruce_1', 'cruce_2', 'cruce_3');

CREATE TABLE fenix_conciliacion_resultado (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    par_id              UUID NOT NULL,
    tipo_cruce          tipo_cruce NOT NULL,
    semana_inicio       DATE,
    estado              estado_conciliacion NOT NULL,
    litros_emisor       DECIMAL(10,2),
    litros_receptor     DECIMAL(10,2),
    diferencia          DECIMAL(10,2),
    clasificacion_ia    TEXT,              -- contexto del Agente Conciliador
    alerta_enviada      BOOLEAN DEFAULT FALSE,
    revisado_por        UUID REFERENCES fenix_usuarios(id),
    revisado_en         TIMESTAMPTZ,
    creado_en           TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_conciliacion_par    ON fenix_conciliacion_resultado(par_id);
CREATE INDEX idx_conciliacion_semana ON fenix_conciliacion_resultado(semana_inicio);
CREATE INDEX idx_conciliacion_estado ON fenix_conciliacion_resultado(estado);

-- ============================================================
-- 8. COLA DE SINCRONIZACIÓN OFFLINE
-- ============================================================

CREATE TYPE estado_sync AS ENUM ('pendiente', 'procesando', 'completado', 'error');

CREATE TABLE fenix_sync_queue (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dispositivo_id  VARCHAR(100) NOT NULL,
    usuario_id      UUID REFERENCES fenix_usuarios(id),
    tabla_destino   VARCHAR(100) NOT NULL,  -- 'fenix_movimientos', 'fenix_horas_maquinaria', etc.
    payload         JSONB NOT NULL,          -- el registro completo a insertar/actualizar
    estado          estado_sync DEFAULT 'pendiente',
    reintentos      INT DEFAULT 0,
    error_msg       TEXT,
    creado_en       TIMESTAMPTZ DEFAULT NOW(),
    procesado_en    TIMESTAMPTZ
);

CREATE INDEX idx_sync_estado ON fenix_sync_queue(estado) WHERE estado = 'pendiente';

-- ============================================================
-- 9. AUDITORÍA
-- ============================================================

CREATE TABLE fenix_audit_log (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id  UUID REFERENCES fenix_usuarios(id),
    accion      VARCHAR(100) NOT NULL,     -- 'INSERT_MOVIMIENTO', 'AUTORIZAR_SOLICITUD', etc.
    tabla       VARCHAR(100),
    registro_id UUID,
    datos_antes JSONB,
    datos_despues JSONB,
    ip_origen   VARCHAR(50),
    creado_en   TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_audit_usuario ON fenix_audit_log(usuario_id);
CREATE INDEX idx_audit_tabla   ON fenix_audit_log(tabla, registro_id);

-- ============================================================
-- 10. WHATSAPP / IA INBOX
-- ============================================================

CREATE TABLE fenix_whatsapp_inbox (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    numero          VARCHAR(30) NOT NULL,
    mensaje         TEXT,
    media_url       TEXT,
    procesado       BOOLEAN DEFAULT FALSE,
    respuesta       TEXT,
    creado_en       TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- FIN DEL ESQUEMA v2
-- ============================================================
