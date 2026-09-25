import re

file = r"c:\Users\JOSE\Desktop\Proyecto fenix\servidor\templates\admin\admin_diesel.html"
with open(file, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add Edit button to solicitudes rows
# Find the line: <td style="white-space:nowrap;"></td>
# Change it to add the button
old_row = r"<td style=\"white-space:nowrap;\">\$\{estatusBadge\}</td>"
new_row = """<td style="white-space:nowrap;">
                                
                                <button style="margin-left:4px; background:rgba(99,102,241,0.2); border:1px solid rgba(99,102,241,0.4); color:#a5b4fc; border-radius:5px; padding:3px 8px; cursor:pointer; font-size:0.8rem;" onclick="event.stopPropagation(); abrirModalEditarSolicitud()">??</button>
                            </td>"""
content = content.replace(old_row, new_row)

# 2. Add Modal HTML right after modalEditarFactura ends
# Find the end of modalEditarFactura (it ends with </div> \n </div>)
# We can just append it before </main> or just right before <script>
modal_html = """
<!-- MODAL EDITAR SOLICITUD -->
<div id="modalEditarSolicitud" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.6); backdrop-filter:blur(4px); align-items:center; justify-content:center; z-index:1000;">
    <div style="background:var(--admin-panel); border:1px solid var(--admin-border); border-radius:12px; padding:24px; width:560px; max-width:92%; box-shadow:0 10px 40px rgba(0,0,0,0.5);">
        <h3 style="margin-top:0; margin-bottom:20px; color:white;">?? Editar Solicitud Diésel</h3>
        
        <div style="display:flex; gap:15px; margin-bottom:15px;">
            <div style="flex:1;">
                <label style="display:block; margin-bottom:5px; font-size:0.9rem; color:#94a3b8;">Litros Solicitados</label>
                <input type="number" step="0.01" id="edit-sol-litros" oninput="calcImporteSol()" style="width:100%; padding:10px; border-radius:6px; border:1px solid #334155; background:#0f172a; color:white; font-family:monospace;">
            </div>
            <div style="flex:1;">
                <label style="display:block; margin-bottom:5px; font-size:0.9rem; color:#94a3b8;">Precio Unitario</label>
                <input type="number" step="0.01" id="edit-sol-precio" oninput="calcImporteSol()" style="width:100%; padding:10px; border-radius:6px; border:1px solid #334155; background:#0f172a; color:white; font-family:monospace;">
            </div>
        </div>
        
        <div style="display:flex; gap:15px; margin-bottom:20px;">
            <div style="flex:1;">
                <label style="display:block; margin-bottom:5px; font-size:0.9rem; color:#94a3b8;">Importe Total</label>
                <input type="number" step="0.01" id="edit-sol-importe" style="width:100%; padding:10px; border-radius:6px; border:1px solid #334155; background:#1e293b; color:#10b981; font-weight:bold; font-family:monospace;" readonly>
            </div>
            <div style="flex:1;">
                <label style="display:block; margin-bottom:5px; font-size:0.9rem; color:#94a3b8;">Obra Destino</label>
                <input type="text" id="edit-sol-obra" style="width:100%; padding:10px; border-radius:6px; border:1px solid #334155; background:#0f172a; color:white;">
            </div>
        </div>
        
        <div style="display:flex; gap:15px; margin-bottom:20px;">
            <div style="flex:1;">
                <label style="display:block; margin-bottom:5px; font-size:0.9rem; color:#94a3b8;">Semana</label>
                <input type="number" id="edit-sol-semana" style="width:100%; padding:10px; border-radius:6px; border:1px solid #334155; background:#0f172a; color:white;">
            </div>
        </div>

        <div style="display:flex; gap:10px; justify-content:flex-end;">
            <button class="btn-rechazar" onclick="borrarRegistro('diesel_solicitudes')" style="margin-right:auto; background:rgba(239,68,68,0.1); color:#ef4444; border:1px solid rgba(239,68,68,0.3);">??? Borrar</button>
            <button class="btn-rechazar" onclick="document.getElementById('modalEditarSolicitud').style.display='none'">Cancelar</button>
            <button class="btn-aprobar" onclick="guardarEdicionSolicitud()">?? Guardar Cambios</button>
        </div>
    </div>
</div>
"""
content = content.replace('<script>', modal_html + '\n<script>')

# 3. Add JS functions
js_code = """
    function calcImporteSol() {
        const lts = parseFloat(document.getElementById('edit-sol-litros').value) || 0;
        const precio = parseFloat(document.getElementById('edit-sol-precio').value) || 0;
        document.getElementById('edit-sol-importe').value = (lts * precio).toFixed(2);
    }

    function abrirModalEditarSolicitud(id) {
        if(!datosTabla[id]) return;
        currentRowId = id;
        const data = datosTabla[id];
        
        document.getElementById('edit-sol-litros').value = data.litros || '';
        document.getElementById('edit-sol-precio').value = data.costo_por_litro || '';
        document.getElementById('edit-sol-importe').value = data.importe_total || '';
        document.getElementById('edit-sol-obra').value = data.obra_destino || '';
        document.getElementById('edit-sol-semana').value = (data.semana||'').toString().replace('Semana','').trim();
        
        document.getElementById('modalEditarSolicitud').style.display = 'flex';
    }

    async function guardarEdicionSolicitud() {
        const payload = {
            tabla: 'diesel.solicitudes',
            id: currentRowId,
            campos: {
                litros: parseFloat(document.getElementById('edit-sol-litros').value) || 0,
                costo_por_litro: parseFloat(document.getElementById('edit-sol-precio').value) || 0,
                importe_total: parseFloat(document.getElementById('edit-sol-importe').value) || 0,
                obra_destino: document.getElementById('edit-sol-obra').value.trim(),
                semana: document.getElementById('edit-sol-semana').value.trim()
            }
        };
        
        try {
            const res = await fetch('/api/admin/editar_registro', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (data.success) {
                document.getElementById('modalEditarSolicitud').style.display = 'none';
                checkSelection();
                cargarDatos();
            } else {
                alert('Error al guardar: ' + data.error);
            }
        } catch(e) {
            alert('Error de conexión');
        }
    }
"""
content = content.replace('function abrirModalEditar(id) {', js_code + '\n    function abrirModalEditar(id) {')

with open(file, 'w', encoding='utf-8') as f:
    f.write(content)

print("Solicitudes edit logic injected.")
