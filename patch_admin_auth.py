import os

def patch_file(filepath, es_diesel):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Add tab button
    btn_consumos_idx = content.find('<button id="btnTabConsumos"')
    if '<button id="btnTabAutorizaciones"' not in content:
        btn_facturas_end = content.find('</button>', content.find('<button id="btnTabFacturas"')) + 9
        content = content[:btn_facturas_end] + '\n                <button id="btnTabAutorizaciones" class="tab-btn" onclick="switchTab(\'autorizaciones\')">✅ Autorizaciones</button>' + content[btn_facturas_end:]

    # 2. Add table
    if '<table class="admin-table" id="tabla-autorizaciones"' not in content:
        table_facturas_end = content.find('</table>', content.find('<table class="admin-table" id="tabla-facturas"')) + 8
        
        ref_header = "Obra Destino" if es_diesel else "Unidad / Vehículo"
        
        auth_table = f'''
            <table class="admin-table" id="tabla-autorizaciones" style="display:none;">
                <thead>
                    <tr>
                        <th>{ref_header}</th>
                        <th>Litros Autorizados</th>
                        <th>Consumo Actual (L)</th>
                        <th>Estatus</th>
                        <th>Acción</th>
                    </tr>
                </thead>
                <tbody id="tbody-autorizaciones">
                    <tr><td colspan="5" style="text-align:center;">Cargando...</td></tr>
                </tbody>
            </table>'''
        content = content[:table_facturas_end] + auth_table + content[table_facturas_end:]

    # 3. Add modal
    if '<div class="modal-overlay" id="modalAuth"' not in content:
        modals_end = content.find('<!-- TomSelect CSS/JS')
        modal_html = '''
<!-- MODAL EDITAR AUTORIZACION -->
<div class="modal-overlay" id="modalAuth" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); backdrop-filter: blur(4px); align-items: center; justify-content: center; z-index: 1000;">
    <div class="modal-box" style="background: var(--admin-panel); border: 1px solid var(--admin-border); border-radius: 12px; padding: 24px; width: 400px; max-width: 90%; box-shadow: 0 10px 40px rgba(0,0,0,0.5);">
        <h3 style="margin-top: 0; margin-bottom: 20px; color: white;">✏️ Editar Tope Semanal</h3>
        <input type="hidden" id="editAuthId">
        <p id="editAuthRef" style="color:var(--admin-primary); margin-bottom: 15px; font-weight:bold;"></p>
        
        <div style="margin-bottom: 15px;">
            <label style="display: block; margin-bottom: 6px; color: var(--text-muted); font-size: 0.85rem;">Litros Autorizados</label>
            <input type="number" step="0.1" id="editAuthLitros" style="width: 100%; padding: 10px; border-radius: 6px; border: 1px solid var(--admin-border); background: rgba(0,0,0,0.3); color: white;">
        </div>
        
        <div style="display: flex; justify-content: flex-end; gap: 10px; margin-top: 24px;">
            <button class="btn-rechazar" onclick="document.getElementById('modalAuth').style.display='none'">Cancelar</button>
            <button class="btn-aprobar" onclick="guardarAuth()">Guardar Cambios</button>
        </div>
    </div>
</div>
'''
        content = content[:modals_end] + modal_html + content[modals_end:]

    # 4. JS: switchTab
    content = content.replace("document.getElementById('btnTabFacturas').classList.remove('active');",
                              "document.getElementById('btnTabFacturas').classList.remove('active');\n        document.getElementById('btnTabAutorizaciones').classList.remove('active');")
    content = content.replace("document.getElementById('tabla-facturas').style.display = 'none';",
                              "document.getElementById('tabla-facturas').style.display = 'none';\n        document.getElementById('tabla-autorizaciones').style.display = 'none';")

    switch_else = content.find('} else {', content.find("if (tab === 'consumos')"))
    if switch_else != -1 and 'tab === \'facturas\'' not in content[switch_else-20:switch_else+20]:
        title = "Diesel" if es_diesel else "Gasolina"
        new_switch_else = f'''}} else if (tab === 'facturas') {{
            document.getElementById('btnTabFacturas').classList.add('active');
            document.getElementById('tabla-facturas').style.display = 'table';
            document.getElementById('tabla-titulo').textContent = '🧾 Facturas de {title}';
            document.getElementById('visor-evidencia').innerHTML = '<div class="visor-empty">👈 Selecciona una factura para ver su PDF.</div>';
        }} else {{
            document.getElementById('btnTabAutorizaciones').classList.add('active');
            document.getElementById('tabla-autorizaciones').style.display = 'table';
            document.getElementById('tabla-titulo').textContent = '✅ Autorizaciones de {title} (Semana Actual)';
            document.getElementById('visor-evidencia').innerHTML = '<div class="visor-empty">👈 Modo Autorizaciones. Usa el botón editar para cambiar el tope semanal.</div>';
        '''
        
        # Replace the `} else {` with `} else if (tab === 'facturas') { ... } else { ... `
        # Actually it's easier to regex or manually find it.
        # Let's find the exact block:
        old_block = f'''}} else {{
            document.getElementById('btnTabFacturas').classList.add('active');
            document.getElementById('tabla-facturas').style.display = 'table';
            document.getElementById('tabla-titulo').textContent = '🧾 Facturas de {title}';
            document.getElementById('visor-evidencia').innerHTML = '<div class="visor-empty">👈 Selecciona una factura para ver su PDF.</div>';
        }}'''
        
        if old_block in content:
            content = content.replace(old_block, new_switch_else + '}')

    # 5. JS: cargarDatos URL
    url_block_old = '''const url = currentTab === 'consumos' 
            ? `/api/admin/pendientes/diesel_consumos?estatus=${estatus}`
            : `/api/admin/pendientes/diesel_facturas?estatus=${estatus}`;'''
    url_block_old_gas = '''const url = currentTab === 'consumos' 
            ? `/api/admin/pendientes/gasolina_consumos?estatus=${estatus}`
            : `/api/admin/pendientes/gasolina_facturas?estatus=${estatus}`;'''
            
    api_tipo = "DIESEL" if es_diesel else "GASOLINA"
    api_prefix = "diesel" if es_diesel else "gasolina"
    
    url_block_new = f'''let url = '';
        if (currentTab === 'consumos') url = `/api/admin/pendientes/{api_prefix}_consumos?estatus=${{estatus}}`;
        else if (currentTab === 'facturas') url = `/api/admin/pendientes/{api_prefix}_facturas?estatus=${{estatus}}`;
        else url = `/api/admin/autorizaciones?tipo={api_tipo}`;'''
        
    content = content.replace(url_block_old, url_block_new).replace(url_block_old_gas, url_block_new)

    tbody_block_old = "const tbodyId = currentTab === 'consumos' ? 'tbody-consumos' : 'tbody-facturas';"
    tbody_block_new = "const tbodyId = currentTab === 'consumos' ? 'tbody-consumos' : (currentTab === 'facturas' ? 'tbody-facturas' : 'tbody-autorizaciones');"
    content = content.replace(tbody_block_old, tbody_block_new)

    # 6. JS: render loop
    if 'currentTab === \'facturas\'' not in content.split('if (currentTab === \'consumos\') {')[1]:
        # replace `} else {` for rendering with `} else if (currentTab === 'facturas') {`
        render_if = content.find("if (currentTab === 'consumos') {")
        render_else = content.find("} else {", render_if)
        render_end = content.find("tbody.appendChild(tr);", render_else)
        
        old_render_block = content[render_else:render_end]
        
        new_auth_render = f'''}} else if (currentTab === 'facturas') {{
{old_render_block[8:]}
                }} else {{
                    tr.onclick = null; // No viewer
                    let stHtml = r.excedido ? `<span style="color:#ef4444; font-weight:bold;">⚠️ Excedido</span>` : `<span style="color:#10b981;">✅ En regla</span>`;
                    tr.style.backgroundColor = r.excedido ? 'rgba(239, 68, 68, 0.1)' : '';
                    tr.innerHTML = `
                        <td style="color: #3b82f6; font-family: monospace;">${{r.referencia}}</td>
                        <td><strong>${{r.litros_autorizados}} L</strong></td>
                        <td style="${{r.excedido ? 'color:#ef4444; font-weight:bold;' : ''}}">${{r.consumo_actual}} L</td>
                        <td>${{stHtml}}</td>
                        <td><button style="background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); color: #fff; border-radius: 6px; padding: 4px 10px; cursor: pointer;" onclick="abrirModalAuth(${{r.id}}, '${{r.referencia}}', ${{r.litros_autorizados}})">✏️ Editar Tope</button></td>
                    `;
                '''
        content = content.replace(old_render_block, new_auth_render)

    # 7. Add auth JS functions
    if 'function abrirModalAuth' not in content:
        js_end = content.rfind('</script>')
        auth_js = '''
    function abrirModalAuth(id, ref, litros) {
        document.getElementById('editAuthId').value = id;
        document.getElementById('editAuthRef').textContent = ref;
        document.getElementById('editAuthLitros').value = litros;
        document.getElementById('modalAuth').style.display = 'flex';
    }

    async function guardarAuth() {
        const id = document.getElementById('editAuthId').value;
        const litros = document.getElementById('editAuthLitros').value;
        try {
            const res = await fetch('/api/admin/autorizaciones/guardar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ id: id, litros: litros })
            });
            const data = await res.json();
            if(data.success) {
                document.getElementById('modalAuth').style.display = 'none';
                cargarDatos();
            } else {
                alert('Error al guardar: ' + data.error);
            }
        } catch(e) {
            alert('Error de conexión');
        }
    }
'''
        content = content[:js_end] + auth_js + content[js_end:]

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


import sys
diesel_path = r"c:\Users\JOSE\Desktop\Proyecto fenix\servidor\templates\admin\admin_diesel.html"
gasolina_path = r"c:\Users\JOSE\Desktop\Proyecto fenix\servidor\templates\admin\admin_gasolina.html"

patch_file(diesel_path, True)
patch_file(gasolina_path, False)
print("Archivos HTML actualizados exitosamente.")
