# -*- coding: utf-8 -*-
"""
Migración: Agrega columna tipo_combustible a fenix_movimientos_combustible
y clasifica cada registro correctamente (Diesel vs Gasolina)
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import sqlite3, os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fenix.db")

def run():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1. Agregar columna tipo_combustible si no existe
    try:
        cur.execute("ALTER TABLE fenix_movimientos_combustible ADD COLUMN tipo_combustible TEXT DEFAULT 'Diesel'")
        print("Columna tipo_combustible agregada.")
    except Exception:
        print("Columna tipo_combustible ya existe, actualizando valores...")

    # 2. Clasificar por origen:
    # GASOLINA: origen_tipo='Gasolinera' (esos son los consumos de gasolina de las unidades)
    cur.execute("""
        UPDATE fenix_movimientos_combustible
        SET tipo_combustible = 'Gasolina'
        WHERE origen_tipo = 'Gasolinera'
    """)
    g_count = cur.rowcount

    # DIESEL: Tanque Pegaso, Marimba, Bidon, Pipa -> es Diesel
    cur.execute("""
        UPDATE fenix_movimientos_combustible
        SET tipo_combustible = 'Diesel'
        WHERE origen_tipo IN ('Tanque', 'Marimba', 'Bidon', 'Pipa')
    """)
    d_count = cur.rowcount

    # 3. Agregar columna tipo_combustible a fenix_facturas_documentos si no existe
    try:
        cur.execute("ALTER TABLE fenix_facturas_documentos ADD COLUMN tipo_combustible TEXT DEFAULT 'Diesel'")
        print("Columna tipo_combustible en facturas_documentos agregada.")
    except:
        print("Columna tipo_combustible en facturas_documentos ya existe.")

    # 4. Clasificar facturas documentales:
    # Los XML de "DERIVADOS DE PETROLEO CASTILLA" son Diesel (tanque pegaso)
    cur.execute("""
        UPDATE fenix_facturas_documentos
        SET tipo_combustible = 'Diesel'
        WHERE emisor_nombre LIKE '%PETROLEO%' OR emisor_nombre LIKE '%DIESEL%' OR emisor_nombre LIKE '%DERIVADOS%'
    """)

    conn.commit()

    # 5. Reporte
    cur.execute("SELECT tipo_combustible, COUNT(*), ROUND(SUM(litros),1) FROM fenix_movimientos_combustible GROUP BY tipo_combustible")
    print("\n=== Movimientos por tipo de combustible ===")
    for r in cur.fetchall():
        print(f"  {r[0]}: {r[1]} registros, {r[2]} litros")

    cur.execute("SELECT tipo_combustible, COUNT(*), ROUND(SUM(litros_totales),1), ROUND(SUM(total),2) FROM fenix_facturas_documentos GROUP BY tipo_combustible")
    print("\n=== Facturas documentales por tipo ===")
    for r in cur.fetchall():
        print(f"  {r[0]}: {r[1]} facturas, {r[2]} litros, ${r[3]:,.2f}")

    conn.close()

if __name__ == "__main__":
    run()
