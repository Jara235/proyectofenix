PRAGMA foreign_keys = ON;

-- ==========================================
-- CATÁLOGOS GLOBALES
-- ==========================================
CREATE TABLE IF NOT EXISTS catalogos_obras (
    codigo TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    ingeniero_responsable TEXT
);

CREATE TABLE IF NOT EXISTS catalogos_equipos (
    numero_economico TEXT PRIMARY KEY,
    descripcion TEXT,
    tipo_equipo TEXT
);

CREATE TABLE IF NOT EXISTS catalogos_operadores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL
);

-- ==========================================
-- MÓDULO: DIÉSEL
-- ==========================================
CREATE TABLE IF NOT EXISTS diesel_solicitudes (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    semana               INTEGER NOT NULL,
    fecha_solicitud      TEXT NOT NULL,
    ingeniero_solicitante TEXT NOT NULL,
    obra_destino         TEXT NOT NULL,
    litros_solicitados   NUMERIC NOT NULL,
    estatus              TEXT DEFAULT 'Pendiente',
    observaciones        TEXT
);

CREATE TABLE IF NOT EXISTS diesel_consumos (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    folio_conciliacion   TEXT UNIQUE NOT NULL, 
    fecha                TEXT NOT NULL,
    semana               INTEGER NOT NULL,
    origen               TEXT,
    tipo_movimiento      TEXT,
    obra_destino         TEXT REFERENCES catalogos_obras(nombre),
    equipo               TEXT,
    equipo_economico     TEXT REFERENCES catalogos_equipos(numero_economico),
    litros               NUMERIC NOT NULL,
    costo_por_litro      NUMERIC,
    importe_total        NUMERIC NOT NULL,
    responsable          TEXT,
    operador             TEXT REFERENCES catalogos_operadores(nombre),
    observaciones        TEXT,
    foto_evidencia       BLOB,  
    usuario_captura      TEXT,
    solicitud_id         INTEGER REFERENCES diesel_solicitudes(id)
);

CREATE TABLE IF NOT EXISTS diesel_facturas (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    folio_conciliacion   TEXT NOT NULL, 
    folio_factura        TEXT NOT NULL,
    fecha_factura        TEXT,
    semana               INTEGER NOT NULL,
    proveedor            TEXT,
    punto_de_carga       TEXT,
    litros_facturados    NUMERIC NOT NULL,
    precio_unitario      NUMERIC,
    importe              NUMERIC,
    iva                  NUMERIC,
    importe_total        NUMERIC NOT NULL,
    uuid_cfdi            TEXT,
    archivo_pdf          BLOB,
    archivo_xml          BLOB
);

-- ==========================================
-- MÓDULO: GASOLINA
-- ==========================================
CREATE TABLE IF NOT EXISTS gasolina_autorizaciones (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    folio_conciliacion   TEXT UNIQUE NOT NULL,
    fecha                TEXT,
    semana               INTEGER,
    origen               TEXT,
    obra_destino         TEXT,
    vehiculo             TEXT,
    placa                TEXT,
    litros_autorizados   NUMERIC,
    importe_autorizado   NUMERIC,
    responsable          TEXT,
    estatus_autorizacion TEXT
);

CREATE TABLE IF NOT EXISTS gasolina_consumos (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    folio_conciliacion   TEXT UNIQUE NOT NULL,
    fecha                TEXT NOT NULL,
    semana               INTEGER NOT NULL,
    origen               TEXT,
    obra_destino         TEXT,
    vehiculo             TEXT,
    placa                TEXT,
    kilometraje          NUMERIC,
    litros               NUMERIC NOT NULL,
    costo_por_litro      NUMERIC,
    importe_total        NUMERIC NOT NULL,
    conductor            TEXT,
    observaciones        TEXT,
    foto_evidencia       BLOB, 
    usuario_captura      TEXT  
);

CREATE TABLE IF NOT EXISTS gasolina_facturas (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    folio_conciliacion   TEXT NOT NULL,
    folio_factura        TEXT NOT NULL,
    fecha_factura        TEXT,
    semana               INTEGER NOT NULL,
    proveedor            TEXT,
    litros_facturados    NUMERIC NOT NULL,
    importe_total        NUMERIC NOT NULL,
    uuid_cfdi            TEXT,
    archivo_pdf          BLOB,
    archivo_xml          BLOB
);

-- ==========================================
-- MÓDULO: ACARREOS
-- ==========================================
CREATE TABLE IF NOT EXISTS acarreos_viajes (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    folio_viaje          TEXT UNIQUE NOT NULL,
    fecha                TEXT NOT NULL,
    semana               INTEGER NOT NULL,
    sindicato            TEXT,
    material             TEXT,
    origen               TEXT,
    obra_destino         TEXT,
    placa_camion         TEXT,
    capacidad_m3         NUMERIC,
    precio_unitario      NUMERIC,
    importe_total        NUMERIC NOT NULL,
    observaciones        TEXT,
    foto_evidencia       BLOB,
    usuario_captura      TEXT
);

CREATE TABLE IF NOT EXISTS acarreos_facturas (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    folio_viaje          TEXT NOT NULL,
    folio_factura        TEXT NOT NULL,
    fecha_factura        TEXT,
    semana               INTEGER NOT NULL,
    sindicato_proveedor  TEXT,
    viajes_amparados     INTEGER,
    importe_total        NUMERIC NOT NULL,
    uuid_cfdi            TEXT,
    archivo_pdf          BLOB,
    archivo_xml          BLOB
);

-- ==========================================
-- MÓDULO: MEZCLA ASFÁLTICA
-- ==========================================
CREATE TABLE IF NOT EXISTS mezcla_materia_prima (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    folio_conciliacion   TEXT UNIQUE NOT NULL,
    fecha                TEXT NOT NULL,
    semana               INTEGER NOT NULL,
    mina_origen          TEXT,
    planta_destino       TEXT,
    material             TEXT,
    camion               TEXT,
    placa                TEXT,
    toneladas            NUMERIC NOT NULL,
    costo_material       NUMERIC,
    flete                NUMERIC,
    importe_total        NUMERIC NOT NULL,
    foto_evidencia       BLOB,
    usuario_captura      TEXT
);

CREATE TABLE IF NOT EXISTS mezcla_produccion (
    id                       INTEGER PRIMARY KEY AUTOINCREMENT,
    folio_conciliacion       TEXT UNIQUE NOT NULL,
    fecha                    TEXT NOT NULL,
    semana                   INTEGER NOT NULL,
    planta                   TEXT,
    tipo_mezcla              TEXT,
    toneladas_producidas     NUMERIC NOT NULL,
    emulsion_consumida_lts   NUMERIC,
    agregados_consumidos_m3  NUMERIC,
    costo_total_produccion   NUMERIC,
    foto_evidencia           BLOB,
    usuario_captura          TEXT
);

CREATE TABLE IF NOT EXISTS mezcla_tendido (
    id                         INTEGER PRIMARY KEY AUTOINCREMENT,
    folio_conciliacion         TEXT UNIQUE NOT NULL,
    fecha                      TEXT NOT NULL,
    semana                     INTEGER NOT NULL,
    planta_origen              TEXT,
    obra_destino               TEXT,
    viajes_enviados            INTEGER,
    toneladas_tendidas         NUMERIC NOT NULL,
    metros_cuadrados_tendidos  NUMERIC,
    rendimiento_obra           TEXT,
    foto_evidencia             BLOB,
    usuario_captura            TEXT
);
