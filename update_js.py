import re

html_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\servidor\templates\captura_v2\captura_diesel.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Add JS logic for parse_factura
js_logic = '''
    // Initialize Factura dropdowns
    let tomSelectFacturaObra = new TomSelect("#obraFacturaSelect",{ create: false, sortField: {field: "text", direction: "asc"} });
    let cargasExtraidas = [];
    let facturaUUID = "";
    let facturaFecha = "";

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
                        <p style="margin:0; font-size:0.9rem"><strong>Carga #</strong> - </p>
                        <p style="margin:0; font-size:0.85rem; color:var(--text-muted)">Litros:  | Precio: {c.precio} | IVA: {c.iva} | <strong>Total: {c.total}</strong></p>
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
    
    // Submit Facturas
    document.getElementById('facturaForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        if(cargasExtraidas.length === 0) {
            alert('No hay cargas de Diésel para guardar.');
            return;
        }
        const obra = tomSelectFacturaObra.getValue();
        if(!obra) { alert('Selecciona una obra destino'); return; }

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
        }
    });
'''

html = html.replace('// Initialize Searchable Dropdowns', js_logic + '\n    // Initialize Searchable Dropdowns')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
