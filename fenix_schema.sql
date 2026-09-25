-- ==========================================
-- SISTEMA FÉNIX — ESQUEMA SQLite v1.0
-- Combustibles (Diésel + Gasolina) + Acarreos
-- Cumple 1NF: atomicidad, sin grupos repetitivos
-- ==========================================

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

-- ====================
-- CATÁLOGOS BASE
-- ====================

-- 1. Obras / Proyectos
CREATE TABLE IF NOT EXISTS fenix_obras (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo      TEXT    UNIQUE NOT NULL,
    nombre      TEXT    NOT NULL,
    activa      INTEGER NOT NULL DEFAULT 1,  -- 1=activa, 0=cerrada
    created_at  TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
);

-- 2. Sindicatos (para Acarreos)
CREATE TABLE IF NOT EXISTS fenix_sindicatos (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre      TEXT    UNIQUE NOT NULL,
    rfc         TEXT,
    contacto    TEXT,
    activo      INTEGER NOT NULL DEFAULT 1,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
);

-- 3. Equipos y Unidades
--    tipo_equipo:      Maquinaria, Camioneta, Pipa, etc.
--    tipo_combustible: Diesel, Gasolina
--    tipo_rendimiento: horas, kilometros
CREATE TABLE IF NOT EXISTS fenix_equipos (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_economico   TEXT    UNIQUE NOT NULL,  -- Ej. PR-01, VOG-03, LD57526
    descripcion        TEXT    NOT NULL,
    tipo_equipo        TEXT    NOT NULL,
    tipo_combustible   TEXT    NOT NULL CHECK (tipo_combustible IN ('Diesel','Gasolina')),
    tipo_rendimiento   TEXT    NOT NULL CHECK (tipo_rendimiento IN ('horas','kilometros','ninguno')),
    rendimiento_base   NUMERIC,                 -- L/h o km/L según fabricante (del inventario)
    obra_id            INTEGER REFERENCES fenix_obras(id) ON DELETE SET NULL,  -- Obra donde está asignado
    activo             INTEGER NOT NULL DEFAULT 1,
    created_at         TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
);

-- 4. Contenedores de Combustible (Intermediarios físicos)
--    tipo: Tanque, Marimba, Bidón, Pipa
CREATE TABLE IF NOT EXISTS fenix_contenedores (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre           TEXT    UNIQUE NOT NULL,  -- Ej. 'Tanque Pegaso', 'Marimba M-01', 'Bidón Lerma'
    tipo             TEXT    NOT NULL CHECK (tipo IN ('Tanque','Marimba','Bidon','Pipa')),
    capacidad_litros NUMERIC,
    obra_id          INTEGER REFERENCES fenix_obras(id) ON DELETE SET NULL,
    activo           INTEGER NOT NULL DEFAULT 1,
    created_at       TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
);

-- 5. Tarifas de Acarreos (Motor de Precios)
CREATE TABLE IF NOT EXISTS fenix_tarifas (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    sindicato_id    INTEGER NOT NULL REFERENCES fenix_sindicatos(id) ON DELETE CASCADE,
    obra_id         INTEGER REFERENCES fenix_obras(id) ON DELETE SET NULL,
    categoria       TEXT    NOT NULL,  -- Ej. 'Mezcla Asfaltica', 'Fresado', 'Material'
    costo_unitario  NUMERIC NOT NULL CHECK (costo_unitario >= 0),
    unidad_medida   TEXT    NOT NULL DEFAULT 'viaje',  -- viaje, m3, ton
    vigente         INTEGER NOT NULL DEFAULT 1,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
    UNIQUE (sindicato_id, obra_id, categoria)
);

-- ====================
-- FACTURAS DE GASOLINERAS (Comprobantes de Compra)
-- ====================

-- 6. Facturas de Combustible
--    Cada que una gasolinera entrega combustible, llega su factura/ticket.
--    Esta tabla es el ÚNICO lugar donde se registran los montos a pagar al proveedor.
CREATE TABLE IF NOT EXISTS fenix_facturas_combustible (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    folio_factura     TEXT    NOT NULL,
    proveedor         TEXT    NOT NULL,  -- Ej. 'Gasolinera Huixquilucan', 'Estación Lerma'
    tipo_combustible  TEXT    NOT NULL CHECK (tipo_combustible IN ('Diesel','Gasolina')),
    fecha_emision     TEXT    NOT NULL,
    litros_amparados  NUMERIC NOT NULL CHECK (litros_amparados > 0),
    precio_unitario   NUMERIC NOT NULL CHECK (precio_unitario > 0),
    subtotal          NUMERIC NOT NULL,
    iva               NUMERIC NOT NULL DEFAULT 0,
    importe_total     NUMERIC NOT NULL,
    estatus_pago      TEXT    NOT NULL DEFAULT 'Pendiente' CHECK (estatus_pago IN ('Pendiente','Pagada','Cancelada')),
    fecha_pago        TEXT,
    observaciones     TEXT,
    imagen_url        TEXT,  -- Ruta a la foto del ticket/factura
    created_at        TEXT   NOT NULL DEFAULT (datetime('now','localtime'))
);

-- ====================
-- MOVIMIENTOS DE COMBUSTIBLE (Sistema de Partida Doble)
-- ====================

-- 7. Movimientos de Combustible
--    CADA litro que entra o sale queda registrado aquí con su Origen y Destino.
--    Esto permite la conciliación completa:
--      COMPRA:    Gasolinera       → Marimba / Tanque / Bidón
--      TRASPASO:  Tanque           → Marimba / Bidón
--      CONSUMO:   Marimba/Bidón    → Equipo/Unidad (final)
--
--    Para Gasolina la ruta es: Gasolinera → Bidón → Unidad
--    Para Diésel:              Gasolinera → Marimba/Bidón → Máquina
CREATE TABLE IF NOT EXISTS fenix_movimientos_combustible (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_movimiento     TEXT    NOT NULL CHECK (tipo_movimiento IN ('COMPRA','TRASPASO','CONSUMO')),
    fecha               TEXT    NOT NULL,
    semana              INTEGER,  -- Número de semana ISO del año
    -- Factura (solo aplica en COMPRA)
    factura_id          INTEGER REFERENCES fenix_facturas_combustible(id) ON DELETE SET NULL,
    -- Origen del combustible
    origen_tipo         TEXT    NOT NULL CHECK (origen_tipo IN ('Gasolinera','Tanque','Marimba','Bidon','Pipa')),
    origen_nombre       TEXT    NOT NULL,  -- Nombre específico Ej. 'Gasolinera Huixquilucan'
    -- Destino del combustible
    destino_tipo        TEXT    NOT NULL CHECK (destino_tipo IN ('Tanque','Marimba','Bidon','Pipa','Equipo')),
    destino_nombre      TEXT    NOT NULL,  -- Nombre o Número Económico si es equipo
    -- Referencia al equipo si el destino es una máquina/unidad (CONSUMO)
    equipo_id           INTEGER REFERENCES fenix_equipos(id) ON DELETE SET NULL,
    -- Contexto
    obra_id             INTEGER REFERENCES fenix_obras(id) ON DELETE SET NULL,
    -- Cantidades
    litros              NUMERIC NOT NULL CHECK (litros > 0),
    precio_unitario     NUMERIC NOT NULL DEFAULT 0 CHECK (precio_unitario >= 0),
    importe             NUMERIC GENERATED ALWAYS AS (litros * precio_unitario) STORED,
    -- Rendimiento reportado (horas o km)
    rendimiento         NUMERIC CHECK (rendimiento >= 0),
    -- Control
    folio_vale          TEXT,
    observaciones       TEXT,
    imagen_url          TEXT,
    created_at          TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
);

-- ====================
-- ACARREOS
-- ====================

-- 8. Viajes de Acarreo
--    Cada fila = un viaje validado de un camión.
--    La suma por sindicato + semana = lo que se le debe pagar.
CREATE TABLE IF NOT EXISTS fenix_viajes_acarreo (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    folio           TEXT,
    fecha           TEXT    NOT NULL,
    semana          INTEGER NOT NULL,  -- Número de semana ISO
    obra_id         INTEGER NOT NULL REFERENCES fenix_obras(id) ON DELETE CASCADE,
    sindicato_id    INTEGER NOT NULL REFERENCES fenix_sindicatos(id) ON DELETE CASCADE,
    material        TEXT    NOT NULL,  -- Ej. 'Mezcla Asfáltica', 'Material Fresado'
    categoria       TEXT    NOT NULL,  -- Ej. 'Mezcla', 'Fresado', 'Material'
    placa           TEXT    NOT NULL,
    capacidad_m3    NUMERIC CHECK (capacidad_m3 > 0),
    operador        TEXT,
    costo_unitario  NUMERIC NOT NULL CHECK (costo_unitario >= 0),
    subtotal        NUMERIC NOT NULL CHECK (subtotal >= 0),
    iva             NUMERIC NOT NULL DEFAULT 0 CHECK (iva >= 0),
    total           NUMERIC GENERATED ALWAYS AS (subtotal + iva) STORED,
    estatus         TEXT    NOT NULL DEFAULT 'Registrado' CHECK (estatus IN ('Registrado','Validado','Facturado','Pagado')),
    observaciones   TEXT,
    imagen_url      TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
);

-- ====================
-- ÍNDICES PARA RENDIMIENTO
-- ====================
CREATE INDEX IF NOT EXISTS idx_mov_comb_fecha    ON fenix_movimientos_combustible(fecha);
CREATE INDEX IF NOT EXISTS idx_mov_comb_obra      ON fenix_movimientos_combustible(obra_id);
CREATE INDEX IF NOT EXISTS idx_mov_comb_equipo    ON fenix_movimientos_combustible(equipo_id);
CREATE INDEX IF NOT EXISTS idx_mov_comb_tipo      ON fenix_movimientos_combustible(tipo_movimiento);
CREATE INDEX IF NOT EXISTS idx_viajes_obra        ON fenix_viajes_acarreo(obra_id);
CREATE INDEX IF NOT EXISTS idx_viajes_sindicato   ON fenix_viajes_acarreo(sindicato_id);
CREATE INDEX IF NOT EXISTS idx_viajes_semana      ON fenix_viajes_acarreo(semana);
CREATE INDEX IF NOT EXISTS idx_facturas_estatus   ON fenix_facturas_combustible(estatus_pago);

-- ====================
-- TABLA DE HORAS DE TRABAJO (Módulo de Rendimiento)
-- ====================

-- 9. Horas de Trabajo por Máquina
--    Fuente: Pestaña Captura_Horas del archivo Maestro
--    Permite calcular el rendimiento real (L/h) vs el rendimiento base del inventario.
CREATE TABLE IF NOT EXISTS fenix_horas_trabajo (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    folio               TEXT    UNIQUE NOT NULL,  -- Ej. HT-MT-25-001
    fecha               TEXT    NOT NULL,
    semana              INTEGER,
    obra_id             INTEGER REFERENCES fenix_obras(id) ON DELETE SET NULL,
    equipo_id           INTEGER REFERENCES fenix_equipos(id) ON DELETE SET NULL,
    operador            TEXT,
    horas_trabajadas    NUMERIC NOT NULL CHECK (horas_trabajadas >= 0),
    actividad_principal TEXT,
    created_at          TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
);

CREATE INDEX IF NOT EXISTS idx_horas_equipo ON fenix_horas_trabajo(equipo_id);
CREATE INDEX IF NOT EXISTS idx_horas_fecha  ON fenix_horas_trabajo(fecha);
CREATE INDEX IF NOT EXISTS idx_horas_obra   ON fenix_horas_trabajo(obra_id);

-- ====================
-- VISTAS DE CONCILIACIÓN (Listas para usar en Excel/Dashboard)
-- ====================

-- Vista A: Resumen de Facturas vs Compras registradas
CREATE VIEW IF NOT EXISTS v_conciliacion_facturas AS
SELECT
    f.id,
    f.folio_factura,
    f.proveedor,
    f.tipo_combustible,
    f.fecha_emision,
    f.litros_amparados          AS litros_facturados,
    COALESCE(SUM(m.litros), 0)  AS litros_registrados,
    f.litros_amparados - COALESCE(SUM(m.litros), 0) AS diferencia_litros,
    f.importe_total,
    f.estatus_pago
FROM fenix_facturas_combustible f
LEFT JOIN fenix_movimientos_combustible m ON m.factura_id = f.id
GROUP BY f.id;

-- Vista B: Balance por Contenedor (¿Cuántos litros tiene cada intermediario?)
CREATE VIEW IF NOT EXISTS v_balance_contenedores AS
SELECT
    contenedor,
    tipo_combustible_aprox,
    SUM(entradas) - SUM(salidas) AS litros_en_existencia
FROM (
    -- Entradas al contenedor
    SELECT
        m.destino_nombre       AS contenedor,
        'N/A'                  AS tipo_combustible_aprox,
        m.litros               AS entradas,
        0                      AS salidas
    FROM fenix_movimientos_combustible m
    WHERE m.destino_tipo IN ('Tanque','Marimba','Bidon','Pipa')
    UNION ALL
    -- Salidas del contenedor
    SELECT
        m.origen_nombre        AS contenedor,
        'N/A'                  AS tipo_combustible_aprox,
        0                      AS entradas,
        m.litros               AS salidas
    FROM fenix_movimientos_combustible m
    WHERE m.origen_tipo IN ('Tanque','Marimba','Bidon','Pipa')
) sub
GROUP BY contenedor;

-- Vista C: Consumo real por Equipo
CREATE VIEW IF NOT EXISTS v_consumo_por_equipo AS
SELECT
    e.numero_economico,
    e.descripcion,
    e.tipo_combustible,
    o.nombre                  AS obra,
    strftime('%Y-%W', m.fecha) AS semana_año,
    SUM(m.litros)             AS total_litros,
    SUM(m.importe)            AS total_importe,
    SUM(m.rendimiento)        AS total_rendimiento
FROM fenix_movimientos_combustible m
JOIN fenix_equipos e ON e.id = m.equipo_id
LEFT JOIN fenix_obras o ON o.id = m.obra_id
WHERE m.tipo_movimiento = 'CONSUMO'
GROUP BY e.id, o.id, strftime('%Y-%W', m.fecha);

-- Vista D: Estimación de Pagos a Sindicatos (Acarreos)
CREATE VIEW IF NOT EXISTS v_estimacion_pagos_sindicatos AS
SELECT
    s.nombre                  AS sindicato,
    o.nombre                  AS obra,
    v.semana,
    v.categoria,
    COUNT(*)                  AS total_viajes,
    SUM(v.subtotal)           AS subtotal_acumulado,
    SUM(v.iva)                AS iva_acumulado,
    SUM(v.total)              AS total_a_pagar,
    MIN(v.estatus)            AS estatus_min  -- si hay uno no pagado, aparece
FROM fenix_viajes_acarreo v
JOIN fenix_sindicatos s ON s.id = v.sindicato_id
JOIN fenix_obras o ON o.id = v.obra_id
GROUP BY s.id, o.id, v.semana, v.categoria;

-- Vista E: Rendimiento Real vs Base por Máquina (Módulo de Rendimiento)
--   Semáforo: VERDE (-15% a +10%), AMARILLO (+10% a +25%), ROJO (>+25%)
CREATE VIEW IF NOT EXISTS v_rendimiento_maquinaria AS
SELECT
    e.numero_economico,
    e.descripcion,
    o.nombre                          AS obra,
    strftime('%Y-%W', h.fecha)        AS semana_anio,
    h.semana                          AS semana_num,
    SUM(h.horas_trabajadas)           AS horas_totales,
    COALESCE(SUM(m.litros), 0)        AS litros_consumidos,
    CASE WHEN SUM(h.horas_trabajadas) > 0
         THEN ROUND(COALESCE(SUM(m.litros), 0) / SUM(h.horas_trabajadas), 2)
         ELSE 0
    END                               AS rendimiento_real_lh,
    e.rendimiento_base                AS rendimiento_base_lh,
    CASE
        WHEN e.rendimiento_base IS NULL OR e.rendimiento_base = 0 THEN NULL
        WHEN SUM(h.horas_trabajadas) = 0 THEN NULL
        ELSE ROUND(
            (COALESCE(SUM(m.litros), 0) / SUM(h.horas_trabajadas) - e.rendimiento_base)
            / e.rendimiento_base * 100, 1)
    END                               AS desviacion_pct,
    CASE
        WHEN e.rendimiento_base IS NULL OR SUM(h.horas_trabajadas) = 0 THEN 'SIN DATOS'
        WHEN (
            (COALESCE(SUM(m.litros), 0) / SUM(h.horas_trabajadas) - e.rendimiento_base)
            / e.rendimiento_base * 100) > 25   THEN 'ROJO - Anomalia'
        WHEN (
            (COALESCE(SUM(m.litros), 0) / SUM(h.horas_trabajadas) - e.rendimiento_base)
            / e.rendimiento_base * 100) > 10   THEN 'AMARILLO - Revisar'
        ELSE 'VERDE - Normal'
    END                               AS semaforo
FROM fenix_horas_trabajo h
JOIN fenix_equipos e  ON e.id = h.equipo_id
JOIN fenix_obras o    ON o.id = h.obra_id
LEFT JOIN fenix_movimientos_combustible m
    ON  m.equipo_id      = e.id
    AND m.fecha          = h.fecha
    AND m.tipo_movimiento = 'CONSUMO'
GROUP BY e.id, o.id, strftime('%Y-%W', h.fecha);
