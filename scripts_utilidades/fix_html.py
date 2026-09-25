import re

with open(r'c:\Users\JOSE\Desktop\Proyecto fenix\servidor\templates\admin\admin_diesel.html', 'r', encoding='utf-8') as f:
    content = f.read()

# We need to find `function switchTab(tab) {` and replace everything down to `// Editar Lógica`
start_marker = "function switchTab(tab) {"
end_marker = "// Editar Lógica"

idx_start = content.find(start_marker)
idx_end = content.find(end_marker)

if idx_start == -1 or idx_end == -1:
    print("Markers not found!")
    exit(1)

new_js = """function switchTab(tab) {
        currentTab = tab;
        
        document.getElementById('btnTabConsumos').classList.remove('active');
        document.getElementById('btnTabFacturas').classList.remove('active');
        document.getElementById('btnTabAutorizaciones').classList.remove('active');
        document.getElementById('btnTabSolicitudes').classList.remove('active');
        
        document.getElementById('tabla-consumos').style.display = 'none';
        document.getElementById('tabla-facturas').style.display = 'none';
        document.getElementById('tabla-autorizaciones').style.display = 'none';
        document.getElementById('tabla-solicitudes').style.display = 'none';
        
        if (tab === 'consumos') {
            document.getElementById('btnTabConsumos').classList.add('active');
            document.getElementById('tabla-consumos').style.display = 'table';
            document.getElementById('tabla-titulo').textContent = '📝 Consumos de Diesel';
            document.getElementById('visor-evidencia').innerHTML = '<div class="visor-empty">👈 Modo Consumos. Selecciona un registro.</div>';
        } else if (tab === 'facturas') {
            document.getElementById('btnTabFacturas').classList.add('active');
            document.getElementById('tabla-facturas').style.display = 'table';
            document.getElementById('tabla-titulo').textContent = '🧾 Facturas de Diesel';
            document.getElementById('visor-evidencia').innerHTML = '<div class="visor-empty">👈 Modo Facturas. Visualiza PDFs y XML.</div>';
        } else if (tab === 'autorizaciones') {
            document.getElementById('btnTabAutorizaciones').classList.add('active');
            document.getElementById('tabla-autorizaciones').style.display = 'table';
            document.getElementById('tabla-titulo').textContent = '✅ Autorizaciones de Diesel';
            document.getElementById('visor-evidencia').innerHTML = '<div class="visor-empty">👈 Modo Autorizaciones. Usa el botón editar para cambiar el tope semanal.</div>';
        } else if (tab === 'solicitudes') {
            document.getElementById('btnTabSolicitudes').classList.add('active');
            document.getElementById('tabla-solicitudes').style.display = 'table';
            document.getElementById('tabla-titulo').textContent = '📥 Solicitudes a Gasolinera (Diesel)';
            document.getElementById('visor-evidencia').innerHTML = '<div class="visor-empty">👈 Selecciona una solicitud para ver detalles o comprobar evidencia.</div>';
        }
        document.getElementById('visor-acciones').style.display = 'none';
        document.getElementById('visor-folio').textContent = 'Ningún registro seleccionado';
        cargarDatos();
    }

    async function cargarDatos() {
        const estatus = document.getElementById('filtro-estatus').value;
        const semana  = document.getElementById('filtro-semana').value;
        const semanaParam = semana ? `&semana=${encodeURIComponent(semana)}` : '';
        const semanaNumParam = semana ? `&semana=${encodeURIComponent(semana.replace('Semana ','').trim())}` : '';
        let url = '';
        if (currentTab === 'consumos') url = `/api/admin/pendientes/diesel_consumos?estatus=${estatus}${semanaParam}`;
        else if (currentTab === 'facturas') url = `/api/admin/pendientes/diesel_facturas?estatus=${estatus}${semanaParam}`;
        else if (currentTab === 'autorizaciones') url = `/api/admin/autorizaciones?tipo=DIESEL${semanaNumParam}`;
        else if (currentTab === 'solicitudes') url = `/api/admin/pendientes/diesel_solicitudes?estatus=${estatus}${semanaParam}`;
        
        const tbodyId = `tbody-${currentTab}`;
        const tbody = document.getElementById(tbodyId);
        tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;">Cargando...</td></tr>';
        
        try {
            const res = await fetch(url);
            const data = await res.json();
            
            if(!data || data.length === 0) {
                tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color: #10b981;">No hay registros encontrados.</td></tr>`;
                return;
            }
            
            tbody.innerHTML = '';
            data.forEach(r => {
                datosTabla[r.id] = r; 
                const tr = document.createElement('tr');
                
                if (currentTab === 'consumos' || currentTab === 'facturas') {
                    tr.style.cursor = 'pointer';
                    const mainFolio = currentTab === 'consumos' ? r.folio_conciliacion : r.folio_factura;
                    tr.onclick = () => verEvidencia(r.id, mainFolio, tr, r.estatus_revision);
                    
                    let btnHtml = '';
                    if(r.estatus_revision === 'PENDIENTE') {
                        btnHtml = `<button class="btn-aprobar" onclick="event.stopPropagation(); aprobarFila(${r.id})">✅</button>`;
                    } else if(r.estatus_revision === 'APROBADO') {
                        btnHtml = `<span style="color:#10b981; font-size:0.8rem;">Aprobado</span>`;
                    } else {
                        btnHtml = `<span style="color:#ef4444; font-size:0.8rem;">Rechazado</span>`;
                    }
                    
                    if (currentTab === 'consumos') {
                        tr.innerHTML = `
                            <td style="color: #3b82f6; font-family: monospace;">${r.folio_conciliacion}</td>
                            <td>${r.fecha}</td>
                            <td>${r.obra_destino}</td>
                            <td><strong>${r.equipo || 'N/A'}</strong></td>
                            <td>${r.litros} L</td>
                            <td>$${r.importe_total}</td>
                            <td>${btnHtml}</td>
                        `;
                    } else {
                        tr.innerHTML = `
                            <td style="color: #3b82f6; font-family: monospace;">${r.folio_factura}</td>
                            <td>${r.fecha_factura}</td>
                            <td>${r.proveedor}</td>
                            <td>${r.litros_facturados} L</td>
                            <td>$${r.importe_total}</td>
                            <td style="font-size: 0.8rem; font-family: monospace; max-width: 150px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${r.uuid_cfdi}">${r.uuid_cfdi}</td>
                            <td>${btnHtml}</td>
                        `;
                    }
                    tbody.appendChild(tr);
                } else if (currentTab === 'autorizaciones') {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td style="color: #3b82f6; font-family: monospace;">${r.referencia}</td>
                        <td><strong>${r.litros_autorizados} L</strong></td>
                        <td><button style="background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); color: #fff; border-radius: 6px; padding: 4px 10px; cursor: pointer;" onclick="abrirModalAuth(${r.id}, '${r.referencia}', ${r.litros_autorizados})">✏️ Editar Tope</button></td>
                    `;
                    tbody.appendChild(tr);
                } else if (currentTab === 'solicitudes') {
                    const tr = document.createElement('tr');
                    tr.style.cursor = 'pointer';
                    tr.onclick = () => verEvidencia(r.id, r.folio_solicitud, tr, r.estatus_conciliacion);
                    
                    let btnHtml = '';
                    if(r.estatus_conciliacion === 'PENDIENTE' || !r.estatus_conciliacion) {
                        btnHtml = `<button class="btn-aprobar" onclick="event.stopPropagation(); aprobarFila(${r.id})">✅</button>`;
                    } else if(r.estatus_conciliacion === 'APROBADO') {
                        btnHtml = `<span style="color:#10b981; font-size:0.8rem;">Aprobado</span>`;
                    } else {
                        btnHtml = `<span style="color:#ef4444; font-size:0.8rem;">Rechazado</span>`;
                    }
                    
                    tr.innerHTML = `
                        <td style="color: #3b82f6; font-family: monospace;">${r.folio_solicitud}</td>
                        <td>${r.fecha}</td>
                        <td>${r.obra_destino}</td>
                        <td>${r.solicitante}</td>
                        <td>${r.litros} L</td>
                        <td>$${parseFloat(r.importe_total || 0).toLocaleString('es-MX', {minimumFractionDigits: 2})}</td>
                        <td>${btnHtml}</td>
                    `;
                    tbody.appendChild(tr);
                }
            });
        } catch(e) {
            tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:#ef4444;">Error al cargar datos.</td></tr>`;
        }
    }

    function verEvidencia(id, folio, trElement, estatus = 'PENDIENTE') {
        currentRowId = id;
        
        document.querySelectorAll('.admin-table tr').forEach(tr => tr.classList.remove('selected'));
        if(trElement) trElement.classList.add('selected');
        
        document.getElementById('visor-folio').textContent = folio;
        
        const visor = document.getElementById('visor-evidencia');
        if (currentTab === 'consumos') {
            visor.innerHTML = `<img src="/api/evidencia/diesel/consumos/${id}?t=${Date.now()}" onerror="this.onerror=null; this.parentElement.innerHTML='<div class=\\'visor-empty\\'>⚠️ Foto no disponible o archivo corrupto.</div>'" />`;
        } else if (currentTab === 'solicitudes') {
            visor.innerHTML = `<div class="visor-empty">📝 Solicitud ${folio}<br><br>Evidencia de solicitud adjunta o notas adicionales irían aquí.</div>`;
        } else {
            visor.innerHTML = `<iframe src="/api/evidencia/diesel/facturas/${id}?t=${Date.now()}" width="100%" height="500px" style="border:none;"></iframe>`;
        }
        
        if (estatus === 'PENDIENTE' || !estatus) {
            document.getElementById('visor-acciones').style.display = 'flex';
        } else {
            document.getElementById('visor-acciones').style.display = 'none';
        }
    }
    
    async function aprobarFila(id) {
        let tablaDB = 'diesel.consumos';
        if (currentTab === 'facturas') tablaDB = 'diesel.facturas';
        if (currentTab === 'solicitudes') tablaDB = 'diesel.solicitudes';
        await cambiarEstatus(tablaDB, id, 'APROBADO');
        if(currentRowId === id) {
            document.getElementById('visor-evidencia').innerHTML = '<div class="visor-empty">Registro aprobado. Selecciona otro.</div>';
            document.getElementById('visor-acciones').style.display = 'none';
        }
        cargarDatos();
    }
    
    async function accionAprobar() {
        if(!currentRowId) return;
        await aprobarFila(currentRowId);
    }
    
    async function accionRechazar() {
        if(!currentRowId) return;
        if(confirm("¿Estás seguro de rechazar este registro?")) {
            let tablaDB = 'diesel.consumos';
            if (currentTab === 'facturas') tablaDB = 'diesel.facturas';
            if (currentTab === 'solicitudes') tablaDB = 'diesel.solicitudes';
            await cambiarEstatus(tablaDB, currentRowId, 'RECHAZADO');
            document.getElementById('visor-evidencia').innerHTML = '<div class="visor-empty">Registro rechazado. Selecciona otro.</div>';
            document.getElementById('visor-acciones').style.display = 'none';
            cargarDatos();
        }
    }

    // Editar Lógica"""

new_content = content[:idx_start] + new_js + content[idx_end:]

with open(r'c:\Users\JOSE\Desktop\Proyecto fenix\servidor\templates\admin\admin_diesel.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("HTML fixed.")
