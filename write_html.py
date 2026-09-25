content = '''{% extends "layout_admin.html" %}

{% block content %}
<div class="panel-header" style="border:none; margin-bottom: 20px;">
    <div>
        <h1 style="margin:0; font-size: 1.8rem; font-weight: 700; color: #a855f7;">🧾 Carga y Previsualización - Jalisco</h1>
        <p style="margin:5px 0 0 0; color: var(--text-muted);">Sube el PDF del reporte semanal, revisa la extracción automática y confirma la inyección a la base de datos.</p>
    </div>
    <div>
        <button class="btn-action" onclick="window.location.href='/admin/jalisco'" style="background: var(--surface-hover); color: var(--text-primary);">
            Volver al Kardex
        </button>
    </div>
</div>

<div class="panel" style="max-width: 1200px; margin: 0 auto; text-align: center;" id="uploadPanel">
    <div id="dropzone" style="border: 2px dashed var(--border-color); border-radius: 12px; padding: 50px 20px; background: var(--bg-dark); cursor: pointer; transition: all 0.3s ease;" onclick="document.getElementById('fileInput').click()">
        <div style="font-size: 4rem; margin-bottom: 10px;">📥</div>
        <h3 style="margin:0; color: #fff;">Arrastra aquí tu PDF de Jalisco</h3>
        <p style="color: var(--text-muted); font-size: 0.9rem;">o haz clic para seleccionar (solo .pdf)</p>
        <input type="file" id="fileInput" accept=".pdf" style="display: none;" onchange="handleFileSelect(event)">
    </div>
</div>

<div id="previewArea" style="margin-top: 30px; display: none; grid-template-columns: 1fr 1fr; gap: 20px; max-width: 1400px; margin-left: auto; margin-right: auto;">
    <!-- Columna Izquierda: Datos Extraídos -->
    <div class="panel" style="display: flex; flex-direction: column;">
        <div class="panel-header" style="border-bottom: 1px solid var(--border-color);">
            <h3 style="margin:0; color: #10b981;">✅ Datos Extraídos (Semana <span id="lblSemana"></span>)</h3>
        </div>
        
        <div style="padding: 15px; flex: 1; overflow-y: auto; max-height: 600px;">
            <table class="admin-table">
                <thead>
                    <tr>
                        <th>Fecha</th>
                        <th>Equipo</th>
                        <th>Combustible</th>
                        <th style="text-align: right;">Litros</th>
                    </tr>
                </thead>
                <tbody id="tablaResultados">
                </tbody>
            </table>
        </div>
        
        <div style="padding: 20px; border-top: 1px solid var(--border-color); background: rgba(16, 185, 129, 0.1);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h4 style="margin: 0; color: #10b981;">Resumen de Inyección</h4>
                    <p style="margin: 5px 0; font-size: 0.9rem;">Total Diésel: <b id="totDiesel">0</b> L</p>
                    <p style="margin: 0; font-size: 0.9rem;">Total Gasolina: <b id="totGasolina">0</b> L</p>
                </div>
                <button class="btn btn-success" id="btnGuardar" onclick="confirmarUpload()" style="font-size: 1.1rem; padding: 12px 20px; background: #10b981; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: bold;">
                    🚀 Inyectar a Base de Datos
                </button>
            </div>
        </div>
    </div>
    
    <!-- Columna Derecha: Visor PDF -->
    <div class="panel" style="display: flex; flex-direction: column;">
        <div class="panel-header" style="border-bottom: 1px solid var(--border-color);">
            <h3 style="margin:0; color: #a855f7;">📄 Visor del Documento Original</h3>
        </div>
        <div style="flex: 1; min-height: 600px; padding: 10px;">
            <iframe id="pdfViewer" style="width: 100%; height: 100%; border: none; border-radius: 8px;"></iframe>
        </div>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
<script>
    let currentFile = null;

    // Drag and drop events
    const dropzone = document.getElementById('dropzone');
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, () => dropzone.style.borderColor = '#10b981', false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, () => dropzone.style.borderColor = 'var(--border-color)', false);
    });

    dropzone.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            processFile(files[0]);
        }
    }

    function handleFileSelect(e) {
        if (e.target.files.length > 0) {
            processFile(e.target.files[0]);
        }
    }

    function processFile(file) {
        if (file.type !== "application/pdf") {
            Swal.fire('Error', 'Por favor sube únicamente archivos PDF.', 'error');
            return;
        }
        
        currentFile = file;
        
        // Show PDF in viewer
        const fileURL = URL.createObjectURL(file);
        document.getElementById('pdfViewer').src = fileURL;
        
        // Send to backend for preview
        const formData = new FormData();
        formData.append('file', file);
        
        Swal.fire({
            title: 'Analizando PDF...',
            text: 'Extrayendo tablas de Diésel y Gasolina',
            allowOutsideClick: false,
            didOpen: () => Swal.showLoading()
        });
        
        fetch('/api/admin/jalisco/preview_pdf', {
            method: 'POST',
            body: formData
        })
        .then(r => r.json())
        .then(res => {
            if (res.error) {
                Swal.fire('Error de Extracción', res.error, 'error');
                return;
            }
            
            Swal.close();
            
            // Hide upload, show preview
            document.getElementById('uploadPanel').style.display = 'none';
            document.getElementById('previewArea').style.display = 'grid';
            
            renderPreview(res.data);
        })
        .catch(err => {
            Swal.fire('Error', 'Ocurrió un error de red al procesar el archivo.', 'error');
            console.error(err);
        });
    }

    function renderPreview(data) {
        document.getElementById('lblSemana').innerText = data.semana || '?';
        
        let totDiesel = 0;
        let totGas = 0;
        const tbody = document.getElementById('tablaResultados');
        tbody.innerHTML = '';
        
        if (!data.consumos || data.consumos.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;">No se detectaron consumos</td></tr>';
            return;
        }
        
        data.consumos.forEach(c => {
            if (c.tipo_combustible === 'DIESEL') totDiesel += c.litros;
            if (c.tipo_combustible === 'GASOLINA') totGas += c.litros;
            
            const tr = document.createElement('tr');
            tr.innerHTML = 
                <td>\</td>
                <td>\</td>
                <td>
                    <span style="padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; background: \; color: \;">
                        \
                    </span>
                </td>
                <td style="text-align: right; font-weight: bold;">\ L</td>
            ;
            tbody.appendChild(tr);
        });
        
        document.getElementById('totDiesel').innerText = totDiesel.toFixed(2);
        document.getElementById('totGasolina').innerText = totGas.toFixed(2);
    }
    
    function confirmarUpload() {
        if (!currentFile) return;
        
        Swal.fire({
            title: '¿Confirmar Inyección?',
            text: "Los saldos teóricos se actualizarán con estos movimientos.",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#10b981',
            cancelButtonColor: '#ef4444',
            confirmButtonText: 'Sí, Inyectar'
        }).then((result) => {
            if (result.isConfirmed) {
                const formData = new FormData();
                formData.append('file', currentFile);
                
                Swal.fire({
                    title: 'Guardando...',
                    allowOutsideClick: false,
                    didOpen: () => Swal.showLoading()
                });
                
                fetch('/api/admin/jalisco/confirm_upload', {
                    method: 'POST',
                    body: formData
                })
                .then(r => r.json())
                .then(res => {
                    if (res.error) {
                        Swal.fire('Error', res.error, 'error');
                    } else {
                        Swal.fire('¡Inyección Exitosa!', res.message, 'success').then(() => {
                            window.location.href = '/admin/jalisco';
                        });
                    }
                })
                .catch(err => {
                    Swal.fire('Error', 'No se pudo guardar la información.', 'error');
                });
            }
        });
    }
</script>
{% endblock %}'''

with open(r'c:\Users\JOSE\Desktop\Proyecto fenix\servidor\templates\admin\admin_jalisco_subir.html', 'w', encoding='utf-8') as f:
    f.write(content)
