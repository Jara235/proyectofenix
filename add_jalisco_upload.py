import sys
import re

with open(r'c:\Users\JOSE\Desktop\Proyecto fenix\app_admin.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_endpoint = """
@app.route('/api/admin/jalisco/upload_pdf', methods=['POST'])
def api_admin_jalisco_upload_pdf():
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
        
        # Guardar en bytes para la base de datos
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
        
        return jsonify({'message': f'Migración exitosa. Se guardaron {inserted} consumos nuevos.'})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
"""

if "def api_admin_jalisco_upload_pdf" not in content:
    # Insert before the run block
    content = content.replace("if __name__ == '__main__':", new_endpoint + "\nif __name__ == '__main__':")
    with open(r'c:\Users\JOSE\Desktop\Proyecto fenix\app_admin.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Endpoint added.")
else:
    print("Endpoint already exists.")
