# -*- coding: utf-8 -*-
import sys
sys.path.append(r'c:\Users\JOSE\Desktop\Proyecto fenix')
from app_admin import get_db

db = get_db()
semana = '29'
origen = 'Marimba M-01'
estatus = 'PENDIENTE'

# 1. Lerma - Tres Marías
registros_lerma = [
    ('2026-07-14', 'PERFILADORA RODATEC RX600-4-4008', 500.0),
    ('2026-07-14', 'PIPA DE AGUA (IMPACTO 01) FORD', 35.0),
    ('2026-07-14', 'PETROLIZADORA (IMPACTO 04) FORD', 75.0),
    ('2026-07-14', 'IMPACTO FORD 4300', 40.0),
    ('2026-07-14', 'PAVIMENTADORA VOGELE SJ 1800-3', 170.0),
    ('2026-07-14', 'NEUMATICO PF-300B', 75.0),
    ('2026-07-14', 'RETROEXCAVADORA JHONDEREE 310 K', 65.0),
    ('2026-07-14', 'BARREDORA LAYMOR SM400', 20.0),
    ('2026-07-14', 'VIBROCOMPACTADOR CATERPILLAR CB66B', 50.0),
    ('2026-07-17', 'PERFILADORA RODATEC RX600-4-4008', 290.0),
    ('2026-07-17', 'PIPA DE AGUA (IMPACTO 01) FORD', 113.0),
    ('2026-07-17', 'PETROLIZADORA (IMPACTO 04) FORD F800', 139.0),
    ('2026-07-17', 'PAVIMENTADORA VOGELE SJ 1800-3', 200.0),
    ('2026-07-17', 'NEUMATICO PF-300B', 69.0),
    ('2026-07-17', 'RETROEXCAVADORA JHONDEREE 310 K', 23.0),
    ('2026-07-17', 'BARREDORA LAYMOR SM400', 59.0),
    ('2026-07-17', 'COMPRESOR SULLIVAN PALATEK D2010', 105.0),
    ('2026-07-17', 'VIBROCOMPACTADOR CATERPILLAR CB66B', 115.0)
]

# (13/07/2026 REMOVED from Lerma)

for idx, (fecha, equipo, litros) in enumerate(registros_lerma):
    folio = f'GC-COMB-006-SEM29-LERMA-{idx+100:02d}' # changed index slightly to avoid any caching or ghost constraint issues
    db.execute('''INSERT INTO diesel.consumos (folio_conciliacion, fecha, semana, origen, obra_destino, equipo, litros, importe_total, operador, estatus_revision, tipo_movimiento)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 0.0, %s, %s, 'Salida')''', 
        (folio, fecha, semana, origen, 'Lerma - Tres Marías', equipo, litros, 'BRANDON', estatus))

# 2. Colegio Militar (All dates included, no duplicates found on 13th)
registros_colegio = [
    ('2026-07-13', 'PERFILADORA RODATEC RX600-4-4008', 90.0),
    ('2026-07-13', 'PIPA DE AGUA (IMPACTO 01) FORD', 50.0),
    ('2026-07-13', 'PETROLIZADORA (IMPACTO 04) FORD F800', 70.0),
    ('2026-07-13', 'IMPACTO FORD 4300', 50.0),
    ('2026-07-13', 'PAVIMENTADORA VOGELE SJ 1800-3', 195.0),
    ('2026-07-13', 'NEUMATICO PF-300B', 50.0),
    ('2026-07-13', 'RETROEXCAVADORA JHONDEREE 310 K', 50.0),
    ('2026-07-13', 'BARREDORA BROCE BROOM KR350', 28.0),
    ('2026-07-13', 'COMPRESOR SULLIVAN PALATEK D2010', 35.0),
    ('2026-07-13', 'VIBROCOMPACTADOR CATERPILLAR CB66B', 50.0),
    ('2026-07-14', 'PERFILADORA RODATEC RX600-4-4008', 500.0),
    ('2026-07-14', 'PIPA DE AGUA (IMPACTO 01) FORD', 35.0),
    ('2026-07-14', 'PETROLIZADORA (IMPACTO 04) FORD F800', 75.0),
    ('2026-07-14', 'IMPACTO FORD 4300', 40.0),
    ('2026-07-14', 'PAVIMENTADORA VOGELE SJ 1800-3', 150.0),
    ('2026-07-14', 'NEUMATICO PF-300B', 65.0),
    ('2026-07-14', 'RETROEXCAVADORA JHONDEREE 310 K', 65.0),
    ('2026-07-14', 'BARREDORA BROCE BROOM KR350', 20.0),
    ('2026-07-14', 'VIBROCOMPACTADOR CATERPILLAR CB66B', 50.0)
]

for idx, (fecha, equipo, litros) in enumerate(registros_colegio):
    folio = f'GC-COMB-006-SEM29-COLMIL-{idx+100:02d}'
    db.execute('''INSERT INTO diesel.consumos (folio_conciliacion, fecha, semana, origen, obra_destino, equipo, litros, importe_total, operador, estatus_revision, tipo_movimiento)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 0.0, %s, %s, 'Salida')''', 
        (folio, fecha, semana, origen, 'Colegio Militar', equipo, litros, 'BONICE', estatus))

# 3. Alfredo del Mazo
registros_alfredo = [
    ('2026-07-10', 'PAVIMENTADORA VOGELE 1800-3 I', 90.0),
    ('2026-07-10', 'RETROEXCAVADORA JHONDEREE 310SK', 30.0),
    ('2026-07-10', 'DOBLE RODILLO/VIBROCOMPACTADOR DE RODILLOS HAMM 120HD VV', 30.0),
    ('2026-07-10', 'NEUMATICO / COMPACTADOR DE NEUMATICOS DINAPAC', 30.0),
    ('2026-07-10', 'BARREDORA BROCE BROOM KR350', 20.0),
    ('2026-07-15', 'PERFILADORA RODATEC RX600-4-4008', 220.0),
    ('2026-07-15', 'RETROEXCAVADORA CASE 580 N', 100.0),
    ('2026-07-15', 'NEU.BOMAG', 50.0),
    ('2026-07-15', 'BARREDORA BROCE BROOM KR350', 30.0),
    ('2026-07-16', 'PERFILADORA RODATEC RX600-4-4008', 409.0),
    ('2026-07-16', 'RETROEXCAVADORA JHONDEREE 310SK', 127.0),
    ('2026-07-16', 'BARREDORA BROCE BROOM KR350', 51.0),
    ('2026-07-16', 'NEUMATICO VOLVO PT-240R', 13.0),
    ('2026-07-17', 'PERFILADORA RODATEC RX600-4-4008', 134.0),
    ('2026-07-17', 'RETROEXCAVADORA JHONDEREE 310SK', 102.0),
    ('2026-07-17', 'PIPA DE AGUA (IMPACTO 01) FORD', 46.0),
    ('2026-07-17', 'PETROLIZADORA (IMPACTO 04) FORD F800', 60.0),
    ('2026-07-17', 'PAVIMENTADORA VOGELE 1800-3 I', 198.0),
    ('2026-07-17', 'COMPRESOR SULLIVAN PALATEK D2010', 33.0),
    ('2026-07-17', 'BARREDORA LAYMOR SM400', 50.0),
    ('2026-07-17', 'PF-300B', 40.0),
    ('2026-07-17', 'CATERPILLAR CB66B', 87.0)
]
# (13/07/2026 REMOVED from Alfredo)

for idx, (fecha, equipo, litros) in enumerate(registros_alfredo):
    folio = f'GC-COMB-006-SEM29-ALFREDO-{idx+100:02d}'
    db.execute('''INSERT INTO diesel.consumos (folio_conciliacion, fecha, semana, origen, obra_destino, equipo, litros, importe_total, operador, estatus_revision, tipo_movimiento)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 0.0, %s, %s, 'Salida')''', 
        (folio, fecha, semana, origen, 'Alfredo del Mazo', equipo, litros, 'BONICE, CRISTIAN REYES Y EDGAR', estatus))

db.commit()
db.close()
print("Inserción limpia completada.")
