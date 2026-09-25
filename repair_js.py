import re

html_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\servidor\templates\captura_v2\captura_diesel.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

clean_js = '''<script>
    // Initialize Searchable Dropdowns
    new TomSelect("#obraSelect",{ create: false, sortField: {field: "text", direction: "asc"} });
    new TomSelect("#equipoSelect",{ create: false, sortField: {field: "text", direction: "asc"} });

    let tomSelectFacturaObra = new TomSelect("#obraFacturaSelect",{ create: false, sortField: {field: "text", direction: "asc"} });
    let cargasExtraidas = [];
    let facturaUUID = "";
    let facturaFecha = "";

    function updateOperacion(selectElement) {
        let val = selectElement.value;
        let parts = val.split("|");
        if(parts.length === 2) {
            document.getElementById('opCodigo').value = parts[0];
            document.getElementById('opNombre').value = parts[1];
        }
    }

    // Tab Switcher
    function switchTab(tab) {
        if(tab === 'consumo') {
            document.getElementById('formConsumoContainer').style.display = 'block';
            document.getElementById('formFacturaContainer').style.display = 'none';
            document.getElementById('historyConsumo').style.display = 'block';
            document.getElementById('historyFactura').style.display = 'none';
            document.getElementById('btnTabConsumo').style.background = 'var(--primary)';
            document.getElementById('btnTabConsumo').style.color = 'white';
            document.getElementById('btnTabFactura').style.background = 'transparent';
            document.getElementById('btnTabFactura').style.color = 'var(--text-muted)';
        } else {
            document.getElementById('formConsumoContainer').style.display = 'none';
            document.getElementById('formFacturaContainer').style.display = 'block';
            document.getElementById('historyConsumo').style.display = 'none';
            document.getElementById('historyFactura').style.display = 'block';
            document.getElementById('btnTabFactura').style.background = 'var(--primary)';
            document.getElementById('btnTabFactura').style.color = 'white';
            document.getElementById('btnTabConsumo').style.background = 'transparent';
            document.getElementById('btnTabConsumo').style.color = 'var(--text-muted)';
        }
    }

    // Auto-fill Responsable
    document.getElementById('obraSelect').addEventListener('change', async function(e) {
        const val = e.target.value;
        if(val) {
            const res = await fetch('/api/get_responsable/' + encodeURIComponent(val));
            const data = await res.json();
            if(data.responsable) document.getElementById('responsableInput').value = data.responsable;
        }
    });

    // Multiple Image Preview and Paste Handling
    let dtConsumo = new DataTransfer();
    const fileInputConsumo = document.getElementById('fileInputConsumo');
    const previewConsumo = document.getElementById('previewConsumo');
    const dropAreaConsumo = document.getElementById('dropAreaConsumo');

    function updatePreviews() {
        previewConsumo.innerHTML = '';
        if(dtConsumo.files.length > 0) {
            dropAreaConsumo.querySelector('.file-upload-text').style.display = 'none';
            for(let i=0; i<dtConsumo.files.length; i++){
                const src = URL.createObjectURL(dtConsumo.files[i]);
                const img = document.createElement('img');
                img.src = src;
                img.style.maxHeight = '80px';
                img.style.borderRadius = '8px';
                previewConsumo.appendChild(img);
            }
            fileInputConsumo.files = dtConsumo.files;
        } else {
            dropAreaConsumo.querySelector('.file-upload-text').style.display = 'block';
            fileInputConsumo.files = dtConsumo.files;
        }
    }

    fileInputConsumo.addEventListener('change', function(e) {
        if(e.target.files.length > 0) {
            for(let i=0; i<e.target.files.length; i++) {
                dtConsumo.items.add(e.target.files[i]);
            }
            updatePreviews();
        }
    });

    document.addEventListener('paste', function(e) {
        if(document.getElementById('formConsumoContainer').style.display === 'none') return;
        
        let items = (e.clipboardData || e.originalEvent.clipboardData).items;
        let foundImage = false;
        for (let index in items) {
            let item = items[index];
            if (item.kind === 'file' && item.type.startsWith('image/')) {
                let blob = item.getAsFile();
                let file = new File([blob], "img_pegada_" + Date.now() + ".jpg", {type: blob.type});
                dtConsumo.items.add(file);
                foundImage = true;
            }
        }
        if(foundImage) {
            updatePreviews();
            showToast("Imagen pegada exitosamente", "success");
        }
    });

    // Lector de Facturas API
    async function procesarFactura() {
        const pdfFile = document.getElementById('archivo_pdf_factura').files[0];
        const xmlFile = document.getElementById('archivo_xml_factura').files[0];
        
        if(pdfFile) {
            document.getElementById('pdfViewer').src = URL.createObjectURL(pdfFile);
        }

        if(!xmlFile) return;

        document.getElementById('loaderFactura').style.display = 'block';
        document.getElementById('resultadosFactura').style.display = 'none';

        const fd = new FormData();
        if(pdfFile) fd.append('archivo_pdf', pdfFile);
        fd.append('archivo_xml', xmlFile);

        try {
            const res = await fetch('/api/parse_factura', { method: 'POST', body: fd });
            const data = await res.json();
            
            document.getElementById('loaderFactura').style.display = 'none';
            document.getElementById('resultadosFactura').style.display = 'block';
            
            document.getElementById('lbl_uuid').innerText = data.uuid || 'No encontrado';
            document.getElementById('lbl_fecha').innerText = data.fecha || 'No encontrada';
            document.getElementById('lbl_obra_texto').innerText = data.obra_texto || 'No encontrado en PDF';
            
            facturaUUID = data.uuid;
            facturaFecha = data.fecha;
            cargasExtraidas = data.cargas;

            if(data.obra_sugerida) {
                tomSelectFacturaObra.setValue(data.obra_sugerida);
            }

            const listaDiv = document.getElementById('listaCargas');
            listaDiv.innerHTML = '';
            
            if(cargasExtraidas.length === 0) {
                listaDiv.innerHTML = '<p style="color:var(--danger)">No se detectaron partidas de Diésel.</p>';
            }

            cargasExtraidas.forEach((c, idx) => {
                listaDiv.innerHTML += 
                    <div style="background: rgba(255,255,255,0.05); padding: 0.5rem 1rem; border-radius: 8px; border-left: 4px solid var(--accent);">
                        <p style="margin:0; font-size:0.9rem"><strong>Carga #\</strong> - \</p>
                        <p style="margin:0; font-size:0.85rem; color:var(--text-muted)">Litros: \ | Precio: $\ | IVA: $\ | <strong>Total: $\</strong></p>
                    </div>
                ;
            });

        } catch(e) {
            console.error(e);
            alert('Error al leer los archivos');
            document.getElementById('loaderFactura').style.display = 'none';
        }
    }

    document.getElementById('archivo_pdf_factura').addEventListener('change', procesarFactura);
    document.getElementById('archivo_xml_factura').addEventListener('change', procesarFactura);

    // Handle Form Consumo
    document.getElementById('dieselForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        const btn = document.getElementById('submitBtnConsumo');
        btn.innerHTML = 'Guardando...';
        btn.disabled = true;

        try {
            const res = await fetch('/api/diesel/consumo', { method: 'POST', body: new FormData(this) });
            const result = await res.json();
            if(result.success) {
                showToast(result.message, 'success');
                setTimeout(() => window.location.reload(), 1500);
            } else {
                showToast(result.message, 'error');
            }
        } catch(error) { showToast('Error de conexión.', 'error'); } 
        finally { btn.innerHTML = 'Guardar Consumo'; btn.disabled = false; }
    });

    // Submit Facturas
    document.getElementById('facturaForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        if(cargasExtraidas.length === 0) {
            alert('No hay cargas de Diésel para guardar.');
            return;
        }
        const obra = tomSelectFacturaObra.getValue();
        if(!obra) { alert('Selecciona una obra destino'); return; }
        
        const btn = document.getElementById('submitBtnFactura');
        btn.innerHTML = 'Guardando...';
        btn.disabled = true;

        const payload = {
            uuid: facturaUUID,
            fecha: facturaFecha,
            obra: obra,
            cargas: cargasExtraidas
        };

        const res = await fetch('/api/diesel/facturas_batch', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if(data.success) {
            alert('Facturas guardadas con éxito!');
            window.location.reload();
        } else {
            alert('Error: ' + data.error);
            btn.innerHTML = 'Guardar Todas las Cargas';
            btn.disabled = false;
        }
    });
</script>'''

html = re.sub(r'<script>.*?</script>', clean_js, html, flags=re.DOTALL)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
