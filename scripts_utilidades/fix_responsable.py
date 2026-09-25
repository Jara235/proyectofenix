# -*- coding: utf-8 -*-
import sys
sys.path.append(r'c:\Users\JOSE\Desktop\Proyecto fenix')
from app_admin import get_db

db = get_db()
db.execute("UPDATE catalogos.obras SET responsable_default = 'Cristian Reyes' WHERE nombre = 'México - Toluca'")
db.commit()
db.close()
print("Updated responsable_default for México - Toluca")
