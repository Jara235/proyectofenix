"""
Normalizar obras en fenix_obras y reasignar movimientos a las obras canónicas.

MAPA DE CONSOLIDACIÓN:
- México-Toluca CANON: id=1 (México-Toluca)
  Duplicados: id=13 (OBRA MEXICO TOLUCA), id=18 (MEXICO-TOLUCA)
  
- Lerma - Tres Marías CANON: id=2 (Lerma - Tres Marías)
  Duplicados: id=4 (Lerma-Tenango), id=14 (LERMA TENANGO)
  NOTA: Lerma-Tenango != Lerma-Tres Marías. Lerma Tenango es la misma ruta que Lerma-Tres Marías
  
- Planta Huixquilucan CANON: id=6 (Planta Huixquilucan)
  Duplicados: id=20 (Planta Huixquilucan), id=15 (P.ASFALTO HUIX)
  
- Bacheo Toluca CANON: id=5 (Bacheo Toluca)
  Duplicados: id=12 (BACHEO TOLUCA Y CALLE VICENTE LOMBARDO TOLEDANO)
  
- Maquinaria CANON: id=21 (Maquinaria Pegaso) -> conservar separado
  Duplicados: id=7 (MAQUINARIA) -> reasignar a 21
"""
import sys, io, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
conn = sqlite3.connect('fenix.db')
cur = conn.cursor()

# Verificar cuántos registros tiene cada ID duplicado antes de tocar
check_ids = [13, 18, 4, 14, 20, 15, 12, 7]
for oid in check_ids:
    cur.execute("SELECT COUNT(*) FROM fenix_movimientos_combustible WHERE obra_id=?", (oid,))
    n_mov = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM fenix_viajes_acarreo WHERE obra_id=?", (oid,))
    n_ac = cur.fetchone()[0]
    cur.execute("SELECT nombre FROM fenix_obras WHERE id=?", (oid,))
    row = cur.fetchone()
    nombre = row[0] if row else "NOT FOUND"
    print(f"  id={oid} '{nombre}' -> movimientos={n_mov}, acarreos={n_ac}")

print("\nSin confirmar cambios aún. Ejecuta normalizar_obras_apply.py para aplicar.")
conn.close()
