# -*- coding: utf-8 -*-
"""
SISTEMA FENIX -- Inicializador de Base de Datos v1.0
====================================================
Crea fenix.db con toda la estructura y datos de catalogo reales.
Uso: python inicializar_fenix.py
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import sqlite3
import os

# Ruta del proyecto
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
DB_PATH   = os.path.join(BASE_DIR, "fenix.db")
SQL_PATH  = os.path.join(BASE_DIR, "fenix_schema.sql")

VERDE  = "\033[92m"
ROJO   = "\033[91m"
CYAN   = "\033[96m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

def log_ok(msg):  print(f"  {VERDE}✔ {msg}{RESET}")
def log_err(msg): print(f"  {ROJO}✘ {msg}{RESET}")
def log_info(msg):print(f"  {CYAN}→ {msg}{RESET}")


def crear_estructura(conn):
    """Lee y ejecuta el archivo SQL del esquema."""
    log_info(f"Leyendo esquema desde: {SQL_PATH}")
    if not os.path.exists(SQL_PATH):
        log_err("No se encontró fenix_schema.sql — ejecuta este script desde la carpeta del proyecto.")
        sys.exit(1)

    with open(SQL_PATH, 'r', encoding='utf-8') as f:
        sql = f.read()

    conn.executescript(sql)
    conn.commit()
    log_ok("Estructura de tablas creada correctamente.")


def cargar_catalogos(conn):
    """Inserta los catálogos base reales de Grupo Trujano."""
    cur = conn.cursor()

    # ---- OBRAS ----
    obras = [
        ('MT',  'México-Toluca'),
        ('L3M', 'Lerma - Tres Marías'),
        ('CL',  'Chamapa-Lechería'),
        ('LT',  'Lerma-Tenango'),
        ('BTL', 'Bacheo Toluca'),
        ('HX',  'Planta Huixquilucan'),
    ]
    cur.executemany(
        "INSERT OR IGNORE INTO fenix_obras (codigo, nombre) VALUES (?, ?)",
        obras
    )
    log_ok(f"{len(obras)} Obras cargadas.")

    # ---- SINDICATOS ----
    sindicatos = [
        ('COSUM TOLUCA',),
        ('OBRAS PUBLICAS',),
        ('CROM',),
        ('INDEPENDIENTE',),
    ]
    cur.executemany(
        "INSERT OR IGNORE INTO fenix_sindicatos (nombre) VALUES (?)",
        sindicatos
    )
    log_ok(f"{len(sindicatos)} Sindicatos cargados.")

    # ---- EQUIPOS (identificados por Número Económico / Unidad) ----
    #  (numero_economico, descripcion, tipo_equipo, tipo_combustible, tipo_rendimiento)
    equipos = [
        # Maquinaria Pesada — Diésel
        ('PER-200',  'Perfiladora Wirtgen W-200',         'Perfiladora',       'Diesel',   'horas'),
        ('VOG-03',   'Pavimentadora Vögele-03',           'Pavimentadora',     'Diesel',   'horas'),
        ('HAMM-01',  'Compactador Tándem Hamm',           'Compactador',       'Diesel',   'horas'),
        ('DINA-01',  'Compactador Neumático Dynapac',     'Compactador',       'Diesel',   'horas'),
        ('BAR-01',   'Barredora Broce Broom',             'Barredora',         'Diesel',   'horas'),
        ('RET-02',   'Retroexcavadora CAT',               'Retroexcavadora',   'Diesel',   'horas'),
        ('PET-02',   'Petrolizadora',                     'Petrolizadora',     'Diesel',   'horas'),
        ('FR-01',    'Fresadora Wirtgen',                 'Fresadora',         'Diesel',   'horas'),
        ('CR-01',    'Cargador Frontal',                  'Cargador',          'Diesel',   'horas'),
        ('EX-01',    'Excavadora',                        'Excavadora',        'Diesel',   'horas'),
        ('CP-01',    'Compactador Pata de Cabra',         'Compactador',       'Diesel',   'horas'),
        ('COM-01',   'Compresor Ingersoll Rand',          'Compresor',         'Diesel',   'horas'),
        ('TL-01',    'Torre de Luces Maxilight',          'Torre de Luces',    'Diesel',   'horas'),
        # Pipas y Camiones de Diésel
        ('PP-01',    'Pipa Agua',                         'Pipa',              'Diesel',   'kilometros'),
        ('CAM-02',   'Camión Impacto',                    'Camión',            'Diesel',   'kilometros'),
        # Marimba / Tanque (consumen diésel para operar)
        ('MAR-01',   'Marimba M-01 (Planta Móvil)',       'Planta Móvil',      'Diesel',   'horas'),
        # Vehículos de Gasolina
        ('PEG-01',   'Pickup Pegaso 1',                   'Pickup',            'Gasolina', 'kilometros'),
        ('PEG-02',   'Pickup Pegaso 2',                   'Pickup',            'Gasolina', 'kilometros'),
        ('RAM-01',   'RAM 1500 Supervisión',              'Pickup',            'Gasolina', 'kilometros'),
        ('MZ-01',    'Mazda Supervisión',                 'Camioneta',         'Gasolina', 'kilometros'),
        ('CAM-01',   'Camioneta Campo 1',                 'Camioneta',         'Gasolina', 'kilometros'),
        ('CAM-03',   'Camioneta Campo 3',                 'Camioneta',         'Gasolina', 'kilometros'),
        ('ING-01',   'Vehículo Ingeniería 1',             'Camioneta',         'Gasolina', 'kilometros'),
    ]
    cur.executemany(
        """INSERT OR IGNORE INTO fenix_equipos
           (numero_economico, descripcion, tipo_equipo, tipo_combustible, tipo_rendimiento)
           VALUES (?, ?, ?, ?, ?)""",
        equipos
    )
    log_ok(f"{len(equipos)} Equipos/Unidades cargados.")

    # ---- CONTENEDORES DE COMBUSTIBLE ----
    contenedores = [
        ('Tanque Pegaso',       'Tanque',  20000),
        ('Marimba M-01',        'Marimba', 5000),
        ('Bidón Lerma-Tenango', 'Bidon',   200),
        ('Bidón Chamapa',       'Bidon',   200),
        ('Bidón Huixquilucan',  'Bidon',   200),
        ('Pipa Cisterna',       'Pipa',    10000),
    ]
    cur.executemany(
        """INSERT OR IGNORE INTO fenix_contenedores
           (nombre, tipo, capacidad_litros)
           VALUES (?, ?, ?)""",
        contenedores
    )
    log_ok(f"{len(contenedores)} Contenedores cargados.")

    conn.commit()


def insertar_datos_prueba(conn):
    """
    Inserta un ciclo completo de prueba para verificar la conciliación:
    1. Factura de gasolinera
    2. COMPRA: Gasolinera → Marimba M-01 (Diésel)
    3. CONSUMO: Marimba M-01 → Perfiladora PER-200
    4. COMPRA de Gasolina: Gasolinera → Bidón Chamapa
    5. CONSUMO Gasolina: Bidón → Pickup PEG-01
    6. Viajes de Acarreo de COSUM TOLUCA
    """
    cur = conn.cursor()

    # IDs dinámicos
    cur.execute("SELECT id FROM fenix_obras WHERE codigo = 'MT'")
    id_mt = cur.fetchone()[0]
    cur.execute("SELECT id FROM fenix_obras WHERE codigo = 'CL'")
    id_cl = cur.fetchone()[0]
    cur.execute("SELECT id FROM fenix_sindicatos WHERE nombre = 'COSUM TOLUCA'")
    id_cosum = cur.fetchone()[0]
    cur.execute("SELECT id FROM fenix_equipos WHERE numero_economico = 'PER-200'")
    id_per = cur.fetchone()[0]
    cur.execute("SELECT id FROM fenix_equipos WHERE numero_economico = 'PEG-01'")
    id_peg1 = cur.fetchone()[0]

    # 1. Factura de Diésel
    cur.execute("""
        INSERT INTO fenix_facturas_combustible
            (folio_factura, proveedor, tipo_combustible, fecha_emision,
             litros_amparados, precio_unitario, subtotal, iva, importe_total)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ('F-10021', 'Gasolinera Huixquilucan', 'Diesel', '2026-06-30',
          3000, 27.50, 82500.00, 13200.00, 95700.00))
    factura_diesel_id = cur.lastrowid

    # 2. COMPRA: Gasolinera → Marimba M-01
    cur.execute("""
        INSERT INTO fenix_movimientos_combustible
            (tipo_movimiento, fecha, semana, factura_id,
             origen_tipo, origen_nombre, destino_tipo, destino_nombre,
             obra_id, litros, precio_unitario)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, ('COMPRA','2026-06-30', 27, factura_diesel_id,
          'Gasolinera','Gasolinera Huixquilucan',
          'Marimba','Marimba M-01',
          id_mt, 3000, 27.50))

    # 3. CONSUMO: Marimba M-01 → Perfiladora
    cur.execute("""
        INSERT INTO fenix_movimientos_combustible
            (tipo_movimiento, fecha, semana,
             origen_tipo, origen_nombre, destino_tipo, destino_nombre,
             equipo_id, obra_id, litros, precio_unitario, rendimiento, folio_vale)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, ('CONSUMO','2026-06-30', 27,
          'Marimba','Marimba M-01',
          'Equipo','PER-200',
          id_per, id_mt, 240, 27.50, 8.5, 'VALE-0901'))

    # 4. Factura de Gasolina
    cur.execute("""
        INSERT INTO fenix_facturas_combustible
            (folio_factura, proveedor, tipo_combustible, fecha_emision,
             litros_amparados, precio_unitario, subtotal, iva, importe_total)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ('F-TK-441', 'Estación Chamapa', 'Gasolina', '2026-06-30',
          200, 24.80, 4960.00, 793.60, 5753.60))
    factura_gas_id = cur.lastrowid

    # 5. COMPRA Gasolina: Gasolinera → Bidón Chamapa
    cur.execute("""
        INSERT INTO fenix_movimientos_combustible
            (tipo_movimiento, fecha, semana, factura_id,
             origen_tipo, origen_nombre, destino_tipo, destino_nombre,
             obra_id, litros, precio_unitario)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, ('COMPRA','2026-06-30', 27, factura_gas_id,
          'Gasolinera','Estación Chamapa',
          'Bidon','Bidón Chamapa',
          id_cl, 200, 24.80))

    # 6. CONSUMO Gasolina: Bidón → Pickup
    cur.execute("""
        INSERT INTO fenix_movimientos_combustible
            (tipo_movimiento, fecha, semana,
             origen_tipo, origen_nombre, destino_tipo, destino_nombre,
             equipo_id, obra_id, litros, precio_unitario, rendimiento, folio_vale)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, ('CONSUMO','2026-06-30', 27,
          'Bidon','Bidón Chamapa',
          'Equipo','PEG-01',
          id_peg1, id_cl, 45, 24.80, 420.0, 'VALE-GAS-012'))

    # 7. Viajes de Acarreo de prueba (Semana 27, COSUM TOLUCA, México-Toluca)
    # (folio, fecha, semana, obra_id, sindicato_id, material, categoria, placa, capacidad_m3, costo_unitario, subtotal, iva)
    viajes = [
        ('SEM27-001','2026-06-30', 27, id_mt, id_cosum, 'Mezcla Asfaltica', 'Mezcla', 'LD57526', 7.0, 1250.00, 8750.00, 0.00),
        ('SEM27-002','2026-06-30', 27, id_mt, id_cosum, 'Mezcla Asfaltica', 'Mezcla', 'LD57527', 7.0, 1250.00, 8750.00, 0.00),
        ('SEM27-003','2026-06-30', 27, id_mt, id_cosum, 'Material Fresado',  'Fresado','LD57530', 8.5,  980.00, 8330.00, 0.00),
    ]
    cur.executemany("""
        INSERT INTO fenix_viajes_acarreo
            (folio, fecha, semana, obra_id, sindicato_id, material, categoria,
             placa, capacidad_m3, costo_unitario, subtotal, iva)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """, viajes)

    conn.commit()
    log_ok(f"Datos de prueba insertados: 2 facturas, 4 movimientos de combustible, {len(viajes)} viajes de acarreo.")


def verificar_conciliacion(conn):
    """Muestra las vistas de conciliación para confirmar que todo cuadra."""
    cur = conn.cursor()

    print(f"\n{BOLD}{CYAN}── CONCILIACIÓN DE FACTURAS ────────────────────────────{RESET}")
    cur.execute("SELECT folio_factura, proveedor, litros_facturados, litros_registrados, diferencia_litros, estatus_pago FROM v_conciliacion_facturas")
    rows = cur.fetchall()
    print(f"  {'Folio':<12} {'Proveedor':<30} {'L.Fact':>8} {'L.Reg':>8} {'Dif':>8} {'Estatus'}")
    print(f"  {'-'*75}")
    for r in rows:
        print(f"  {str(r[0]):<12} {str(r[1]):<30} {str(r[2]):>8} {str(r[3]):>8} {str(r[4]):>8} {str(r[5])}")

    print(f"\n{BOLD}{CYAN}── BALANCE DE CONTENEDORES ─────────────────────────────{RESET}")
    cur.execute("SELECT contenedor, litros_en_existencia FROM v_balance_contenedores")
    rows = cur.fetchall()
    for r in rows:
        print(f"  {str(r[0]):<30} {str(r[1]):>10} litros")

    print(f"\n{BOLD}{CYAN}── ESTIMACIÓN DE PAGOS A SINDICATOS ────────────────────{RESET}")
    cur.execute("SELECT sindicato, obra, semana, categoria, total_viajes, total_a_pagar FROM v_estimacion_pagos_sindicatos")
    rows = cur.fetchall()
    print(f"  {'Sindicato':<20} {'Obra':<20} {'Sem':>4} {'Categ.':<12} {'Viajes':>6} {'Total a Pagar':>14}")
    print(f"  {'-'*80}")
    for r in rows:
        print(f"  {str(r[0]):<20} {str(r[1]):<20} {str(r[2]):>4} {str(r[3]):<12} {str(r[4]):>6} ${float(r[5]):>13,.2f}")


def main():
    print(f"\n{BOLD}{'='*55}")
    print(f"  [FENIX] SISTEMA FENIX -- Inicializador de Base de Datos v1.0")
    print(f"{'='*55}{RESET}\n")

    log_info(f"Base de datos: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        print(f"\n{BOLD}[1/4] Creando estructura de tablas...{RESET}")
        crear_estructura(conn)

        print(f"\n{BOLD}[2/4] Cargando catalogos reales...{RESET}")
        cargar_catalogos(conn)

        print(f"\n{BOLD}[3/4] Insertando datos de prueba...{RESET}")
        insertar_datos_prueba(conn)

        print(f"\n{BOLD}[4/4] Verificando conciliacion...{RESET}")
        verificar_conciliacion(conn)

        print(f"\n{VERDE}{BOLD}{'='*55}")
        print(f"  [OK] BASE DE DATOS CREADA EXITOSAMENTE")
        print(f"  [DB] Archivo: fenix.db")
        print(f"  [>>] 8 tablas + 4 vistas de conciliacion")
        print(f"{'='*55}{RESET}\n")

    except Exception as e:
        log_err(f"Error durante la inicializacion: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
