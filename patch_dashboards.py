import os

def patch_diesel(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Add HTML Card
    if '<!-- DIESEL AUTORIZACIONES -->' not in content:
        target_html = '<!-- DIESEL CONCILIACION -->'
        card_html = '''
    <!-- DIESEL AUTORIZACIONES -->
    <div class="card" style="border-top: 2px solid rgba(239, 68, 68, 0.3);">
        <div class="card-header">
            <div>
                <div class="card-title" style="color:#ef4444;">🚨 Autorizaciones vs Consumidos</div>
                <div class="card-sub">Litros autorizados por obra vs consumos reales aprobados</div>
            </div>
        </div>
        <div style="overflow-x:auto;">
            <table>
                <thead>
                    <tr>
                        <th>Obra</th>
                        <th style="text-align:right;color:#10b981;">Lts. Autorizados</th>
                        <th style="text-align:right;color:#3b82f6;">Lts. Consumidos</th>
                        <th style="text-align:right;">Estatus</th>
                    </tr>
                </thead>
                <tbody id="diesel-auth-tbody"><tr><td colspan="4" style="text-align:center;padding:2rem;color:var(--muted);">Cargando...</td></tr></tbody>
            </table>
        </div>
    </div>

'''
        content = content.replace(target_html, card_html + target_html)

    # 2. Add JS Function
    if 'async function loadDieselAuth()' not in content:
        target_js = 'async function reloadAll()'
        js_func = '''
    async function loadDieselAuth() {
        const sem = getSemana();
        const res = await fetch('/api/diesel/autorizaciones?semana=' + encodeURIComponent(sem));
        const d   = await res.json();
        if (!d.success) return;

        const tbody = document.getElementById('diesel-auth-tbody');
        tbody.innerHTML = '';
        if (!d.data || d.data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;padding:2rem;color:var(--muted);">Sin datos de autorizaciones</td></tr>';
            return;
        }

        d.data.forEach(r => {
            const st = r.excedido ? '<span style="background:rgba(239,68,68,0.12);color:#ef4444;font-weight:700;border-radius:12px;padding:2px 10px;">EXCEDIDO</span>' : '<span style="background:rgba(16,185,129,0.12);color:#10b981;font-weight:700;border-radius:12px;padding:2px 10px;">EN REGLA</span>';
            tbody.innerHTML += `<tr>
                <td style="font-weight:600;">${r.obra}</td>
                <td style="text-align:right;color:#10b981;">${N.format(r.autorizado)} L</td>
                <td style="text-align:right;color:#3b82f6;">${N.format(r.consumido)} L</td>
                <td style="text-align:right;">${st}</td>
            </tr>`;
        });
    }

'''
        content = content.replace(target_js, js_func + target_js)
        
    # 3. Add to reloadAll
    if 'loadDieselAuth();' not in content:
        content = content.replace('loadDieselConcObra();', 'loadDieselConcObra();\n        loadDieselAuth();')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def patch_gasolina(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Add HTML Card
    if '<!-- GASOLINA AUTORIZACIONES -->' not in content:
        target_html = '<!-- GASOLINA RENDIMIENTO -->'
        if target_html not in content:
            target_html = '<!-- GASOLINA POR VEHICULO -->'
            
        card_html = '''
    <!-- GASOLINA AUTORIZACIONES -->
    <div class="card" style="border-top: 2px solid rgba(239, 68, 68, 0.3);">
        <div class="card-header">
            <div>
                <div class="card-title" style="color:#ef4444;">🚨 Autorizaciones vs Consumidos</div>
                <div class="card-sub">Litros autorizados por vehículo vs consumos reales aprobados</div>
            </div>
        </div>
        <div style="overflow-x:auto;">
            <table>
                <thead>
                    <tr>
                        <th>Vehículo</th>
                        <th style="text-align:right;color:#10b981;">Lts. Autorizados</th>
                        <th style="text-align:right;color:#3b82f6;">Lts. Consumidos</th>
                        <th style="text-align:right;">Estatus</th>
                    </tr>
                </thead>
                <tbody id="gasolina-auth-tbody"><tr><td colspan="4" style="text-align:center;padding:2rem;color:var(--muted);">Cargando...</td></tr></tbody>
            </table>
        </div>
    </div>

'''
        content = content.replace(target_html, card_html + target_html)

    # 2. Add JS Function
    if 'async function loadGasolinaAuth()' not in content:
        target_js = 'async function reloadAll()'
        js_func = '''
    async function loadGasolinaAuth() {
        const sem = getSemana();
        const res = await fetch('/api/gasolina/autorizaciones?semana=' + encodeURIComponent(sem));
        const d   = await res.json();
        if (!d.success) return;

        const tbody = document.getElementById('gasolina-auth-tbody');
        if(!tbody) return;
        tbody.innerHTML = '';
        if (!d.data || d.data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;padding:2rem;color:var(--muted);">Sin datos de autorizaciones</td></tr>';
            return;
        }

        d.data.forEach(r => {
            const st = r.excedido ? '<span style="background:rgba(239,68,68,0.12);color:#ef4444;font-weight:700;border-radius:12px;padding:2px 10px;">EXCEDIDO</span>' : '<span style="background:rgba(16,185,129,0.12);color:#10b981;font-weight:700;border-radius:12px;padding:2px 10px;">EN REGLA</span>';
            tbody.innerHTML += `<tr>
                <td style="font-weight:600;">${r.vehiculo}</td>
                <td style="text-align:right;color:#10b981;">${N.format(r.autorizado)} L</td>
                <td style="text-align:right;color:#3b82f6;">${N.format(r.consumido)} L</td>
                <td style="text-align:right;">${st}</td>
            </tr>`;
        });
    }

'''
        content = content.replace(target_js, js_func + target_js)
        
    # 3. Add to reloadAll
    if 'loadGasolinaAuth();' not in content:
        content = content.replace('loadGasolinaComparativo();', 'loadGasolinaComparativo();\n        loadGasolinaAuth();')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

diesel_path = r"c:\Users\JOSE\Desktop\Proyecto fenix\servidor\templates\dashboard\dashboard_diesel.html"
gasolina_path = r"c:\Users\JOSE\Desktop\Proyecto fenix\servidor\templates\dashboard\dashboard_gasolina.html"

patch_diesel(diesel_path)
patch_gasolina(gasolina_path)
print("Dashboards HTML actualizados.")
