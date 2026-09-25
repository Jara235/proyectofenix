import re

html_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\servidor\templates\captura_v2\captura_diesel.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Add Dashboard Tab
tab_buttons = '''
    <div style="background: rgba(0,0,0,0.3); border-radius: 12px; padding: 4px; display: flex; gap: 4px;">
        <button id="btnTabConsumo" class="tab-btn active" onclick="switchTab('consumo')" style="padding: 0.5rem 1rem; border-radius: 8px; border: none; background: var(--primary); color: white; cursor: pointer; font-weight: 600;">Consumos</button>
        <button id="btnTabFactura" class="tab-btn" onclick="switchTab('factura')" style="padding: 0.5rem 1rem; border-radius: 8px; border: none; background: transparent; color: var(--text-muted); cursor: pointer; font-weight: 600;">Facturas Automáticas</button>
        <button id="btnTabDashboard" class="tab-btn" onclick="switchTab('dashboard')" style="padding: 0.5rem 1rem; border-radius: 8px; border: none; background: transparent; color: var(--text-muted); cursor: pointer; font-weight: 600;">Resumen Dashboard</button>
    </div>
'''
html = re.sub(r'<div style="background: rgba\(0,0,0,0\.3\); border-radius: 12px; padding: 4px; display: flex; gap: 4px;">.*?</div>', tab_buttons, html, flags=re.DOTALL)

# Add Dashboard Container before History Section
dashboard_html = '''
<!-- ==================== DASHBOARD RESUMEN ==================== -->
<div class="glass-card" id="formDashboardContainer" style="display: none; margin-bottom: 2rem;">
    <h3 style="margin-bottom: 1rem; color: var(--accent);">Resumen General (Consumos vs Facturación)</h3>
    
    <!-- Filtros -->
    <div class="form-grid" style="margin-bottom: 2rem;">
        <div class="form-group">
            <label>Filtrar por Obra Destino</label>
            <select id="dashObraSelect" onchange="loadDashboard()">
                <option value="">Todas las Obras</option>
                {% for o in obras %}
                    <option value="{{ o['nombre'] }}">{{ o['nombre'] }}</option>
                {% endfor %}
            </select>
        </div>
        <div class="form-group">
            <label>Filtrar por Tipo de Movimiento</label>
            <select id="dashMovSelect" onchange="loadDashboard()">
                <option value="">Todos los Movimientos</option>
                {% for op in operaciones %}
                    <option value="{{ op['tipo_operacion'] }}">{{ op['tipo_operacion'] }}</option>
                {% endfor %}
            </select>
        </div>
    </div>
    
    <!-- KPIs -->
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem;">
        <div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px; border-left: 4px solid #3b82f6;">
            <p style="margin: 0; color: var(--text-muted); font-size: 0.9rem;">Litros Consumidos</p>
            <h2 id="kpiLtsCons" style="margin: 0.5rem 0 0 0; color: white;">0.00</h2>
        </div>
        <div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px; border-left: 4px solid #10b981;">
            <p style="margin: 0; color: var(--text-muted); font-size: 0.9rem;">Litros Facturados</p>
            <h2 id="kpiLtsFact" style="margin: 0.5rem 0 0 0; color: white;">0.00</h2>
        </div>
        <div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px; border-left: 4px solid #eab308;">
            <p style="margin: 0; color: var(--text-muted); font-size: 0.9rem;">Importe Consumido</p>
            <h2 id="kpiImpCons" style="margin: 0.5rem 0 0 0; color: white;">.00</h2>
        </div>
        <div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px; border-left: 4px solid #8b5cf6;">
            <p style="margin: 0; color: var(--text-muted); font-size: 0.9rem;">Importe Facturado</p>
            <h2 id="kpiImpFact" style="margin: 0.5rem 0 0 0; color: white;">.00</h2>
        </div>
    </div>
    
    <!-- Tabla -->
    <div style="overflow-x: auto;">
        <table style="width: 100%; text-align: left; border-collapse: collapse;">
            <thead>
                <tr style="border-bottom: 1px solid var(--border-color);">
                    <th style="padding: 0.75rem;">Semana</th>
                    <th style="padding: 0.75rem; text-align: right;">Lts. Consumidos</th>
                    <th style="padding: 0.75rem; text-align: right;">Lts. Facturados</th>
                    <th style="padding: 0.75rem; text-align: right;">Imp. Consumido</th>
                    <th style="padding: 0.75rem; text-align: right;">Imp. Facturado</th>
                    <th style="padding: 0.75rem; text-align: right;">Dif. Lts (Fact-Cons)</th>
                </tr>
            </thead>
            <tbody id="dashTableBody">
                <!-- Data from JS -->
            </tbody>
        </table>
    </div>
</div>

<h3 style="margin-bottom: 1rem; color: var(--text-main);" id="historicoTitle">Últimos Registros Capturados</h3>
'''
html = re.sub(r'<h3 style="margin-bottom: 1rem; color: var\(--text-main\);">Últimos Registros Capturados</h3>', dashboard_html, html)

# Modify switchTab function logic in JS
switch_tab_js = '''    function switchTab(tab) {
        document.getElementById('formConsumoContainer').style.display = 'none';
        document.getElementById('formFacturaContainer').style.display = 'none';
        document.getElementById('formDashboardContainer').style.display = 'none';
        document.getElementById('historyConsumo').style.display = 'none';
        document.getElementById('historyFactura').style.display = 'none';
        document.getElementById('historicoTitle').style.display = 'none';
        
        document.getElementById('btnTabConsumo').style.background = 'transparent';
        document.getElementById('btnTabConsumo').style.color = 'var(--text-muted)';
        document.getElementById('btnTabFactura').style.background = 'transparent';
        document.getElementById('btnTabFactura').style.color = 'var(--text-muted)';
        document.getElementById('btnTabDashboard').style.background = 'transparent';
        document.getElementById('btnTabDashboard').style.color = 'var(--text-muted)';

        if(tab === 'consumo') {
            document.getElementById('formConsumoContainer').style.display = 'block';
            document.getElementById('historyConsumo').style.display = 'block';
            document.getElementById('historicoTitle').style.display = 'block';
            document.getElementById('btnTabConsumo').style.background = 'var(--primary)';
            document.getElementById('btnTabConsumo').style.color = 'white';
        } else if(tab === 'factura') {
            document.getElementById('formFacturaContainer').style.display = 'block';
            document.getElementById('historyFactura').style.display = 'block';
            document.getElementById('historicoTitle').style.display = 'block';
            document.getElementById('btnTabFactura').style.background = 'var(--primary)';
            document.getElementById('btnTabFactura').style.color = 'white';
        } else if(tab === 'dashboard') {
            document.getElementById('formDashboardContainer').style.display = 'block';
            document.getElementById('btnTabDashboard').style.background = 'var(--primary)';
            document.getElementById('btnTabDashboard').style.color = 'white';
            loadDashboard();
        }
    }

    async function loadDashboard() {
        const obra = document.getElementById('dashObraSelect').value;
        const mov = document.getElementById('dashMovSelect').value;
        
        try {
            const res = await fetch(/api/diesel/dashboard?obra=&movimiento=);
            const data = await res.json();
            if(data.success) {
                const numFormat = new Intl.NumberFormat('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
                const curFormat = new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' });
                
                document.getElementById('kpiLtsCons').innerText = numFormat.format(data.kpis.litros_consumidos);
                document.getElementById('kpiLtsFact').innerText = numFormat.format(data.kpis.litros_facturados);
                document.getElementById('kpiImpCons').innerText = curFormat.format(data.kpis.importe_consumido);
                document.getElementById('kpiImpFact').innerText = curFormat.format(data.kpis.importe_facturado);
                
                const tbody = document.getElementById('dashTableBody');
                tbody.innerHTML = '';
                
                if(data.table.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; padding: 1rem; color: var(--text-muted);">No hay datos para estos filtros.</td></tr>';
                }
                
                data.table.forEach(r => {
                    const difLts = r.litros_facturados - r.litros_consumidos;
                    const difColor = difLts >= 0 ? '#10b981' : '#ef4444';
                    
                    tbody.innerHTML += 
                        <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                            <td style="padding: 0.75rem; color: var(--accent);"><strong></strong></td>
                            <td style="padding: 0.75rem; text-align: right;"></td>
                            <td style="padding: 0.75rem; text-align: right; color: var(--primary);"></td>
                            <td style="padding: 0.75rem; text-align: right;"></td>
                            <td style="padding: 0.75rem; text-align: right;"></td>
                            <td style="padding: 0.75rem; text-align: right; font-weight: bold; color: ;"></td>
                        </tr>
                    ;
                });
            }
        } catch(e) { console.error("Error loading dashboard", e); }
    }
'''
html = re.sub(r'    function switchTab\(tab\) \{.*?(?=    // Auto-fill Responsable)', switch_tab_js + '\n', html, flags=re.DOTALL)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
