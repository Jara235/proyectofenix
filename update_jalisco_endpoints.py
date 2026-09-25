import sys
import re

with open(r'c:\Users\JOSE\Desktop\Proyecto fenix\app_admin.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the old api_admin_jalisco_upload_pdf endpoint
old_endpoint_pattern = re.compile(r"@app\.route\('/api/admin/jalisco/upload_pdf'.*?(?=@app\.route|if __name__ == '__main__':)", re.DOTALL)
content = old_endpoint_pattern.sub('', content)

new_endpoints = """
@app.route('/admin/jalisco/subir')
def admin_jalisco_subir():
    return render_template('admin/admin_jalisco_subir.html')

@app.route('/api/admin/jalisco/preview_pdf', methods=['POST'])
def api_admin_jalisco_preview_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    try:
        import os
        import tempfile
        import base64
        from servidor.parser_jalisco import extraer_pdf_jalisco
        
        fd, temp_path = tempfile.mkstemp(suffix='.pdf')
        os.close(fd)
        file.save(temp_path)
        
        # Guardar en bytes para la base de datos (luego se lo pasamos al frontend o lo cacheamos, pero como no podemos mantener estado fcilmente, devolveremos base64 o le pediremos que vuelva a subir)
        # Una mejor forma es devolver un resumen, y cuando confirme, vuelve a enviar el archivo o el JSON
        
        datos = extraer_pdf_jalisco(temp_path)
        os.remove(temp_path)
        
        return jsonify({'success': True, 'data': datos})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/jalisco/confirm_upload', methods=['POST'])
def api_admin_jalisco_confirm_upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    try:
        import os
        import tempfile
        from servidor.parser_jalisco import extraer_pdf_jalisco
        
        fd, temp_path = tempfile.mkstemp(suffix='.pdf')
        os.close(fd)
        file.save(temp_path)
        
        with open(temp_path, 'rb') as f_pdf:
            pdf_bytes = f_pdf.read()
            
        datos = extraer_pdf_jalisco(temp_path)
        os.remove(temp_path)
        
        semana = datos.get('semana', 0)
        
        db = get_db()
        inserted = 0
        
        for c in datos['consumos']:
            fecha = c['fecha']
            equipo = c['equipo']
            litros = c['litros']
            costo = c['costo_por_litro']
            tipo = c['tipo_combustible']
            importe = litros * costo
            
            # Ver si ya existe para evitar duplicados
            exist = db.execute("SELECT id FROM diesel.jalisco_movimientos WHERE fecha=%s AND equipo=%s AND litros=%s AND tipo_movimiento='SALIDA'", (fecha, equipo, litros)).fetchone()
            if exist: continue
            
            # Obtener saldo_teorico anterior del mismo tipo de combustible
            last = db.execute("SELECT saldo_teorico FROM diesel.jalisco_movimientos WHERE tipo_combustible=%s ORDER BY id DESC LIMIT 1", (tipo,)).fetchone()
            saldo_anterior = float(last['saldo_teorico']) if last and last['saldo_teorico'] is not None else 0.0
            nuevo_saldo = saldo_anterior - litros
            
            db.execute('''
                INSERT INTO diesel.jalisco_movimientos 
                (fecha, semana, tipo_movimiento, equipo, litros, costo_por_litro, importe_total, saldo_teorico, tipo_combustible, archivo_pdf)
                VALUES (%s, %s, 'SALIDA', %s, %s, %s, %s, %s, %s, %s)
            ''', (fecha, semana, equipo, litros, costo, importe, nuevo_saldo, tipo, pdf_bytes))
            
            inserted += 1
            
        db.connection.commit()
        db.close()
        
        return jsonify({'success': True, 'message': f'Migración exitosa. Se guardaron {inserted} consumos nuevos.'})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
"""

content = content.replace("if __name__ == '__main__':", new_endpoints + "\nif __name__ == '__main__':")

with open(r'c:\Users\JOSE\Desktop\Proyecto fenix\app_admin.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Endpoints replaced.")
