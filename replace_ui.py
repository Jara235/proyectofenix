import sys
import re

with open(r'c:\Users\JOSE\Desktop\Proyecto fenix\servidor\templates\admin\admin_resumen.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Replace the headers for responsables
content = content.replace(
    '''                            <th>🏗️ Obra / Centro de Trabajo</th>
                            <th>👤 Responsable</th>''',
    '''                            <th>👤 Responsable</th>
                            <th>🏗️ Obras / Centros de Trabajo</th>'''
)
content = content.replace(
    'Autorizado vs Consumido por Obra y Responsable',
    'Autorizado vs Consumido por Responsable (Sumando todas sus obras)'
)

# 2. Update tbody building inside cargarResponsables()
content = content.replace(
    '''                    <td>${r.obra || '—'}</td>
                    <td>${r.responsable}</td>''',
    '''                    <td>${r.responsable}</td>
                    <td>${r.obras || '—'}</td>'''
)

# 3. Add tabla-maquinaria after panel-responsables-wrapper
new_table_html = '''    </div> <!-- end panel-responsables-wrapper -->

    <!-- ==================== TABLA: MAQUINARIA ==================== -->
    <style>
        #tabla-maquinaria td {
            font-size: 0.75rem;
            padding: 4px 12px;
            border-bottom: 1px solid var(--border);
        }
        #tabla-maquinaria th {
            font-size: 0.75rem;
            background-color: var(--surface-hover);
        }
        #tabla-maquinaria .tot-row td {
            font-weight: 700;
            background-color: #f8fafc;
        }
    </style>
    <div class="split-view" style="grid-template-columns: 1fr; margin-top: 12px;" id="panel-maquinaria-wrapper">
        <div class="admin-card">
            <div class="card-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <div>
                    <h3 id="maquinaria-titulo" style="margin: 0; font-size: 1rem; color: #1e293b;">🚜 Desglose por Maquinaria</h3>
                    <div style="font-size: 0.75rem; color: var(--text-muted);">Consumido por Obra y Equipo</div>
                </div>
            </div>
            <div class="table-responsive">
                <table class="admin-table" id="tabla-maquinaria">
                    <thead>
                        <tr>
                            <th>🏗️ Obra / Centro de Trabajo</th>
                            <th>🚜 Maquinaria / Equipo</th>
                            <th style="text-align: right;">Autorizado (L)</th>
                            <th style="text-align: right;">Consumido (L)</th>
                        </tr>
                    </thead>
                    <tbody id="tbody-maquinaria">
                        <tr><td colspan="4" style="text-align:center; color:var(--text-muted);">Seleccione una semana para ver datos</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
'''
content = content.replace('    </div>\n\n    <!-- ==================== LOGICA JS ==================== -->', new_table_html + '\n    <!-- ==================== LOGICA JS ==================== -->')

# 4. Add cargarMaquinaria() to JS
new_js = '''
    async function cargarMaquinaria() {
        const tbody  = document.getElementById('tbody-maquinaria');
        const semanaParam = document.getElementById('filtro-semana').value;
        const wrapper = document.getElementById('panel-maquinaria-wrapper');

        if (currentModulo !== 'diesel') {
            wrapper.style.display = 'none';
            return;
        }
        wrapper.style.display = 'block';

        tbody.innerHTML = '<tr><td colspan="4" style="text-align:center; color:var(--text-muted);"><i class="fas fa-spinner fa-spin"></i> Cargando desglose de maquinaria...</td></tr>';
        document.getElementById('maquinaria-titulo').textContent = `🚜 Desglose por Maquinaria - Semana ${semanaParam}`;

        try {
            const url = `/api/admin/resumen/maquinaria?modulo=${currentModulo}&semana=${encodeURIComponent(semanaParam)}`;
            const res = await fetch(url);
            const data = await res.json();
            
            if (data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="4" style="text-align:center; color:var(--text-muted);">No hay registros de consumos aprobados.</td></tr>';
                return;
            }

            let html = '';
            let totCon = 0;

            data.forEach(r => {
                const con = parseFloat(r.consumido || 0);
                totCon += con;

                html += `<tr>
                    <td>${r.obra || '—'}</td>
                    <td>${r.maquinaria}</td>
                    <td style="text-align:right;">—</td>
                    <td style="text-align:right;">${con.toLocaleString('en-US', {minimumFractionDigits:2, maximumFractionDigits:2})} L</td>
                </tr>`;
            });

            // Totals
            html += `<tr class="tot-row">
                <td colspan="2" style="color: #1e293b; padding: 6px 12px; text-align: right;">TOTAL MAQUINARIA</td>
                <td style="text-align:right;">—</td>
                <td style="text-align:right;">${totCon.toLocaleString('en-US', {minimumFractionDigits:2, maximumFractionDigits:2})} L</td>
            </tr>`;

            tbody.innerHTML = html;
        } catch (err) {
            console.error(err);
            tbody.innerHTML = '<tr><td colspan="4" style="text-align:center; color:#ef4444;">Error al cargar desglose de maquinaria.</td></tr>';
        }
    }
'''

content = content.replace('    async function cargarResponsables() {', new_js + '\n    async function cargarResponsables() {')
content = content.replace('cargarResponsables();', 'cargarResponsables();\n        cargarMaquinaria();')

with open(r'c:\Users\JOSE\Desktop\Proyecto fenix\servidor\templates\admin\admin_resumen.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Replaced UI.")
