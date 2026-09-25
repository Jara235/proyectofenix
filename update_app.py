import re

html_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\app_captura.py'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

new_endpoint = '''@app.route('/api/diesel/facturas_batch', methods=['POST'])
def api_post_facturas_batch():
    try:
        data = request.json
        db = get_db()
        for c in data['cargas']:
            db.execute("""INSERT INTO diesel_consumos 
                (folio_conciliacion, fecha, origen, tipo_movimiento, obra_destino, equipo, litros, costo_por_litro, importe_total, observaciones)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
                data['uuid'], data['fecha'], 'FACTURA', 'CONSUMO', data['obra'], c['descripcion'], c['litros'], c['precio'], c['total'], 'Importado automáticamente via XML'
            ))
        db.commit()
        db.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

'''

html = html.replace('@app.route(' + "'/api/diesel/consumo', methods=['POST'])", new_endpoint + "@app.route('/api/diesel/consumo', methods=['POST'])")

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
