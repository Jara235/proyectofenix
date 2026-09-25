import re

html_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\servidor\templates\captura_v2\captura_diesel.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

new_factura_block = '''<!-- ==================== FORMULARIO DE FACTURAS ==================== -->
<div class="glass-card" id="formFacturaContainer" style="display: none;">
    <h3 style="margin-bottom: 1rem; color: var(--accent);">Extracción Automática de Facturas</h3>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;">
        
        <!-- Izquierda: Controles y Cargas -->
        <div>
            <form id="facturaForm">
                <div class="form-grid">
                    <div class="form-group">
                        <label>1. Cargar PDF (Opcional, para Punto de Carga)</label>
                        <input type="file" id="archivo_pdf_factura" name="archivo_pdf" accept=".pdf" style="padding: 0.5rem;" required>
                    </div>
                    <div class="form-group">
                        <label>2. Cargar XML (Requerido, para Importes)</label>
                        <input type="file" id="archivo_xml_factura" name="archivo_xml" accept=".xml" style="padding: 0.5rem;" required>
                    </div>
                </div>
                
                <div id="loaderFactura" style="display:none; color: var(--accent); margin: 1rem 0;">
                    ⏳ Extrayendo información con IA...
                </div>
                
                <div id="resultadosFactura" style="display:none; margin-top: 1rem;">
                    <div style="background: rgba(0,0,0,0.2); padding: 1rem; border-radius: 8px;">
                        <p style="margin-bottom:0.5rem"><strong>UUID:</strong> <span id="lbl_uuid"></span></p>
                        <p style="margin-bottom:0.5rem"><strong>Fecha:</strong> <span id="lbl_fecha"></span></p>
                        <p style="margin-bottom:0.5rem"><strong>Obra Detectada en PDF:</strong> <span id="lbl_obra_texto" style="color:var(--primary)"></span></p>
                    </div>
                    
                    <div class="form-group" style="margin-top:1rem;">
                        <label>Confirmar Obra Destino</label>
                        <select name="obra_destino" id="obraFacturaSelect" required placeholder="Selecciona obra...">
                            <option value="">Selecciona obra...</option>
                            {% for ob in obras %}
                                <option value="{{ ob['nombre'] }}">{{ ob['codigo'] }} - {{ ob['nombre'] }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    
                    <h4 style="margin-top: 1rem; color: var(--text-main);">Cargas de Diésel Encontradas</h4>
                    <div id="listaCargas" style="margin-top: 0.5rem; display: flex; flex-direction: column; gap: 0.5rem;">
                        <!-- Se llena con JS -->
                    </div>
                    
                    <button type="submit" class="btn-primary" id="submitBtnFactura" style="margin-top: 1rem; background: linear-gradient(135deg, var(--accent), var(--primary)); width: 100%;">
                        Guardar Todas las Cargas
                    </button>
                </div>
            </form>
        </div>
        
        <!-- Derecha: Visor de PDF -->
        <div style="background: rgba(0,0,0,0.1); border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); overflow: hidden; height: 600px;">
            <iframe id="pdfViewer" style="width: 100%; height: 100%; border: none;" src=""></iframe>
        </div>
        
    </div>
</div>
'''

html = re.sub(r'<!-- ==================== FORMULARIO DE FACTURAS ==================== -->.*?</div>', new_factura_block, html, flags=re.DOTALL)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
