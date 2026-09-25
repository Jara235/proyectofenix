-- ==========================================
-- SCRIPT DE INICIALIZACIÓN: PROYECTO FÉNIX (MODIFICADO OCR & ESTIMADOS)
-- COPIAR Y EJECUTAR EN EL SQL EDITOR DE SUPABASE
-- ==========================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Tabla de Obras (Catálogo)
CREATE TABLE IF NOT EXISTS fenix_obras (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Pre-cargar las 4 obras oficiales
INSERT INTO fenix_obras (codigo, nombre) VALUES
('MT', 'México-Toluca'),
('L3M', 'Lerma - Tres Marías'),
('CL', 'Chamapa-Lechería'),
('LT', 'Lerma-Tenango')
ON CONFLICT (codigo) DO UPDATE SET nombre = EXCLUDED.nombre;

-- 2. Tabla de Equipos y Maquinaria (Catálogo)
CREATE TABLE IF NOT EXISTS fenix_equipos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo_economico TEXT UNIQUE NOT NULL,
    tipo_equipo TEXT NOT NULL,
    tipo_rendimiento TEXT NOT NULL CHECK (tipo_rendimiento IN ('horas', 'kilometros')),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Pre-cargar los equipos reales de la obra
INSERT INTO fenix_equipos (codigo_economico, tipo_equipo, tipo_rendimiento) VALUES
('PER-200', 'Perfiladora Wirtgen F-200', 'horas'),
('VOG-03', 'Vögele-03', 'horas'),
('HAMM', 'Tándem Hamm', 'horas'),
('DINA', 'Neumático Dinapac', 'horas'),
('BAR-01', 'Barredora Broce Broom', 'horas'),
('RET-02', 'Retroexcavadora', 'horas'),
('PET-02', 'Petrolizadora', 'horas'),
('CAM-02', 'Camión Impacto', 'kilometros'),
('COM-01', 'Compresor Ingersoll Rand', 'horas'),
('TL-01', 'Torre de Luces Maxilight', 'horas'),
('FR-01', 'Fresadora', 'horas'),
('CP-01', 'Compactador', 'horas'),
('EX-01', 'Excavadora', 'horas'),
('PP-01', 'Pipa', 'kilometros'),
('CM-01', 'Camión', 'kilometros'),
('CR-01', 'Cargador', 'horas'),
('OTRO', 'Otro', 'horas')
ON CONFLICT (codigo_economico) DO UPDATE SET 
    tipo_equipo = EXCLUDED.tipo_equipo,
    tipo_rendimiento = EXCLUDED.tipo_rendimiento;

-- 3. Tabla de Bitácora del Tanque Pegaso
CREATE TABLE IF NOT EXISTS fenix_bitacora_pegaso (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fecha DATE NOT NULL DEFAULT CURRENT_DATE,
    tipo_movimiento TEXT NOT NULL CHECK (tipo_movimiento IN ('Entrada', 'Salida a Marimba', 'Salida Directa Máquina')),
    origen_destino TEXT NOT NULL, -- 'Gasolinera Huixquilucan', 'Tanque Pegaso', etc.
    obra_id UUID REFERENCES fenix_obras(id) ON DELETE SET NULL,
    equipo_id UUID REFERENCES fenix_equipos(id) ON DELETE SET NULL,
    litros_entrada NUMERIC NOT NULL DEFAULT 0 CHECK (litros_entrada >= 0),
    litros_salida NUMERIC NOT NULL DEFAULT 0 CHECK (litros_salida >= 0),
    costo_por_litro NUMERIC NOT NULL DEFAULT 0 CHECK (costo_por_litro >= 0),
    importe NUMERIC GENERATED ALWAYS AS (
        CASE 
            WHEN tipo_movimiento = 'Entrada' THEN litros_entrada * costo_por_litro
            ELSE litros_salida * costo_por_litro
        END
    ) STORED,
    observaciones TEXT,
    image_url TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 4. Tabla de Bitácora de la Marimba (Mamba / M-01)
CREATE TABLE IF NOT EXISTS fenix_bitacora_marimba (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fecha DATE NOT NULL DEFAULT CURRENT_DATE,
    tipo_movimiento TEXT NOT NULL CHECK (tipo_movimiento IN ('Entrada desde Pegaso', 'Entrada desde Gasolinera', 'Salida a Obra')),
    origen_obra_id UUID REFERENCES fenix_obras(id) ON DELETE SET NULL,
    equipo_id UUID REFERENCES fenix_equipos(id) ON DELETE SET NULL,
    litros_entrada NUMERIC NOT NULL DEFAULT 0 CHECK (litros_entrada >= 0),
    litros_salida NUMERIC NOT NULL DEFAULT 0 CHECK (litros_salida >= 0),
    costo_por_litro NUMERIC NOT NULL DEFAULT 0 CHECK (costo_por_litro >= 0),
    importe NUMERIC GENERATED ALWAYS AS (
        CASE 
            WHEN tipo_movimiento LIKE 'Entrada%' THEN litros_entrada * costo_por_litro
            ELSE litros_salida * costo_por_litro
        END
    ) STORED,
    observaciones TEXT,
    image_url TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 5. Tabla de Bitácora de Obra (Recepción y Consumo de Máquinas)
CREATE TABLE IF NOT EXISTS fenix_bitacora_obra (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fecha DATE NOT NULL DEFAULT CURRENT_DATE,
    obra_id UUID REFERENCES fenix_obras(id) ON DELETE CASCADE,
    fuente TEXT NOT NULL CHECK (fuente IN ('Pegaso Directo', 'Marimba M-01')),
    equipo_id UUID REFERENCES fenix_equipos(id) ON DELETE CASCADE,
    litros_recibidos NUMERIC NOT NULL CHECK (litros_recibidos > 0),
    costo_por_litro NUMERIC NOT NULL DEFAULT 0 CHECK (costo_por_litro >= 0),
    importe NUMERIC GENERATED ALWAYS AS (litros_recibidos * costo_por_litro) STORED,
    actividad_ejecutada TEXT,
    incidencia TEXT,
    horas_trabajadas NUMERIC CHECK (horas_trabajadas >= 0),
    kilometraje NUMERIC CHECK (kilometraje >= 0),
    observaciones TEXT,
    image_url TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 6. Tabla de Estimados Semanales de Combustible (Nuevo)
CREATE TABLE IF NOT EXISTS fenix_estimados_semanales (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    semana_fecha DATE NOT NULL DEFAULT CURRENT_DATE, -- Fecha del Lunes de esa semana
    obra_id UUID REFERENCES fenix_obras(id) ON DELETE CASCADE,
    equipo_id UUID REFERENCES fenix_equipos(id) ON DELETE CASCADE,
    litros_estimados NUMERIC NOT NULL CHECK (litros_estimados >= 0),
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(semana_fecha, obra_id, equipo_id)
);

-- 7. Tabla de Mensajes Recibidos de WhatsApp (Inbox)
CREATE TABLE IF NOT EXISTS fenix_whatsapp_inbox (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fecha_mensaje TIMESTAMPTZ DEFAULT now(),
    remitente_telefono TEXT NOT NULL,
    remitente_nombre TEXT NOT NULL,
    mensaje_original TEXT NOT NULL,
    categoria_detectada TEXT CHECK (categoria_detectada IN ('pegaso', 'marimba', 'obra', 'estimado_semanal', 'desconocido')),
    datos_extraidos JSONB DEFAULT '{}'::jsonb,
    image_url TEXT,
    procesado BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- ==========================================
-- POLÍTICAS DE SEGURIDAD (RLS) - SUPABASE
-- ==========================================

ALTER TABLE fenix_obras ENABLE ROW LEVEL SECURITY;
ALTER TABLE fenix_equipos ENABLE ROW LEVEL SECURITY;
ALTER TABLE fenix_bitacora_pegaso ENABLE ROW LEVEL SECURITY;
ALTER TABLE fenix_bitacora_marimba ENABLE ROW LEVEL SECURITY;
ALTER TABLE fenix_bitacora_obra ENABLE ROW LEVEL SECURITY;
ALTER TABLE fenix_estimados_semanales ENABLE ROW LEVEL SECURITY;
ALTER TABLE fenix_whatsapp_inbox ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Permitir todo a anon en obras" ON fenix_obras FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "Permitir todo a anon en equipos" ON fenix_equipos FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "Permitir todo a anon en pegaso" ON fenix_bitacora_pegaso FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "Permitir todo a anon en marimba" ON fenix_bitacora_marimba FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "Permitir todo a anon en obra bitacora" ON fenix_bitacora_obra FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "Permitir todo a anon en estimados" ON fenix_estimados_semanales FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "Permitir todo a anon en whatsapp inbox" ON fenix_whatsapp_inbox FOR ALL TO anon USING (true) WITH CHECK (true);

-- ==========================================
-- INSERTAR DATOS DE PRUEBA INICIALES
-- ==========================================

DO $$
DECLARE
    id_mt UUID;
    id_l3m UUID;
    id_cl UUID;
    id_lt UUID;
    
    id_per UUID;
    id_vog UUID;
    id_hamm UUID;
    id_dina UUID;
    id_bar UUID;
    id_ret UUID;
    id_pet UUID;
    id_cam UUID;
    id_com UUID;
    id_tl UUID;
    
    id_ex UUID;
    id_cp UUID;
BEGIN
    -- Obtener IDs de obras
    SELECT id INTO id_mt FROM fenix_obras WHERE codigo = 'MT';
    SELECT id INTO id_l3m FROM fenix_obras WHERE codigo = 'L3M';
    SELECT id INTO id_cl FROM fenix_obras WHERE codigo = 'CL';
    SELECT id INTO id_lt FROM fenix_obras WHERE codigo = 'LT';
    
    -- Obtener IDs de equipos
    SELECT id INTO id_per FROM fenix_equipos WHERE codigo_economico = 'PER-200';
    SELECT id INTO id_vog FROM fenix_equipos WHERE codigo_economico = 'VOG-03';
    SELECT id INTO id_hamm FROM fenix_equipos WHERE codigo_economico = 'HAMM';
    SELECT id INTO id_dina FROM fenix_equipos WHERE codigo_economico = 'DINA';
    SELECT id INTO id_bar FROM fenix_equipos WHERE codigo_economico = 'BAR-01';
    SELECT id INTO id_ret FROM fenix_equipos WHERE codigo_economico = 'RET-02';
    SELECT id INTO id_pet FROM fenix_equipos WHERE codigo_economico = 'PET-02';
    SELECT id INTO id_cam FROM fenix_equipos WHERE codigo_economico = 'CAM-02';
    SELECT id INTO id_com FROM fenix_equipos WHERE codigo_economico = 'COM-01';
    SELECT id INTO id_tl FROM fenix_equipos WHERE codigo_economico = 'TL-01';
    SELECT id INTO id_ex FROM fenix_equipos WHERE codigo_economico = 'EX-01';
    SELECT id INTO id_cp FROM fenix_equipos WHERE codigo_economico = 'CP-01';

    -- 1. Insertar Estimados Semanales para Obra México-Toluca (Semana Lunes 15 de Junio)
    INSERT INTO fenix_estimados_semanales (semana_fecha, obra_id, equipo_id, litros_estimados) VALUES
    ('2026-06-15', id_mt, id_per, 250),
    ('2026-06-15', id_mt, id_vog, 120),
    ('2026-06-15', id_mt, id_hamm, 50),
    ('2026-06-15', id_mt, id_dina, 50),
    ('2026-06-15', id_mt, id_bar, 40),
    ('2026-06-15', id_mt, id_ret, 60),
    ('2026-06-15', id_mt, id_pet, 50),
    ('2026-06-15', id_mt, id_cam, 30)
    ON CONFLICT (semana_fecha, obra_id, equipo_id) DO UPDATE SET litros_estimados = EXCLUDED.litros_estimados;

    -- 2. Insertar Estimados Semanales para Lerma-Tenango
    INSERT INTO fenix_estimados_semanales (semana_fecha, obra_id, equipo_id, litros_estimados) VALUES
    ('2026-06-15', id_lt, id_vog, 90),
    ('2026-06-15', id_lt, id_dina, 40),
    ('2026-06-15', id_lt, id_bar, 40)
    ON CONFLICT (semana_fecha, obra_id, equipo_id) DO UPDATE SET litros_estimados = EXCLUDED.litros_estimados;

    -- 3. Movimientos del Tanque Pegaso
    -- Carga de Gasolinera Huixquilucan
    INSERT INTO fenix_bitacora_pegaso (fecha, tipo_movimiento, origen_destino, litros_entrada, costo_por_litro, observaciones)
    VALUES ('2026-06-15', 'Entrada', 'Gasolinera Huixquilucan', 5000, 27.20, 'Compra semanal inicial Factura F-9921');

    -- Salida Pegaso a Marimba
    INSERT INTO fenix_bitacora_pegaso (fecha, tipo_movimiento, origen_destino, obra_id, litros_salida, costo_por_litro, observaciones)
    VALUES ('2026-06-15', 'Salida a Marimba', 'Tanque Pegaso', id_mt, 1500, 27.20, 'Despacho a Marimba M-01 para obra MT');

    -- Marimba: Entrada desde Pegaso
    INSERT INTO fenix_bitacora_marimba (fecha, tipo_movimiento, origen_obra_id, litros_entrada, costo_por_litro, observaciones)
    VALUES ('2026-06-15', 'Entrada desde Pegaso', id_mt, 1500, 27.20, 'Carga recibida de Tanque Pegaso');

    -- Pegaso: Salida Directa a Máquina (Lerma-Tenango)
    INSERT INTO fenix_bitacora_pegaso (fecha, tipo_movimiento, origen_destino, obra_id, equipo_id, litros_salida, costo_por_litro, observaciones)
    VALUES ('2026-06-15', 'Salida Directa Máquina', 'Tanque Pegaso', id_lt, id_vog, 90, 27.20, 'Compactadora Vogele LT directa de Pegaso');

    -- Obra LT: Registra la recepción directa de Pegaso
    INSERT INTO fenix_bitacora_obra (fecha, obra_id, fuente, equipo_id, litros_recibidos, costo_por_litro, actividad_ejecutada, horas_trabajadas, observaciones)
    VALUES ('2026-06-15', id_lt, 'Pegaso Directo', id_vog, 90, 27.20, 'Apoyo carpeta asfáltica frente 1', 5.5, 'Suministro directo');

    -- Marimba: Suministros a obra MT (Consumos reales)
    INSERT INTO fenix_bitacora_marimba (fecha, tipo_movimiento, origen_obra_id, equipo_id, litros_salida, costo_por_litro, observaciones)
    VALUES 
    ('2026-06-15', 'Salida a Obra', id_mt, id_per, 250, 27.20, 'Suministro Perfiladora Wirtgen'),
    ('2026-06-15', 'Salida a Obra', id_mt, id_vog, 100, 27.20, 'Suministro Vogele-03');

    -- Obra MT: Registra recepción de combustible desde Marimba
    INSERT INTO fenix_bitacora_obra (fecha, obra_id, fuente, equipo_id, litros_recibidos, costo_por_litro, actividad_ejecutada, horas_trabajadas, observaciones)
    VALUES 
    ('2026-06-15', id_mt, 'Marimba M-01', id_per, 250, 27.20, 'Perfilado de carpeta asfáltica', 6, 'Ticket flujómetro 0250'),
    ('2026-06-15', id_mt, 'Marimba M-01', id_vog, 100, 27.20, 'Pavimentación de tramo principal', 4.5, 'Suministro de combustible');

END $$;
