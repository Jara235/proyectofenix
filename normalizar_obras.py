"""
Normalización de Obras en fenix_obras.

MAPA FINAL (basado en lo que el usuario confirmó):
- México-Toluca = id=1  | Consolida: OBRA MEXICO TOLUCA(13), MEXICO-TOLUCA(18)
- Lerma - Tres Marías = id=2 | Consolida: Lerma-Tenango(4), LERMA TENANGO(14)
- Planta Huixquilucan = id=6 | Consolida: Planta Huixquilucan duplicado(20), P.ASFALTO HUIX(15)
- Bacheo Toluca = id=5 | Consolida: BACHEO TOLUCA Y CALLE VICENTE LOMBARDO(12)
- Maquinaria Pegaso = id=21 | Consolida: MAQUINARIA(7)
- LERMA TENANGO registros de movimientos -> reasignar a Lerma-Tres Marías (id=2)
- MEXICO-TOLUCA acarreos (140) -> reasignar a México-Toluca (id=1)
"""
import sys, io, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
conn = sqlite3.connect('fenix.db')
cur = conn.cursor()

# MAPA: [viejo_id] -> [nuevo_id canónico]
REMAP = {
    13: 1,   # OBRA MEXICO TOLUCA -> México-Toluca
    18: 1,   # MEXICO-TOLUCA -> México-Toluca  (tiene 140 acarreos)
    4: 2,    # Lerma-Tenango -> Lerma - Tres Marías
    14: 2,   # LERMA TENANGO -> Lerma - Tres Marías  (tiene 7 movimientos)
    20: 6,   # Planta Huixquilucan (dup) -> Planta Huixquilucan (6)
    15: 6,   # P.ASFALTO HUIX -> Planta Huixquilucan (6)
    12: 5,   # BACHEO TOLUCA Y CALLE... -> Bacheo Toluca (5)
    7: 21,   # MAQUINARIA -> Maquinaria Pegaso (21)
    11: 11,  # EXPLANADA DAMIAN CARMONA -> conservar
}

# Reasignar movimientos_combustible
for old_id, new_id in REMAP.items():
    if old_id == new_id: continue
    cur.execute("UPDATE fenix_movimientos_combustible SET obra_id=? WHERE obra_id=?", (new_id, old_id))
    if cur.rowcount > 0:
        print(f"  Movimientos: id={old_id} -> {new_id} ({cur.rowcount} filas)")

# Reasignar viajes_acarreo
for old_id, new_id in REMAP.items():
    if old_id == new_id: continue
    cur.execute("UPDATE fenix_viajes_acarreo SET obra_id=? WHERE obra_id=?", (new_id, old_id))
    if cur.rowcount > 0:
        print(f"  Acarreos: id={old_id} -> {new_id} ({cur.rowcount} filas)")

# Reasignar equipos
for old_id, new_id in REMAP.items():
    if old_id == new_id: continue
    cur.execute("UPDATE fenix_equipos SET obra_id=? WHERE obra_id=?", (new_id, old_id))
    if cur.rowcount > 0:
        print(f"  Equipos: id={old_id} -> {new_id} ({cur.rowcount} filas)")

# Reasignar horas_trabajo
for old_id, new_id in REMAP.items():
    if old_id == new_id: continue
    cur.execute("UPDATE fenix_horas_trabajo SET obra_id=? WHERE obra_id=?", (new_id, old_id))
    if cur.rowcount > 0:
        print(f"  Horas: id={old_id} -> {new_id} ({cur.rowcount} filas)")

# Desactivar los duplicados (no borrar, por seguridad)
ids_to_deactivate = list(REMAP.keys())
cur.execute(f"UPDATE fenix_obras SET activa=0 WHERE id IN ({','.join(['?']*len(ids_to_deactivate))})", ids_to_deactivate)
print(f"\n  Obras desactivadas (duplicados): {ids_to_deactivate}")

# Actualizar nombres canónicos para que sean más legibles
canonical_names = {
    1: 'México-Toluca',
    2: 'Lerma - Tres Marías',
    5: 'Bacheo Toluca',
    6: 'Planta Huixquilucan',
    21: 'Maquinaria Pegaso',
    19: 'Planta Pegaso',
    3: 'Chamapa-Lechería',
}
for id_val, name in canonical_names.items():
    cur.execute("UPDATE fenix_obras SET nombre=? WHERE id=?", (name, id_val))
    print(f"  Renombrado id={id_val} -> '{name}'")

conn.commit()
conn.close()

print("\n✅ Normalización completada")
print("Verificando resultado final...")

import sqlite3
conn2 = sqlite3.connect('fenix.db')
conn2.row_factory = sqlite3.Row
cur2 = conn2.cursor()
cur2.execute("""
    SELECT COALESCE(o.nombre,'Sin asignar') as obra, ROUND(SUM(m.litros),1) as lts, COUNT(*) as n
    FROM fenix_movimientos_combustible m
    LEFT JOIN fenix_obras o ON o.id = m.obra_id
    WHERE m.tipo_movimiento='CONSUMO' AND m.tipo_combustible='Diesel'
    GROUP BY m.obra_id ORDER BY lts DESC
""")
print("\n=== DIESEL POR OBRA (post-normalización) ===")
for r in cur2.fetchall():
    print(f"  {r['obra']}: {r['lts']} L ({r['n']} regs)")
conn2.close()
