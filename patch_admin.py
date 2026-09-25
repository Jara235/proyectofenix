import os

file_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\app_admin.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_endpoint = """
@app.route('/api/admin/aprobar_batch', methods=['POST'])
def api_aprobar_batch():
    try:
        data = request.json
        tabla = data.get('tabla')
        ids = data.get('ids', [])
        nuevo_estatus = data.get('estatus', 'APROBADO')
        
        tablas_permitidas = ['diesel.consumos', 'diesel.facturas', 'diesel.solicitudes', 'gasolina.consumos', 'gasolina.facturas', 'gasolina.solicitudes']
        if tabla not in tablas_permitidas or not ids:
            return jsonify({'success': False, 'error': 'Datos inválidos'})
            
        col_estatus = 'estatus_conciliacion' if 'solicitudes' in tabla else 'estatus_revision'
        
        db = get_db()
        # Verificar duplicados si estamos aprobando
        if nuevo_estatus == 'APROBADO':
            for id_reg in ids:
                # Obtener info del registro
                row = db.execute(f"SELECT * FROM {tabla} WHERE id = %s", (id_reg,)).fetchone()
                if not row: continue
                
                # Armar condiciones segun la tabla
                dup_query = None
                dup_params = None
                
                if 'consumos' in tabla:
                    dup_query = f"SELECT id FROM {tabla} WHERE fecha = %s AND litros = %s AND obra_destino = %s AND id != %s AND {col_estatus} = 'APROBADO'"
                    dup_params = (row['fecha'], row['litros'], row['obra_destino'], id_reg)
                elif 'facturas' in tabla:
                    dup_query = f"SELECT id FROM {tabla} WHERE fecha_factura = %s AND litros_facturados = %s AND proveedor = %s AND id != %s AND {col_estatus} = 'APROBADO'"
                    dup_params = (row['fecha_factura'], row['litros_facturados'], row['proveedor'], id_reg)
                elif 'solicitudes' in tabla:
                    dup_query = f"SELECT id FROM {tabla} WHERE fecha = %s AND litros = %s AND importe_total = %s AND obra_destino = %s AND id != %s AND {col_estatus} = 'APROBADO'"
                    dup_params = (row['fecha'], row['litros'], row['importe_total'], row['obra_destino'], id_reg)
                    
                if dup_query:
                    dup = db.execute(dup_query, dup_params).fetchone()
                    if dup:
                        db.close()
                        return jsonify({
                            'success': False, 
                            'duplicateWarning': True, 
                            'error': f'Se detectó un registro ya aprobado casi idéntico. Verifica la información antes de aprobar para evitar duplicados.'
                        })
        
        # Proceder a actualizar
        format_strings = ','.join(['%s'] * len(ids))
        db.execute(f"UPDATE {tabla} SET {col_estatus} = %s WHERE id IN ({format_strings})", [nuevo_estatus] + ids)
        db.commit()
        db.close()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

"""

if '@app.route(\'/api/admin/aprobar_batch\'' not in content:
    target = "def api_actualizar_estatus():"
    idx = content.find("def api_borrar_registro():")
    if idx != -1:
        # insert before api_borrar_registro
        idx = content.rfind("@app.route('/api/admin/borrar_registro'", 0, idx)
        content = content[:idx] + new_endpoint + "\n" + content[idx:]
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Endpoint added.")
    else:
        print("Could not find insertion point.")
else:
    print("Endpoint already exists.")
