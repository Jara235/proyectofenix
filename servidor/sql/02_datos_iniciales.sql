-- ============================================================
-- Proyecto Fénix v2 — Datos Iniciales (Catálogos Reales)
-- Grupo Trujano
-- Archivo: 02_datos_iniciales.sql
-- Fuente: Extraído de GC-COMB-3.1 Excel Maestro + GC-COMB-003_V2
-- ============================================================

-- ============================================================
-- 1. OBRAS Y PLANTAS
-- ============================================================

INSERT INTO fenix_obras (nombre, iniciales, tipo) VALUES
    ('México-Toluca',               'MT',  'obra'),
    ('Lerma - Tres Marías',         'LT',  'obra'),
    ('Chamapa-Lechería',            'CL',  'obra'),
    ('Bacheo Toluca',               'BT',  'obra'),
    ('Planta Asfalto Pegaso',       'PAP', 'planta_asfalto'),
    ('Planta Asfalto Huixquilucan', 'PAH', 'planta_asfalto'),
    ('Dragones',                    'DR',  'obra'),
    ('Jalisco',                     'JAL', 'obra'),
    ('No aplica',                   'NA',  'otro');

-- ============================================================
-- 2. GASOLINERAS DEL GRUPO
-- ============================================================

INSERT INTO fenix_gasolineras (nombre, ubicacion) VALUES
    ('Gasolinera Huixquilucan', 'Huixquilucan, Estado de México');

-- ============================================================
-- 3. EQUIPOS / MAQUINARIA (40+ equipos del inventario real)
-- ============================================================
-- Nota: obra_asignada_id y operador_nombre se actualizan después
-- de crear los usuarios con los nombres de operadores.

INSERT INTO fenix_equipos
    (economico, tipo_unidad, marca, modelo, anio_fabricacion, num_serie, dueno, rendimiento_nuevo, unidad_medida)
VALUES
    -- RETROEXCAVADORAS
    ('RT-01', 'Retroexcavadora', 'CASE',     '580 N',    2011, 'JJGN580NABC540211',    'Trituradora Roca Dura San Miguel S.A. de C.V.', 6.50, 'L/h'),
    ('RT-02', 'Retroexcavadora', 'JHONDEREE','310 K',    2010, '1T0231KXTEE258108',    NULL,                                           6.50, 'L/h'),
    ('RT-03', 'Retroexcavadora', 'CASE',     '580 N',    2010, 'JJGN58NHAC535026',     'Trituradora Roca Dura San Miguel S.A. de C.V.', 6.50, 'L/h'),
    ('RT-04', 'Retroexcavadora', 'CASE',     '420DN',    NULL, 'CAT0420DTFDP27091',    NULL,                                           6.50, 'L/h'),
    ('RT-05', 'Retroexcavadora', 'JHONDEREE','310SK',    NULL, '1T0310SKAEE262172',    NULL,                                           6.50, 'L/h'),
    -- PAVIMENTADORAS
    ('VG-01', 'Pavimentadora',   'VOGELE',   '1800-3 i', 2016, '14821687',             'JDJ Equipo y Construcciones S.A. de C.V.',     14.50,'L/h'),
    ('VG-02', 'Pavimentadora',   'VOGELE',   '1800-2 SJ',2009, '11821564',             'Trituradora Roca Dura San Miguel S.A. de C.V.',14.50,'L/h'),
    ('VG-03', 'Pavimentadora',   'VOGELE',   'SJ 1800-3',2021, '14823977',             'JDJ Equipo y Construcciones S.A. de C.V.',     14.50,'L/h'),
    -- PERFILADORAS
    ('PR-01', 'Perfiladora',     'RODATEC',  'RX600-4-4008',2015,'79816538',           'JDJ Equipo y Construcciones S.A. de C.V.',     65.00,'L/h'),
    ('PR-02', 'Perfiladora',     'RODATEC',  'RX600E',   2013, '79549560',             NULL,                                           65.00,'L/h'),
    -- BARREDORAS
    ('BR-01', 'Barredora',       'BROCE',    'RJ350',    2010, '89602',                'JDJ Equipo y Construcciones S.A. de C.V.',      7.50,'L/h'),
    ('BR-02', 'Barredora',       'LAYMOR',   'SM400',    2016, '36864',                'Trituradora Roca Dura San Miguel S.A. de C.V.', 7.50,'L/h'),
    ('BR-03', 'Barredora',       'SUPERIOR BROOM','DT80J',2015,'804108',              NULL,                                            7.50,'L/h'),
    ('BR-04', 'Barredora',       'LAYMOR',   'SM400',    2017, '34091',                'JDJ Equipo y Construcciones S.A. de C.V.',      7.50,'L/h'),
    ('BR-05', 'Barredora',       'BROCE BROOM','KR350',  NULL, '407123',              NULL,                                            7.50,'L/h'),
    ('BR-06', 'Barredora',       'BROCE BROOM','KR350',  NULL, '408531',              NULL,                                            7.50,'L/h'),
    -- DOBLE RODILLOS / VIBROCOMPACTADORES
    ('DR-01', 'Doble Rodillo / Vibrocompactador', 'HAMM', '120HD VV',2010,'H1840093', 'Trituradora Roca Dura San Miguel S.A. de C.V.',12.00,'L/h'),
    ('DR-02', 'Doble Rodillo / Vibrocompactador', 'HAMM', '140HD',   2010,'H1840234', 'JDJ Equipo y Construcciones S.A. de C.V.',     12.00,'L/h'),
    ('DR-03', 'Doble Rodillo',   'INGERSOLL RAND','DD-108HF',NULL,'189989',          NULL,                                           12.00,'L/h'),
    ('DR-04', 'Doble Rodillo',   'RAD ROLLER','FILY-325 PRO',NULL,'LD600JN2026012501',NULL,                                         12.00,'L/h'),
    -- TÁNDEM
    ('TD-01', 'Tándem Doble Rodillo / Vibrocompactor','CAT','CB54',2014,'CAT0CB54PJLM00895','Trituradora Roca Dura San Miguel S.A. de C.V.',12.00,'L/h'),
    -- VIBROCOMPACTADOR
    ('VC-01', 'Vibrocompactador','CATERPILLAR','CB66B',  2017, 'CATCB66BVB6600136',    'JDJ Equipo y Construcciones S.A. de C.V.',     12.00,'L/h'),
    -- NEUMÁTICOS / COMPACTADORES
    ('NM-01', 'Neumático / Compactador','DINAPAC','CP271',2010,'23620561',            'Trituradora Roca Dura San Miguel S.A. de C.V.', 9.50,'L/h'),
    ('NM-02', 'Neumático',       'VOLVO',    'PT-240R',  2014, 'VCE0T240A0S325028',   'JDJ Equipo y Construcciones S.A. de C.V.',      9.50,'L/h'),
    -- COMPRESORES
    ('CPR-01','Compresor',       'SULLIVAN PALATEK','D2010',2017,'PHD25B330551',      NULL,                                            9.00,'L/h'),
    ('CPR-02','Compresor',       'SULLIVAN PALATEK','D2010',2017,'PHD25B330552',      NULL,                                            9.00,'L/h'),
    -- TRANSFER BUGGY
    ('BG-01', 'Transfer Buggy',  'RODATEC',  NULL,       NULL, 'CB-2500B 538',         NULL,                                           30.00,'L/h'),
    -- IMPACTOS (medidos en km/L)
    ('CI-01', 'Impacto',         'FORD',     '4300',     2013, '1HTMMAAL2DH158631',   'JDJ Equipo y Construcciones S.A. de C.V.',      3.50,'km/L'),
    ('CI-02', 'Impacto',         'FORD',     'F800',     1998, '1FDNF80C7WVA19892',   'JDJ Equipo y Construcciones S.A. de C.V.',      3.50,'km/L'),
    -- PETROLIZADORAS
    ('PT-01', 'Petrolizadora',   'FORD',     'F800',     1998, '1FDNF80C2WVA22179',   'JDJ Equipo y Construcciones S.A. de C.V.',     10.00,'L/h'),
    ('PT-02', 'Petrolizadora',   'INTERNATIONAL',NULL,   2003, '3HTMMAAR830567',       NULL,                                           10.00,'L/h'),
    -- PIPA DE AGUA
    ('PP-01', 'Pipa de Agua',    'FORD',     NULL,       NULL, '1FDYR80U0GVA15942',   'JDJ Equipo y Construcciones S.A. de C.V.',      3.50,'km/L');

-- ============================================================
-- 4. ASIGNAR EQUIPOS A SUS OBRAS INICIALES
-- ============================================================

-- México-Toluca
UPDATE fenix_equipos SET obra_asignada_id = (SELECT id FROM fenix_obras WHERE iniciales = 'MT'),
    operador_nombre = 'Gerardo Ezequiel Piña Fernández'  WHERE economico = 'VG-01';
UPDATE fenix_equipos SET obra_asignada_id = (SELECT id FROM fenix_obras WHERE iniciales = 'MT'),
    operador_nombre = 'POR ASIGNAR'                      WHERE economico = 'DR-01';
UPDATE fenix_equipos SET obra_asignada_id = (SELECT id FROM fenix_obras WHERE iniciales = 'MT'),
    operador_nombre = 'Julián Piña Hernández'            WHERE economico = 'DR-02';
UPDATE fenix_equipos SET obra_asignada_id = (SELECT id FROM fenix_obras WHERE iniciales = 'MT'),
    operador_nombre = 'Edgar Rosales Martínez'           WHERE economico = 'BR-01';
UPDATE fenix_equipos SET obra_asignada_id = (SELECT id FROM fenix_obras WHERE iniciales = 'MT'),
    operador_nombre = 'Luis Fernando Mendiola Vivero'    WHERE economico = 'NM-02';
UPDATE fenix_equipos SET obra_asignada_id = (SELECT id FROM fenix_obras WHERE iniciales = 'MT'),
    operador_nombre = 'Adolfo Nava Lopez'                WHERE economico = 'RT-05';

-- Lerma - Tres Marías
UPDATE fenix_equipos SET obra_asignada_id = (SELECT id FROM fenix_obras WHERE iniciales = 'LT'),
    operador_nombre = 'Jose de Jesus Eusebio Martinez'   WHERE economico = 'VG-03';
UPDATE fenix_equipos SET obra_asignada_id = (SELECT id FROM fenix_obras WHERE iniciales = 'LT'),
    operador_nombre = 'Alan Alexis Gutierrez Flores'     WHERE economico = 'PR-02';
UPDATE fenix_equipos SET obra_asignada_id = (SELECT id FROM fenix_obras WHERE iniciales = 'LT'),
    operador_nombre = 'Fernando Angeles Reyes'           WHERE economico = 'BR-04';
UPDATE fenix_equipos SET obra_asignada_id = (SELECT id FROM fenix_obras WHERE iniciales = 'LT'),
    operador_nombre = 'Jose Manuel Reyes Flores'         WHERE economico = 'VC-01';
UPDATE fenix_equipos SET obra_asignada_id = (SELECT id FROM fenix_obras WHERE iniciales = 'LT'),
    operador_nombre = 'Marco Antonio Estrada Arellano'   WHERE economico = 'NM-01';
UPDATE fenix_equipos SET obra_asignada_id = (SELECT id FROM fenix_obras WHERE iniciales = 'LT'),
    operador_nombre = 'Eduardo Guadarrama Garcia'        WHERE economico = 'CPR-01';
UPDATE fenix_equipos SET obra_asignada_id = (SELECT id FROM fenix_obras WHERE iniciales = 'LT'),
    operador_nombre = 'Marco Antonio Millan Centeno'     WHERE economico = 'CI-02';
UPDATE fenix_equipos SET obra_asignada_id = (SELECT id FROM fenix_obras WHERE iniciales = 'LT'),
    operador_nombre = 'Francisco Gomora / Elthon Eduardo' WHERE economico = 'PT-02';

-- México-Toluca (RT-03 estaba asignado ahí en el catálogo)
UPDATE fenix_equipos SET obra_asignada_id = (SELECT id FROM fenix_obras WHERE iniciales = 'MT')
    WHERE economico = 'RT-03';

-- ============================================================
-- 5. TANQUE PEGASO Y MARIMBA M-01
-- ============================================================

-- Se insertan con obra/responsable NULL; se actualizan cuando se creen los usuarios
INSERT INTO fenix_tanques (nombre, capacidad_lts, obra_id) VALUES
    ('Tanque Pegaso', 20000, (SELECT id FROM fenix_obras WHERE iniciales = 'PAP'));

INSERT INTO fenix_pipas (nombre, capacidad_lts) VALUES
    ('Marimba M-01', NULL);

-- ============================================================
-- 6. USUARIOS INICIALES DEL SISTEMA
-- (contraseñas hasheadas con bcrypt — cambiar en producción)
-- ============================================================
-- NOTA: En producción los passwords deben generarse con bcrypt
-- desde n8n o el script de onboarding.
-- Por ahora se insertan con un hash de la contraseña "Fenix2026!"
-- Hash bcrypt de "Fenix2026!": $2b$12$Ym3uqS8q.../ejemplo (reemplazar)

INSERT INTO fenix_usuarios (nombre, email, password_hash, rol) VALUES
    -- === INGENIEROS DE OBRA / PLANTA (5 originales + 5 nuevos) ===
    ('Francisco Javier',      'fjavier@grupotrujano.mx',   '$2b$12$HASH_TEMPORAL_CAMBIAR', 'ingeniero'),
    ('Apolinar',              'apolinar@grupotrujano.mx',  '$2b$12$HASH_TEMPORAL_CAMBIAR', 'ingeniero'),
    ('Diego Carreola',        'dcarreola@grupotrujano.mx', '$2b$12$HASH_TEMPORAL_CAMBIAR', 'ingeniero'),
    ('Janeth Aguilar',        'janeth@grupotrujano.mx',    '$2b$12$HASH_TEMPORAL_CAMBIAR', 'ingeniero'),
    ('Luis Mendiola',         'luis@grupotrujano.mx',      '$2b$12$HASH_TEMPORAL_CAMBIAR', 'ingeniero'),
    ('Carlos Rivera',         'crivera@grupotrujano.mx',   '$2b$12$HASH_TEMPORAL_CAMBIAR', 'ingeniero'),
    ('Roberto Gómez',         'rgomez@grupotrujano.mx',    '$2b$12$HASH_TEMPORAL_CAMBIAR', 'ingeniero'),
    ('Ana Lilia Martínez',    'amartinez@grupotrujano.mx', '$2b$12$HASH_TEMPORAL_CAMBIAR', 'ingeniero'),
    ('Fernando Juárez',       'fjuarez@grupotrujano.mx',   '$2b$12$HASH_TEMPORAL_CAMBIAR', 'ingeniero'),
    ('Oscar Villanueva',      'ovillanueva@grupotrujano.mx','$2b$12$HASH_TEMPORAL_CAMBIAR', 'ingeniero'),

    -- === DIRECTIVOS (Autorizan combustible) ===
    ('Director Operaciones',  'operaciones@grupotrujano.mx','$2b$12$HASH_TEMPORAL_CAMBIAR', 'directivo'),
    ('Director General',      'direccion@grupotrujano.mx',  '$2b$12$HASH_TEMPORAL_CAMBIAR', 'directivo'),
    ('Auditor Interno',       'auditoria@grupotrujano.mx',  '$2b$12$HASH_TEMPORAL_CAMBIAR', 'directivo'),

    -- === CHOFERES DE PIPA / MARIMBA ===
    ('Brandon',               'brandon_pipa@grupotrujano.mx','$2b$12$HASH_TEMPORAL_CAMBIAR', 'chofer_pipa'),
    ('Jack',                  'jack_pipa@grupotrujano.mx',   '$2b$12$HASH_TEMPORAL_CAMBIAR', 'chofer_pipa'),
    ('Miguel Sánchez',        'msanchez_pipa@grupotrujano.mx','$2b$12$HASH_TEMPORAL_CAMBIAR', 'chofer_pipa'),
    ('Pedro Hernández',       'phernandez_pipa@grupotrujano.mx','$2b$12$HASH_TEMPORAL_CAMBIAR', 'chofer_pipa'),
    ('Ricardo López',         'rlopez_pipa@grupotrujano.mx', '$2b$12$HASH_TEMPORAL_CAMBIAR', 'chofer_pipa'),

    -- === OPERADORES DE TANQUE ===
    ('Mario Castillejos',     'mcastillejos_tanque@grupotrujano.mx','$2b$12$HASH_TEMPORAL_CAMBIAR', 'operador_tanque'),
    ('Hugo Ramírez',          'hramirez_tanque@grupotrujano.mx',    '$2b$12$HASH_TEMPORAL_CAMBIAR', 'operador_tanque'),
    ('Sergio Vargas',         'svargas_tanque@grupotrujano.mx',     '$2b$12$HASH_TEMPORAL_CAMBIAR', 'operador_tanque'),

    -- === OPERADORES DE MAQUINARIA (Tienen cuenta para interactuar, aunque el ing. puede registrar por ellos) ===
    ('Gerardo Ezequiel Piña', 'g_pina@grupotrujano.mx',     '$2b$12$HASH_TEMPORAL_CAMBIAR', 'ingeniero'), -- Usan rol ingeniero para la PWA
    ('Julián Piña Hernández', 'j_pina@grupotrujano.mx',     '$2b$12$HASH_TEMPORAL_CAMBIAR', 'ingeniero'),
    ('Edgar Rosales',         'e_rosales@grupotrujano.mx',  '$2b$12$HASH_TEMPORAL_CAMBIAR', 'ingeniero'),
    ('Adolfo Nava Lopez',     'a_nava@grupotrujano.mx',     '$2b$12$HASH_TEMPORAL_CAMBIAR', 'ingeniero'),
    ('Jose de Jesus Eusebio', 'j_eusebio@grupotrujano.mx',  '$2b$12$HASH_TEMPORAL_CAMBIAR', 'ingeniero'),
    ('Alan Alexis Gutierrez', 'a_gutierrez@grupotrujano.mx','$2b$12$HASH_TEMPORAL_CAMBIAR', 'ingeniero'),
    ('Fernando Angeles',      'f_angeles@grupotrujano.mx',  '$2b$12$HASH_TEMPORAL_CAMBIAR', 'ingeniero'),
    ('Jose Manuel Reyes',     'j_reyes@grupotrujano.mx',    '$2b$12$HASH_TEMPORAL_CAMBIAR', 'ingeniero'),
    ('Marco Antonio Estrada', 'm_estrada@grupotrujano.mx',  '$2b$12$HASH_TEMPORAL_CAMBIAR', 'ingeniero'),
    ('Eduardo Guadarrama',    'e_guadarrama@grupotrujano.mx','$2b$12$HASH_TEMPORAL_CAMBIAR', 'ingeniero'),

    -- === ADMINISTRADORES ===
    ('Administrador Sistema', 'admin@grupotrujano.mx',     '$2b$12$HASH_TEMPORAL_CAMBIAR', 'admin');

-- Asignar ingenieros responsables a sus obras
UPDATE fenix_obras SET responsable_id = (SELECT id FROM fenix_usuarios WHERE email = 'fjavier@grupotrujano.mx')
    WHERE iniciales = 'MT';
UPDATE fenix_obras SET responsable_id = (SELECT id FROM fenix_usuarios WHERE email = 'apolinar@grupotrujano.mx')
    WHERE iniciales = 'LT';
UPDATE fenix_obras SET responsable_id = (SELECT id FROM fenix_usuarios WHERE email = 'dcarreola@grupotrujano.mx')
    WHERE iniciales = 'BT';
UPDATE fenix_obras SET responsable_id = (SELECT id FROM fenix_usuarios WHERE email = 'janeth@grupotrujano.mx')
    WHERE iniciales = 'PAP';
UPDATE fenix_obras SET responsable_id = (SELECT id FROM fenix_usuarios WHERE email = 'luis@grupotrujano.mx')
    WHERE iniciales = 'PAH';

-- ============================================================
-- FIN DE DATOS INICIALES
-- ============================================================
