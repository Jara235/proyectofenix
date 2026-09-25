import re

with open(r'servidor\templates\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

new_html = '''<!-- ══════════════════ GASOLINA ══════════════════ -->
<div id="panel-gasolina" class="panel">
  <div id="gasolina-kpi" class="kpi-grid"></div>
  
  <div class="section-title">Conciliación: Alertas de Desviación (Matriz vs Gasolineras)</div>
  <div id="gasolina-alertas" class="grid-2" style="margin-bottom: 20px;"></div>
  
  <div class="section-title">Matriz de Control Operativo (Autorizado vs Deducciones Diarias)</div>
  <div class="chart-card" style="overflow-x: auto;">
    <div class="table-wrap">
      <table id="table-matriz-gasolina" style="min-width: 1500px;">
        <thead id="thead-matriz-gasolina">
          <!-- Se llena dinamicamente -->
        </thead>
        <tbody id="tbody-matriz-gasolina">
          <!-- Se llena dinamicamente -->
        </tbody>
      </table>
    </div>
  </div>
</div>'''

new_js = '''// ─── GASOLINA ────────────────────────────────────────────────────────────
async function loadGasolina(){
  const [kpis, matrizData, alertas] = await Promise.all([
    fetch('/api/gasolina/kpis'+q()).then(r=>r.json()),
    fetch('/api/gasolina/matriz'+q()).then(r=>r.json()),
    fetch('/api/gasolina/conciliacion'+q()).then(r=>r.json())
  ]);
  
  // 1. KPIs
  document.getElementById('gasolina-kpi').innerHTML = `
    <div class="kpi-card"><span class="kpi-icon">📋</span><div class="kpi-label">Presupuesto Autorizado</div><div class="kpi-value mono">${fmtP(kpis.importe_autorizado)}</div><div class="kpi-sub">Según Excel</div></div>
    <div class="kpi-card amber"><span class="kpi-icon">📉</span><div class="kpi-label">Consumo Reportado</div><div class="kpi-value mono text-amber">${fmtP(kpis.importe_reportado)}</div><div class="kpi-sub">Deducciones Matriz</div></div>
    <div class="kpi-card green"><span class="kpi-icon">⛽</span><div class="kpi-label">Gasto Real (Tickets)</div><div class="kpi-value mono text-green">${fmtP(kpis.importe_real)}</div><div class="kpi-sub">${fmt(kpis.litros_real)} L</div></div>
  `;
  
  // 2. Alertas de Conciliación
  const alertasDiv = document.getElementById('gasolina-alertas');
  if (alertas.length === 0) {
    alertasDiv.innerHTML = '<div class="alert-box"><div class="icon">✅</div><div><h4>Conciliación Cuadrada</h4><p>No hay diferencias > $10 entre la matriz y los reportes de gasolineras.</p></div></div>';
  } else {
    alertasDiv.innerHTML = alertas.map(a => `
      <div class="alert-box" style="border-left: 4px solid #ef4444;">
        <div class="icon">🚨</div>
        <div>
          <h4>Diferencia en ${a.placa} el ${a.fecha}</h4>
          <p>Se reportaron <b>${fmtP(a.monto_excel)}</b> en Excel vs <b>${fmtP(a.monto_ticket)}</b> en ${a.proveedor}. (Diff: ${fmtP(a.diferencia)})</p>
        </div>
      </div>
    `).join('');
  }
  
  // 3. Renderizar Matriz Compleja
  const thead = document.getElementById('thead-matriz-gasolina');
  const tbody = document.getElementById('tbody-matriz-gasolina');
  
  let headerRow1 = `<tr><th rowspan="2" style="background:#0ea5e9; color:white;">Responsable</th><th rowspan="2" style="background:#0ea5e9; color:white;">Centro de Trabajo</th><th rowspan="2" style="background:#0ea5e9; color:white;">Unidad / Equipo</th><th rowspan="2" style="background:#0ea5e9; color:white;">Placas</th><th rowspan="2" style="background:#0ea5e9; color:white;">Importe Semanal Autorizado</th>`;
  let headerRow2 = `<tr>`;
  
  matrizData.fechas.forEach(f => {
    headerRow1 += `<th colspan="3" style="text-align:center; background:#bbf7d0; color:#166534;">${f}</th>`;
    headerRow2 += `<th>LEVET</th><th>MOBILE</th><th>SIVALE</th>`;
  });
  
  headerRow1 += `</tr>`;
  headerRow2 += `</tr>`;
  thead.innerHTML = headerRow1 + headerRow2;
  
  let trs = '';
  let lastResponsable = '';
  
  matrizData.filas.forEach((r, idx) => {
    // Para no repetir el responsable visualmente si es el mismo, o pintar fondo distinto
    let isNewResp = r.responsable !== lastResponsable;
    let respText = isNewResp ? r.responsable : '';
    lastResponsable = r.responsable;
    
    // Calcular totales de consumo de esa fila
    let totFila = 0;
    r.dias.forEach(d => { totFila += d.levet + d.mobile + d.sivale; });
    let saldo = r.autorizado - totFila;
    
    trs += `<tr>
      <td style="font-weight:bold; color:var(--text-color);">${respText}</td>
      <td>${r.obra || ''}</td>
      <td>${r.unidad || ''}</td>
      <td class="mono">${r.placa || ''}</td>
      <td class="mono text-green" style="font-weight:bold">${fmtP(r.autorizado)}</td>
    `;
    
    r.dias.forEach(d => {
      trs += `
        <td class="mono ${d.levet>0?'text-amber':''}">${d.levet>0 ? fmtP(d.levet) : ''}</td>
        <td class="mono ${d.mobile>0?'text-blue':''}">${d.mobile>0 ? fmtP(d.mobile) : ''}</td>
        <td class="mono ${d.sivale>0?'text-purple':''}">${d.sivale>0 ? fmtP(d.sivale) : ''}</td>
      `;
    });
    trs += `</tr>`;
  });
  
  tbody.innerHTML = trs;
}'''

start_html = content.find('<!-- ══════════════════ GASOLINA ══════════════════ -->')
end_html = content.find('<!-- ══════════════════ ACARREOS ══════════════════ -->')
content = content[:start_html] + new_html + '\n\n' + content[end_html:]

start_js = content.find('// ─── GASOLINA ────────────────────────────────────────────────────────────')
end_js = content.find('// ─── ACARREOS ────────────────────────────────────────────────────────────')
content = content[:start_js] + new_js + '\n\n' + content[end_js:]

with open(r'servidor\templates\index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('HTML Patched')
