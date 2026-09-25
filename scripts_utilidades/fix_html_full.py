import re

with open(r'c:\Users\JOSE\Desktop\Proyecto fenix\servidor\templates\admin\admin_diesel.html', 'r', encoding='utf-8') as f:
    content = f.read()

# We want to replace everything from `{% block scripts %}` to `{% endblock %}`
# So we locate the block scripts section and completely rewrite it.

start_marker = "{% block scripts %}"
end_marker = "{% endblock %}"

# But wait, looking at the previous diff, I might have deleted `{% endblock %}` or `{% block scripts %}`. Let's just find `<!-- TomSelect CSS/JS para Admin -->` and replace everything after it with a fresh script block.
start_marker = "<!-- TomSelect CSS/JS para Admin -->"

idx_start = content.find(start_marker)

if idx_start == -1:
    print("Marker not found!")
    exit(1)

new_js = """<!-- TomSelect CSS/JS para Admin -->
<link href="https://cdn.jsdelivr.net/npm/tom-select@2.2.2/dist/css/tom-select.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/tom-select@2.2.2/dist/js/tom-select.complete.min.js"></script>

{% endblock %}

{% block scripts %}
<script>
    let currentRowId = null;
    let datosTabla = {};
    let currentTab = 'consumos';

    function switchTab(tab) {
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
            document.getElementById('visor-evidencia').innerHTML = '<div class="visor-empty">👈 Selecciona un consumo para ver su foto.</div>';
        } else if (tab === 'facturas') {
            document.getElementById('btnTabFacturas').classList.add('active');
            document.getElementById('tabla-facturas').style.display = 'table';
            document.getElementById('tabla-titulo').textContent = '🧾 Facturas de Diesel';
            document.getElementById('visor-evidencia').innerHTML = '<div class="visor-empty">👈 Selecciona una factura para ver su PDF.</div>';
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

    // Editar Lógica
    let tomSelectObra = null;
    let tomSelectEquipo = null;
    
    function abrirModalEditar() {
        if(!currentRowId || !datosTabla[currentRowId]) return;
        const data = datosTabla[currentRowId];
        
        document.getElementById('editFecha').value = data.fecha || '';
        document.getElementById('editSemana').value = data.semana || '';
        document.getElementById('editLitros').value = data.litros || '';
        document.getElementById('editImporte').value = data.importe_total || '';
        
        // Initialize TomSelect if not initialized
        if(!tomSelectObra) {
            tomSelectObra = new TomSelect("#editObra", { create: false, selectOnTab: true });
        }
        if(!tomSelectEquipo) {
            tomSelectEquipo = new TomSelect("#editEquipo", { create: false, selectOnTab: true });
        }
        
        tomSelectObra.setValue(data.obra_destino);
        tomSelectEquipo.setValue(data.equipo);
        
        document.getElementById('modalEditar').style.display = 'flex';
    }

    async function guardarEdicion() {
        const payload = {
            tabla: 'diesel.consumos',
            id: currentRowId,
            campos: {
                fecha: document.getElementById('editFecha').value,
                semana: document.getElementById('editSemana').value,
                obra_destino: tomSelectObra.getValue(),
                equipo: tomSelectEquipo.getValue(),
                litros: document.getElementById('editLitros').value,
                importe_total: document.getElementById('editImporte').value
            }
        };

        const res = await fetch('/api/admin/editar_registro', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        const respData = await res.json();
        
        if(respData.success) {
            document.getElementById('modalEditar').style.display = 'none';
            cargarDatos(); // Refrescar la tabla
        } else {
            alert('Error al actualizar: ' + respData.error);
        }
    }

    // Calculate Week logic for admin editing
    document.getElementById("editFecha").addEventListener("change", function(e) {
        if(!this.value) return;
        const parts = this.value.split('-');
        const d = new Date(parts[0], parts[1]-1, parts[2]);
        const dayNum = d.getDay() || 7;
        d.setDate(d.getDate() + 4 - dayNum);
        const yearStart = new Date(d.getFullYear(),0,1);
        const week = Math.ceil((((d - yearStart) / 86400000) + 1)/7);
        document.getElementById("editSemana").value = week;
    });

    async function init() {
        // Cargar semanas disponibles
        const semRes = await fetch('/api/admin/semanas');
        const semanas = await semRes.json();
        const selSem = document.getElementById('filtro-semana');
        semanas.forEach(s => {
            const opt = document.createElement('option');
            opt.value = s;
            opt.textContent = s;
            selSem.appendChild(opt);
        });
        // Seleccionar semana más reciente por defecto
        if (semanas.length > 0) selSem.value = semanas[0];
        cargarDatos();
    }

    document.addEventListener('DOMContentLoaded', init);

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
            if(res.ok) {
                document.getElementById('modalAuth').style.display = 'none';
                cargarDatos();
            } else {
                alert('Error al guardar: ' + data.error);
            }
        } catch (error) {
            alert('Error de conexión');
        }
    }

    function abrirModalAjusteJalisco(semana, ajusteActual) {
        document.getElementById('editJaliscoSemana').value = semana;
        document.getElementById('editJaliscoRef').textContent = 'Semana ' + semana;
        document.getElementById('editJaliscoAjuste').value = ajusteActual;
        document.getElementById('modalAjusteJalisco').style.display = 'flex';
    }

    async function guardarAjusteJalisco() {
        const semana = document.getElementById('editJaliscoSemana').value;
        const ajuste = document.getElementById('editJaliscoAjuste').value;
        
        try {
            const res = await fetch('/api/admin/jalisco/ajuste', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ semana: semana, ajuste: parseFloat(ajuste) })
            });
            const data = await res.json();
            
            if(res.ok && data.success) {
                document.getElementById('modalAjusteJalisco').style.display = 'none';
                cargarDatos();
            } else {
                alert('Error al guardar: ' + (data.error || 'Desconocido'));
            }
        } catch (error) {
            alert('Error de conexión');
        }
    }
</script>
{% endblock %}
"""

new_content = content[:idx_start] + new_js

with open(r'c:\Users\JOSE\Desktop\Proyecto fenix\servidor\templates\admin\admin_diesel.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("HTML restored completely.")
