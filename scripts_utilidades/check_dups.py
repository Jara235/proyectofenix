# -*- coding: utf-8 -*-
import sys
sys.path.append(r'c:\Users\JOSE\Desktop\Proyecto fenix')
from app_admin import get_db

db = get_db()

existing = db.execute('''
    SELECT fecha::text, obra_destino, equipo, litros 
    FROM diesel.consumos 
    WHERE semana = '29' 
      AND fecha IN ('2026-07-10', '2026-07-13')
      AND obra_destino IN ('Lerma - Tres Marías', 'Colegio Militar', 'Alfredo del Mazo')
      AND folio_conciliacion NOT LIKE 'GC-COMB-006-SEM29-LERMA-%%'
      AND folio_conciliacion NOT LIKE 'GC-COMB-006-SEM29-COLMIL-%%'
      AND folio_conciliacion NOT LIKE 'GC-COMB-006-SEM29-ALFREDO-%%'
''').fetchall()

print(f"Encontrados {len(existing)} registros previos en la BD para los dias 10 y 13.")
for row in existing:
    print("  ->", dict(row))

db.execute('''
    DELETE FROM diesel.consumos 
    WHERE folio_conciliacion LIKE 'GC-COMB-006-SEM29-LERMA-%%'
       OR folio_conciliacion LIKE 'GC-COMB-006-SEM29-COLMIL-%%'
       OR folio_conciliacion LIKE 'GC-COMB-006-SEM29-ALFREDO-%%'
''')
print("Eliminados los registros recien insertados.")
db.commit()
db.close()
