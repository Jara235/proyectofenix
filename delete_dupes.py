# -*- coding: utf-8 -*-
import sys
sys.path.append(r'c:\Users\JOSE\Desktop\Proyecto fenix')
from app_admin import get_db
db = get_db()

# Borrar todas las solicitudes de la importación masiva duplicada que empiezan con SOL-D-2026...
# Esto incluye los 5 aprobados por error y los 22 que se quedaron en pendiente.
db.execute("DELETE FROM diesel.solicitudes WHERE folio_solicitud LIKE 'SOL-D-2026%%'")
db.commit()

print("Duplicados eliminados exitosamente de la base de datos.")
db.close()
