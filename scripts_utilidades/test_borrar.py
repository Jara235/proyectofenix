import urllib.request
import json

req = urllib.request.Request('http://127.0.0.1:5002/api/admin/borrar_registro', 
    data=json.dumps({'tabla': 'diesel.consumos', 'id': "152"}).encode('utf-8'),
    headers={'Content-Type': 'application/json'})

try:
    with urllib.request.urlopen(req) as response:
        print("Response:", response.status, response.read().decode())
except Exception as e:
    print("Error:", e)

import psycopg2
conn = psycopg2.connect(dbname='fenix_db', user='postgres', password='Bupito*268', host='localhost')
cur = conn.cursor()
cur.execute("SELECT id FROM diesel.consumos WHERE id = 152")
print("Row 152 after:", cur.fetchall())
