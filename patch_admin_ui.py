import os
import re

files_to_patch = [
    r'c:\Users\JOSE\Desktop\Proyecto fenix\servidor\templates\admin\admin_diesel.html',
    r'c:\Users\JOSE\Desktop\Proyecto fenix\servidor\templates\admin\admin_gasolina.html'
]

js_functions = """
    // --- BATCH APPROVAL LOGIC ---
    function toggleAll(source) {
        const checkboxes = document.querySelectorAll('.chk-row');
        for(let i=0; i<checkboxes.length; i++) {
            checkboxes[i].checked = source.checked;
        }
        checkSelection();
    }

    function checkSelection() {
        const checkboxes = document.querySelectorAll('.chk-row:checked');
        const btn = document.getElementById('btn-aprobar-batch');
        if(btn) {
            btn.style.display = checkboxes.length > 0 ? 'inline-block' : 'none';
            btn.textContent = `✅ Aprobar Seleccionados (${checkboxes.length})`;
        }
    }

    async function aprobarBatch() {
        const checkboxes = document.querySelectorAll('.chk-row:checked');
        if(checkboxes.length === 0) return;
        
        let ids = [];
        checkboxes.forEach(cb => ids.push(parseInt(cb.value)));
        
        // Determinar tabla basado en currentTab y si es diesel o gasolina
        let prefix = window.location.pathname.includes('gasolina') ? 'gasolina' : 'diesel';
        let tabla = prefix + '.' + currentTab;
        
        try {
            const res = await fetch('/api/admin/aprobar_batch', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ tabla: tabla, ids: ids, estatus: 'APROBADO' })
            });
            const data = await res.json();
            
            if(data.success) {
                // Deseleccionar checkbox maestro
                const chkAll = document.querySelector('thead input[type="checkbox"]');
                if(chkAll) chkAll.checked = false;
                cargarDatos();
            } else if(data.duplicateWarning) {
                // Mostrar warning amigable en lugar de solo alert
                if(confirm('⚠️ PRECAUCIÓN: ' + data.error + '\\n\\n¿Deseas continuar y aprobar de todos modos? (Esto podría crear duplicados en tus registros)')) {
                    // Si el usuario acepta, podemos forzar (requeriria otro parametro en el backend) o simplemente rechazar por ahora
                    // Para simplificar, Fenix rechaza por seguridad. El usuario debe borrar el duplicado.
                    alert('Acción cancelada por seguridad. Por favor, revisa la tabla y borra el registro duplicado antes de aprobar.');
                }
            } else {
                alert('Error al aprobar: ' + data.error);
            }
        } catch(e) {
            alert('Error de conexión al aprobar masivamente');
        }
    }
"""

button_html = """
                    <button id="btn-aprobar-batch" style="display:none; margin-left:10px; background: rgba(16,185,129,0.2); color: #10b981; border: 1px solid rgba(16,185,129,0.4); border-radius: 6px; padding: 6px 12px; cursor: pointer; font-weight: bold;" onclick="aprobarBatch()">✅ Aprobar Seleccionados</button>
"""

for filepath in files_to_patch:
    if not os.path.exists(filepath): continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if 'aprobarBatch()' in content:
        print(f"Ya parchado: {filepath}")
        continue
        
    # Inject check columns in tables
    # Consumos
    content = content.replace('<th>Folio</th>', '<th style="width: 40px;"><input type="checkbox" onchange="toggleAll(this)"></th>\n                          <th>Folio</th>')
    # Facturas
    content = content.replace('<th>Folio Factura</th>', '<th style="width: 40px;"><input type="checkbox" onchange="toggleAll(this)"></th>\n                          <th>Folio Factura</th>')
    # Solicitudes (if exists) - usually starts with Folio too. But let's check exact match.
    # We already replaced '<th>Folio</th>', which might have caught Solicitudes too.
    
    # Inject button after filtro-estatus
    content = content.replace('</select>\n                    </div>', f'</select>{button_html}                    </div>')
    # Or near it.
    idx = content.find('id="filtro-estatus"')
    if idx != -1:
        end_select = content.find('</select>', idx) + 9
        content = content[:end_select] + button_html + content[end_select:]
    
    # Inject JS rendering td
    # 1. Consumos: `<td style="color: #3b82f6; font-family: monospace;">${r.folio_conciliacion}</td>`
    content = content.replace(
        '<td style="color: #3b82f6; font-family: monospace;">${r.folio_conciliacion}</td>', 
        '<td><input type="checkbox" class="chk-row" value="${r.id}" onchange="checkSelection()"></td>\n                              <td style="color: #3b82f6; font-family: monospace;">${r.folio_conciliacion}</td>'
    )
    # 2. Facturas: `<td style="color: #3b82f6; font-family: monospace;">${r.folio_factura}</td>`
    content = content.replace(
        '<td style="color: #3b82f6; font-family: monospace;">${r.folio_factura}</td>', 
        '<td><input type="checkbox" class="chk-row" value="${r.id}" onchange="checkSelection()"></td>\n                              <td style="color: #3b82f6; font-family: monospace;">${r.folio_factura}</td>'
    )
    # 3. Solicitudes: `<td style="color: #3b82f6; font-family: monospace;">${r.folio_solicitud}</td>`
    content = content.replace(
        '<td style="color: #3b82f6; font-family: monospace;">${r.folio_solicitud}</td>', 
        '<td><input type="checkbox" class="chk-row" value="${r.id}" onchange="checkSelection()"></td>\n                          <td style="color: #3b82f6; font-family: monospace;">${r.folio_solicitud}</td>'
    )
    
    # Inject JS functions
    content = content.replace('</script>\n{% endblock %}', f'{js_functions}\n</script>\n{{% endblock %}}')
    
    # Also reset selection when switching tabs
    content = content.replace('cargarDatos();', 'checkSelection();\n        cargarDatos();')
    
    # Reset master checkbox
    content = content.replace('tbody.innerHTML = \'\';', 'const master = document.querySelector(\'#tabla-\' + currentTab + \' thead input[type="checkbox"]\');\n              if(master) master.checked = false;\n              tbody.innerHTML = \'\';')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Parchado: {filepath}")

