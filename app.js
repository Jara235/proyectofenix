/* ==========================================================================
   APPLICATION LOGIC: PROYECTO FÉNIX (DASHBOARD & SECURE AI ASSISTANT)
   ========================================================================== */

// --- Configuration & Global State ---
let supabaseClient = null;
let useMockData = true;

// Mock Database (Fallback / Demo mode)
let mockDb = {
    obras: [
        { id: "o1", codigo: "MT", nombre: "México-Toluca" },
        { id: "o2", codigo: "L3M", nombre: "Lerma - Tres Marías" },
        { id: "o3", codigo: "CL", nombre: "Chamapa-Lechería" },
        { id: "o4", codigo: "LT", nombre: "Lerma-Tenango" }
    ],
    equipos: [
        { id: "e1", codigo_economico: "PER-200", tipo_equipo: "Perfiladora Wirtgen F-200", tipo_rendimiento: "horas" },
        { id: "e2", codigo_economico: "VOG-03", tipo_equipo: "Vögele-03", tipo_rendimiento: "horas" },
        { id: "e3", codigo_economico: "HAMM", tipo_equipo: "Tándem Hamm", tipo_rendimiento: "horas" },
        { id: "e4", codigo_economico: "DINA", tipo_equipo: "Neumático Dinapac", tipo_rendimiento: "horas" },
        { id: "e5", codigo_economico: "BAR-01", tipo_equipo: "Barredora Broce Broom", tipo_rendimiento: "horas" },
        { id: "e6", codigo_economico: "RET-02", tipo_equipo: "Retroexcavadora", tipo_rendimiento: "horas" },
        { id: "e7", codigo_economico: "PET-02", tipo_equipo: "Petrolizadora", tipo_rendimiento: "horas" },
        { id: "e8", codigo_economico: "CAM-02", tipo_equipo: "Camión Impacto", tipo_rendimiento: "kilometros" },
        { id: "e9", codigo_economico: "COM-01", tipo_equipo: "Compresor Ingersoll Rand", tipo_rendimiento: "horas" },
        { id: "e10", codigo_economico: "TL-01", tipo_equipo: "Torre de Luces Maxilight", tipo_rendimiento: "horas" },
        { id: "e11", codigo_economico: "CP-01", tipo_equipo: "Compactador", tipo_rendimiento: "horas" },
        { id: "e12", codigo_economico: "EX-01", tipo_equipo: "Excavadora", tipo_rendimiento: "horas" }
    ],
    pegaso: [
        { id: "p1", fecha: "2026-06-15", tipo_movimiento: "Entrada", origen_destino: "Gasolinera Huixquilucan", obra_id: null, equipo_id: null, litros_entrada: 5000, litros_salida: 0, costo_por_litro: 27.20, importe: 136000, observaciones: "Carga semanal inicial Factura F-9921", image_url: "ticket_gasolina.jpg" },
        { id: "p2", fecha: "2026-06-15", tipo_movimiento: "Salida a Marimba", origen_destino: "Tanque Pegaso", obra_id: "o1", equipo_id: null, litros_entrada: 0, litros_salida: 1500, costo_por_litro: 27.20, importe: 40800, observaciones: "Carga a Mamba M-01 para obra MT", image_url: "medidor_pegaso.jpg" },
        { id: "p3", fecha: "2026-06-15", tipo_movimiento: "Salida Directa Máquina", origen_destino: "Tanque Pegaso", obra_id: "o4", equipo_id: "e2", litros_entrada: 0, litros_salida: 90, costo_por_litro: 27.20, importe: 2448, observaciones: "Suministro directo a Vögele-03 en LT", image_url: "odometro.jpg" }
    ],
    marimba: [
        { id: "m1", fecha: "2026-06-15", tipo_movimiento: "Entrada desde Pegaso", origen_obra_id: "o1", equipo_id: null, litros_entrada: 1500, litros_salida: 0, costo_por_litro: 27.20, importe: 40800, observaciones: "Carga recibida de Tanque Pegaso", image_url: "medidor_pegaso.jpg" },
        { id: "m2", fecha: "2026-06-15", tipo_movimiento: "Salida a Obra", origen_obra_id: "o1", equipo_id: "e1", litros_entrada: 0, litros_salida: 250, costo_por_litro: 27.20, importe: 6800, observaciones: "Despacho Perfiladora Wirtgen", image_url: "odometro.jpg" },
        { id: "m3", fecha: "2026-06-15", tipo_movimiento: "Salida a Obra", origen_obra_id: "o1", equipo_id: "e2", litros_entrada: 0, litros_salida: 100, costo_por_litro: 27.20, importe: 2720, observaciones: "Despacho Vogele-03", image_url: "odometro.jpg" }
    ],
    obra: [
        { id: "ob1", fecha: "2026-06-15", obra_id: "o1", fuente: "Marimba M-01", equipo_id: "e1", litros_recibidos: 250, costo_por_litro: 27.20, importe: 6800, actividad_ejecutada: "Perfilado de carpeta asfáltica", incidencia: "Ninguna", horas_trabajadas: 6, kilometraje: null, observaciones: "Ticket flujómetro 0250", image_url: "odometro.jpg" },
        { id: "ob2", fecha: "2026-06-15", obra_id: "o1", fuente: "Marimba M-01", equipo_id: "e2", litros_recibidos: 100, costo_por_litro: 27.20, importe: 2720, actividad_ejecutada: "Pavimentación de tramo principal", incidencia: "Ninguna", horas_trabajadas: 4.5, kilometraje: null, observaciones: "Suministro normal", image_url: "odometro.jpg" },
        { id: "ob3", fecha: "2026-06-15", obra_id: "o4", fuente: "Pegaso Directo", equipo_id: "e2", litros_recibidos: 90, costo_por_litro: 27.20, importe: 2448, actividad_ejecutada: "Apoyo carpeta asfáltica frente 1", incidencia: "Ninguna", horas_trabajadas: 5.5, kilometraje: null, observaciones: "Recepción directa tanque Pegaso", image_url: "odometro.jpg" }
    ],
    estimates: [
        { id: "est1", semana_fecha: "2026-06-15", obra_id: "o1", equipo_id: "e1", litros_estimados: 250 },
        { id: "est2", semana_fecha: "2026-06-15", obra_id: "o1", equipo_id: "e2", litros_estimados: 120 },
        { id: "est3", semana_fecha: "2026-06-15", obra_id: "o1", equipo_id: "e3", litros_estimados: 50 },
        { id: "est4", semana_fecha: "2026-06-15", obra_id: "o1", equipo_id: "e4", litros_estimados: 50 },
        { id: "est5", semana_fecha: "2026-06-15", obra_id: "o1", equipo_id: "e5", litros_estimados: 40 },
        { id: "est6", semana_fecha: "2026-06-15", obra_id: "o1", equipo_id: "e6", litros_estimados: 60 },
        { id: "est7", semana_fecha: "2026-06-15", obra_id: "o1", equipo_id: "e7", litros_estimados: 50 },
        { id: "est8", semana_fecha: "2026-06-15", obra_id: "o1", equipo_id: "e8", litros_estimados: 30 },
        { id: "est9", semana_fecha: "2026-06-15", obra_id: "o4", equipo_id: "e2", litros_estimados: 90 },
        { id: "est10", semana_fecha: "2026-06-15", obra_id: "o4", equipo_id: "e4", litros_estimados: 40 },
        { id: "est11", semana_fecha: "2026-06-15", obra_id: "o4", equipo_id: "e5", litros_estimados: 40 }
    ],
    whatsapp: []
};

// Mock images definitions
const mockImages = {
    "ticket_gasolina.jpg": "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?auto=format&fit=crop&q=80&w=800",
    "medidor_pegaso.jpg": "https://images.unsplash.com/photo-1581092160607-ee22621dd758?auto=format&fit=crop&q=80&w=800",
    "odometro.jpg": "https://images.unsplash.com/photo-1517524206127-48bbd363f3d7?auto=format&fit=crop&q=80&w=800"
};

// Charts State
let chartFlow = null;
let chartPerformance = null;
let chartDistribution = null;
let chartPeticionesDiaObra = null;
let chartMarimbaDiaObra = null;
let chartPegasoDiaObra = null;

// --- App Initialization ---
document.addEventListener("DOMContentLoaded", () => {
    // 1. Load Supabase Credentials if stored
    loadConfig();
    
    // 2. Set UI Event Listeners
    initTabs();
    initModals();
    initSimulator();
    initChat();
    
    // 3. Render Dashboard Data & Charts
    updateUI();
    
    // 4. Update Current Date Display
    updateDateDisplay();
});

// --- Supabase Config ---
function loadConfig() {
    const savedUrl = localStorage.getItem("supabase_url");
    const savedKey = localStorage.getItem("supabase_key");
    
    const statusDot = document.getElementById("db-status");
    
    if (savedUrl && savedKey) {
        try {
            if (window.supabase) {
                supabaseClient = window.supabase.createClient(savedUrl, savedKey);
                useMockData = false;
                statusDot.className = "db-status-badge online";
                statusDot.querySelector(".status-text").textContent = "Conectado a Supabase";
                
                document.getElementById("cfg-supabase-url").value = savedUrl;
                document.getElementById("cfg-supabase-key").value = savedKey;
                
                syncFromSupabase();
            } else {
                throw new Error("Supabase CDN not loaded yet");
            }
        } catch (e) {
            console.error("Error connecting to Supabase: ", e);
            useMockData = true;
            statusDot.className = "db-status-badge offline";
            statusDot.querySelector(".status-text").textContent = "Error de Conexión (Mock)";
        }
    } else {
        useMockData = true;
        statusDot.className = "db-status-badge offline";
        statusDot.querySelector(".status-text").textContent = "Datos Locales (Mock)";
    }
}

async function syncFromSupabase() {
    if (useMockData || !supabaseClient) return;
    
    try {
        let { data: obras } = await supabaseClient.from('fenix_obras').select('*');
        let { data: equipos } = await supabaseClient.from('fenix_equipos').select('*');
        let { data: pegaso } = await supabaseClient.from('fenix_bitacora_pegaso').select('*');
        let { data: marimba } = await supabaseClient.from('fenix_bitacora_marimba').select('*');
        let { data: obra } = await supabaseClient.from('fenix_bitacora_obra').select('*');
        let { data: estimates } = await supabaseClient.from('fenix_estimados_semanales').select('*');
        let { data: whatsapp } = await supabaseClient.from('fenix_whatsapp_inbox').select('*');
        
        if (obras) mockDb.obras = obras;
        if (equipos) mockDb.equipos = equipos;
        if (pegaso) mockDb.pegaso = pegaso;
        if (marimba) mockDb.marimba = marimba;
        if (obra) mockDb.obra = obra;
        if (estimates) mockDb.estimates = estimates;
        if (whatsapp) mockDb.whatsapp = whatsapp;
        
        updateUI();
    } catch (err) {
        console.error("Error syncing Supabase tables:", err);
    }
}

// --- Tabs Management ---
function initTabs() {
    const navButtons = document.querySelectorAll(".nav-btn");
    const tabContents = document.querySelectorAll(".tab-content");
    const pageTitle = document.getElementById("page-title");
    const pageSubtitle = document.getElementById("page-subtitle");

    navButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const tabId = btn.getAttribute("data-tab");
            
            navButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            tabContents.forEach(content => content.classList.remove("active"));
            document.getElementById(`tab-${tabId}`).classList.add("active");
            
            if (tabId === "dashboard") {
                pageTitle.textContent = "Conciliación & KPIs";
                pageSubtitle.textContent = "Monitoreo de flujo de combustible de Grupo Trujano";
            } else if (tabId === "bitacoras") {
                pageTitle.textContent = "Bitácoras Diésel";
                pageSubtitle.textContent = "Hojas de control físico homologadas de Pegaso, Mamba y Obras";
            } else if (tabId === "asistente") {
                pageTitle.textContent = "Asistente IA Seguro";
                pageSubtitle.textContent = "Consulta conversacional parametrizada sobre consumo e inventarios";
            } else if (tabId === "simulador") {
                pageTitle.textContent = "Simulador WhatsApp";
                pageSubtitle.textContent = "Panel de testing para simular el envío de mensajes e imágenes por WhatsApp";
            }
        });
    });

    const subtabBtns = document.querySelectorAll(".subtab-btn");
    const subtabContents = document.querySelectorAll(".subtab-content");

    subtabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const subtabId = btn.getAttribute("data-subtab");
            
            subtabBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            subtabContents.forEach(content => content.classList.remove("active"));
            document.getElementById(`subtab-${subtabId}`).classList.add("active");
        });
    });
}

// --- Modals Management ---
function initModals() {
    const configModal = document.getElementById("config-modal");
    const btnConfig = document.getElementById("btn-config");
    const btnCloseModal = document.getElementById("btn-close-modal");
    const btnSaveConfig = document.getElementById("btn-save-config");
    const btnClearConfig = document.getElementById("btn-clear-config");
    
    const viewerModal = document.getElementById("image-viewer-modal");
    const btnCloseViewer = document.getElementById("btn-close-viewer");

    btnConfig.addEventListener("click", () => configModal.classList.add("active"));
    btnCloseModal.addEventListener("click", () => configModal.classList.remove("active"));
    
    btnSaveConfig.addEventListener("click", () => {
        const url = document.getElementById("cfg-supabase-url").value.trim();
        const key = document.getElementById("cfg-supabase-key").value.trim();
        
        if (url && key) {
            localStorage.setItem("supabase_url", url);
            localStorage.setItem("supabase_key", key);
        } else {
            localStorage.removeItem("supabase_url");
            localStorage.removeItem("supabase_key");
        }
        
        configModal.classList.remove("active");
        loadConfig();
    });

    btnClearConfig.addEventListener("click", () => {
        localStorage.removeItem("supabase_url");
        localStorage.removeItem("supabase_key");
        document.getElementById("cfg-supabase-url").value = "";
        document.getElementById("cfg-supabase-key").value = "";
        configModal.classList.remove("active");
        loadConfig();
    });

    btnCloseViewer.addEventListener("click", () => viewerModal.classList.remove("active"));

    [configModal, viewerModal].forEach(modal => {
        modal.addEventListener("click", (e) => {
            if (e.target === modal) modal.classList.remove("active");
        });
    });
}

function openImageViewer(imgName, title, desc) {
    const viewerModal = document.getElementById("image-viewer-modal");
    const viewerImg = document.getElementById("viewer-img");
    const viewerTitle = document.getElementById("viewer-title");
    const viewerDesc = document.getElementById("viewer-desc");
    
    viewerImg.src = mockImages[imgName] || mockImages["ticket_gasolina.jpg"];
    viewerTitle.textContent = title;
    viewerDesc.textContent = desc || "";
    
    viewerModal.classList.add("active");
}

function updateDateDisplay() {
    const display = document.getElementById("current-date-display");
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    display.textContent = new Date("2026-06-15").toLocaleDateString('es-ES', options);
}

// --- Data Calculations & KPI update ---
function updateUI() {
    calculateKPIs();
    renderTables();
    renderEstimatesTable();
    renderCharts();
}

function calculateKPIs() {
    // 1. Tanque Pegaso level (Entradas - Salidas)
    const pegasoEntradas = mockDb.pegaso.filter(r => r.tipo_movimiento === 'Entrada').reduce((acc, curr) => acc + Number(curr.litros_entrada), 0);
    const pegasoSalidas = mockDb.pegaso.filter(r => r.tipo_movimiento !== 'Entrada').reduce((acc, curr) => acc + Number(curr.litros_salida), 0);
    const pegasoInventario = pegasoEntradas - pegasoSalidas;

    document.getElementById("val-pegaso-inventario").textContent = pegasoInventario.toLocaleString('en-US');
    
    // Pegaso despachado hoy
    const pegasoSalidasHoy = mockDb.pegaso.filter(r => r.fecha === '2026-06-15' && r.tipo_movimiento !== 'Entrada').reduce((acc, curr) => acc + Number(curr.litros_salida), 0);
    document.getElementById("val-pegaso-despachado").textContent = pegasoSalidasHoy;

    // 2. Marimba level (Entradas - Salidas)
    const marimbaEntradas = mockDb.marimba.filter(r => r.tipo_movimiento.startsWith('Entrada')).reduce((acc, curr) => acc + Number(curr.litros_entrada), 0);
    const marimbaSalidas = mockDb.marimba.filter(r => r.tipo_movimiento === 'Salida a Obra').reduce((acc, curr) => acc + Number(curr.litros_salida), 0);
    const marimbaInventario = marimbaEntradas - marimbaSalidas;

    document.getElementById("val-marimba-inventario").textContent = marimbaInventario.toLocaleString('en-US');

    // 3. Consumo Obras
    const obrasConsumo = mockDb.obra.reduce((acc, curr) => acc + Number(curr.litros_recibidos), 0);
    const obrasCosto = mockDb.obra.reduce((acc, curr) => acc + Number(curr.importe), 0);
    
    document.getElementById("val-obras-consumo").textContent = obrasConsumo.toLocaleString('en-US');
    document.getElementById("val-obras-costo").textContent = "$" + obrasCosto.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

    // 4. Conciliation Logic (Discrepancies)
    const pegasoToMarimba = mockDb.pegaso.filter(r => r.tipo_movimiento === 'Salida a Marimba').reduce((acc, curr) => acc + Number(curr.litros_salida), 0);
    const marimbaFromPegaso = mockDb.marimba.filter(r => r.tipo_movimiento === 'Entrada desde Pegaso').reduce((acc, curr) => acc + Number(curr.litros_entrada), 0);
    const diffPegasoMarimba = Math.abs(pegasoToMarimba - marimbaFromPegaso);

    const marimbaToObra = mockDb.marimba.filter(r => r.tipo_movimiento === 'Salida a Obra').reduce((acc, curr) => acc + Number(curr.litros_salida), 0);
    const obraFromMarimba = mockDb.obra.filter(r => r.fuente === 'Marimba M-01').reduce((acc, curr) => acc + Number(curr.litros_recibidos), 0);
    const diffMarimbaObra = Math.abs(marimbaToObra - obraFromMarimba);

    const pegasoToObraDirect = mockDb.pegaso.filter(r => r.tipo_movimiento === 'Salida Directa Máquina').reduce((acc, curr) => acc + Number(curr.litros_salida), 0);
    const obraFromPegasoDirect = mockDb.obra.filter(r => r.fuente === 'Pegaso Directo').reduce((acc, curr) => acc + Number(curr.litros_recibidos), 0);
    const diffPegasoObra = Math.abs(pegasoToObraDirect - obraFromPegasoDirect);

    const diffTotal = diffPegasoMarimba + diffMarimbaObra + diffPegasoObra;
    
    const diffElement = document.getElementById("val-diff-total");
    const diffDesc = document.getElementById("val-diff-desc");
    const alertWrapper = document.getElementById("alert-icon-wrapper");
    const alertsList = document.getElementById("alerts-list");

    diffElement.textContent = diffTotal + " L";

    alertsList.innerHTML = "";

    if (diffTotal === 0) {
        diffDesc.textContent = "Flujo de combustible verificado";
        alertWrapper.className = "kpi-icon icon-emerald";
        
        alertsList.innerHTML = `
            <div class="alert-item success">
                <i class="fa-solid fa-circle-check"></i>
                <span><strong>Conciliación Perfecta:</strong> Todo el flujo de diésel cuadra. Las transferencias entre Pegaso y Mamba están completas, y las obras han reconocido todos los despachos.</span>
            </div>
        `;
    } else {
        diffDesc.textContent = "Discrepancia detectada en conciliación";
        alertWrapper.className = "kpi-icon icon-rose";

        if (diffPegasoMarimba > 0) {
            alertsList.innerHTML += `
                <div class="alert-item danger">
                    <i class="fa-solid fa-triangle-exclamation"></i>
                    <span><strong>Discrepancia Pegaso ➡️ Mamba:</strong> Hay una diferencia de <strong>${diffPegasoMarimba} L</strong>. Pegaso registra salidas a Mamba por ${pegasoToMarimba} L, pero la Mamba solo reporta haber recibido ${marimbaFromPegaso} L.</span>
                </div>
            `;
        }
        if (diffMarimbaObra > 0) {
            alertsList.innerHTML += `
                <div class="alert-item warning">
                    <i class="fa-solid fa-circle-exclamation"></i>
                    <span><strong>Discrepancia Mamba ➡️ Obra:</strong> Hay una diferencia de <strong>${diffMarimbaObra} L</strong>. Mamba reporta entregas en obra por ${marimbaToObra} L, pero las bitácoras de obra solo reconocen ${obraFromMarimba} L.</span>
                </div>
            `;
        }
        if (diffPegasoObra > 0) {
            alertsList.innerHTML += `
                <div class="alert-item warning">
                    <i class="fa-solid fa-circle-exclamation"></i>
                    <span><strong>Discrepancia Pegaso Directo ➡️ Obra:</strong> Hay una diferencia de <strong>${diffPegasoObra} L</strong>. Pegaso despachó directo ${pegasoToObraDirect} L, pero en obra se registraron ${obraFromPegasoDirect} L.</span>
                </div>
            `;
        }
    }

    // Extra metrics
    const marimbaEntradaGasolinera = mockDb.marimba.filter(r => r.tipo_movimiento === 'Entrada desde Gasolinera').reduce((acc, curr) => acc + Number(curr.litros_entrada), 0);
    document.getElementById("stat-total-cargas").textContent = (pegasoEntradas + marimbaEntradaGasolinera).toLocaleString() + " Litros";
    
    const totalCompradoImporte = mockDb.pegaso.filter(r => r.tipo_movimiento === 'Entrada').reduce((acc, curr) => acc + Number(curr.importe), 0) +
                                 mockDb.marimba.filter(r => r.tipo_movimiento === 'Entrada desde Gasolinera').reduce((acc, curr) => acc + Number(curr.importe), 0);
    
    document.getElementById("stat-total-costo").textContent = "$" + totalCompradoImporte.toLocaleString('en-US', {minimumFractionDigits:2, maximumFractionDigits:2}) + " MXN";
}

// --- Render Data Tables ---
function renderTables() {
    // 1. Render Pegaso Table
    const tbodyPegaso = document.querySelector("#table-pegaso tbody");
    tbodyPegaso.innerHTML = "";
    mockDb.pegaso.forEach(row => {
        const obraName = mockDb.obras.find(o => o.id === row.obra_id)?.nombre || "-";
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${row.fecha}</td>
            <td><span class="row-badge ${row.tipo_movimiento === 'Entrada' ? 'badge-emerald' : row.tipo_movimiento === 'Salida a Marimba' ? 'badge-violet' : 'badge-cyan'}">${row.tipo_movimiento}</span></td>
            <td>${row.origen_destino}</td>
            <td>${obraName}</td>
            <td>${row.litros_entrada > 0 ? row.litros_entrada : "-"}</td>
            <td>${row.litros_salida > 0 ? row.litros_salida : "-"}</td>
            <td>$${Number(row.costo_por_litro).toFixed(2)}</td>
            <td>$${Number(row.importe).toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
            <td class="photo-cell" onclick="openImageViewer('${row.image_url}', 'Pegaso - ${row.tipo_movimiento}', '${row.observaciones}')">${row.image_url ? '<i class="fa-regular fa-image"></i> Ver Foto' : 'Solo Texto'}</td>
            <td>
                <button class="btn-icon" onclick="editRecord('pegaso', '${row.id}')"><i class="fa-solid fa-pen-to-square"></i></button>
                <button class="btn-icon delete" onclick="deleteRecord('pegaso', '${row.id}')"><i class="fa-solid fa-trash"></i></button>
            </td>
        `;
        tbodyPegaso.appendChild(tr);
    });

    // 2. Render Marimba Table
    const tbodyMarimba = document.querySelector("#table-marimba tbody");
    tbodyMarimba.innerHTML = "";
    mockDb.marimba.forEach(row => {
        const obraName = mockDb.obras.find(o => o.id === row.origen_obra_id)?.nombre || "-";
        const equipoCode = mockDb.equipos.find(e => e.id === row.equipo_id)?.codigo_economico || "-";
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${row.fecha}</td>
            <td><span class="row-badge ${row.tipo_movimiento.startsWith('Entrada') ? 'badge-emerald' : row.tipo_movimiento === 'Salida a Obra' ? 'badge-rose' : 'badge-cyan'}">${row.tipo_movimiento}</span></td>
            <td>${obraName}</td>
            <td>${equipoCode}</td>
            <td>${row.litros_entrada > 0 ? row.litros_entrada : "-"}</td>
            <td>${row.litros_salida > 0 ? row.litros_salida : "-"}</td>
            <td>$${Number(row.costo_por_litro).toFixed(2)}</td>
            <td>$${Number(row.importe).toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
            <td class="photo-cell" onclick="openImageViewer('${row.image_url}', 'Mamba - ${row.tipo_movimiento}', '${row.observaciones}')">${row.image_url ? '<i class="fa-regular fa-image"></i> Ver Foto' : 'Solo Texto'}</td>
            <td>
                <button class="btn-icon" onclick="editRecord('marimba', '${row.id}')"><i class="fa-solid fa-pen-to-square"></i></button>
                <button class="btn-icon delete" onclick="deleteRecord('marimba', '${row.id}')"><i class="fa-solid fa-trash"></i></button>
            </td>
        `;
        tbodyMarimba.appendChild(tr);
    });

    // 3. Render Obra Table
    const tbodyObra = document.querySelector("#table-obra tbody");
    tbodyObra.innerHTML = "";
    mockDb.obra.forEach(row => {
        const obraName = mockDb.obras.find(o => o.id === row.obra_id)?.nombre || "-";
        const equipo = mockDb.equipos.find(e => e.id === row.equipo_id);
        const equipoCode = equipo?.codigo_economico || "-";
        const equipoTipo = equipo?.tipo_equipo || "-";
        
        let rendimientoStr = "-";
        if (equipo) {
            if (equipo.tipo_rendimiento === 'horas' && row.horas_trabajadas) {
                const rend = (row.litros_recibidos / row.horas_trabajadas).toFixed(1);
                rendimientoStr = `${rend} L/h`;
            } else if (equipo.tipo_rendimiento === 'kilometros' && row.kilometraje) {
                const rend = (row.kilometraje / row.litros_recibidos).toFixed(1);
                rendimientoStr = `${rend} km/L`;
            }
        }

        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${row.fecha}</td>
            <td>${obraName}</td>
            <td><span class="row-badge ${row.fuente === 'Pegaso Directo' ? 'badge-cyan' : 'badge-violet'}">${row.fuente}</span></td>
            <td><strong>${equipoCode}</strong> (${equipoTipo})</td>
            <td>${row.litros_recibidos} L</td>
            <td>$${Number(row.costo_por_litro).toFixed(2)}</td>
            <td>$${Number(row.importe).toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
            <td><span class="row-badge badge-amber">${rendimientoStr}</span></td>
            <td><em>${row.actividad_ejecutada || ""}</em>. ${row.observaciones || ""}</td>
            <td class="photo-cell" onclick="openImageViewer('${row.image_url}', 'Obra - Suministro', '${row.observaciones}')">${row.image_url ? '<i class="fa-regular fa-image"></i> Ver Foto' : 'Solo Texto'}</td>
            <td>
                <button class="btn-icon" onclick="editRecord('obra', '${row.id}')"><i class="fa-solid fa-pen-to-square"></i></button>
                <button class="btn-icon delete" onclick="deleteRecord('obra', '${row.id}')"><i class="fa-solid fa-trash"></i></button>
            </td>
        `;
        tbodyObra.appendChild(tr);
    });
}

// --- Render Estimates vs Actual Table ---
function renderEstimatesTable() {
    const tbody = document.querySelector("#table-estimates-comparison tbody");
    if (!tbody) return;
    tbody.innerHTML = "";

    let topMaquinaCode = "-";
    let maxConsumo = 0;

    mockDb.estimates.forEach(est => {
        const obra = mockDb.obras.find(o => o.id === est.obra_id);
        const equipo = mockDb.equipos.find(e => e.id === est.equipo_id);
        
        if (!obra || !equipo) return;

        // Sum actual consumption for this machine in this work site
        const actualLiters = mockDb.obra
            .filter(r => r.obra_id === est.obra_id && r.equipo_id === est.equipo_id)
            .reduce((acc, curr) => acc + Number(curr.litros_recibidos), 0);

        if (actualLiters > maxConsumo) {
            maxConsumo = actualLiters;
            topMaquinaCode = `${equipo.codigo_economico} (${obra.nombre})`;
        }

        const deviation = actualLiters - est.litros_estimados;
        let pctDeviation = 0;
        if (est.litros_estimados > 0) {
            pctDeviation = Math.round((actualLiters / est.litros_estimados) * 100);
        }

        let statusClass = "badge-cyan";
        let statusText = "Falta Reportar";

        if (actualLiters > 0) {
            if (deviation > 10) {
                statusClass = "badge-rose";
                statusText = "Sobreconsumo";
            } else if (deviation < -10) {
                statusClass = "badge-violet";
                statusText = "Incompleto";
            } else {
                statusClass = "badge-emerald";
                statusText = "Dentro de Rango";
            }
        }

        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td><strong>${obra.nombre}</strong></td>
            <td>${equipo.codigo_economico} (${equipo.tipo_equipo})</td>
            <td>${est.litros_estimados} L</td>
            <td>${actualLiters > 0 ? actualLiters + ' L' : '-'}</td>
            <td><span class="${deviation > 10 ? 'text-danger' : deviation < -10 ? 'text-info' : ''}">${deviation > 0 ? '+' + deviation : deviation} L</span></td>
            <td>${actualLiters > 0 ? pctDeviation + '%' : '-'}</td>
            <td><span class="row-badge ${statusClass}">${statusText}</span></td>
        `;
        tbody.appendChild(tr);
    });

    if (maxConsumo > 0) {
        document.getElementById("stat-top-maquina").textContent = `${topMaquinaCode} (${maxConsumo} L)`;
    } else {
        document.getElementById("stat-top-maquina").textContent = "-";
    }
}

// --- CRUD Actions ---
window.deleteRecord = async (table, id) => {
    if (!confirm("¿Estás seguro de eliminar este registro?")) return;
    
    if (useMockData) {
        mockDb[table] = mockDb[table].filter(r => r.id !== id);
        updateUI();
    } else {
        try {
            const dbTable = table === 'pegaso' ? 'fenix_bitacora_pegaso' : table === 'marimba' ? 'fenix_bitacora_marimba' : 'fenix_bitacora_obra';
            await supabaseClient.from(dbTable).delete().eq('id', id);
            syncFromSupabase();
        } catch (e) {
            alert("Error al borrar registro en Supabase.");
        }
    }
};

window.editRecord = (table, id) => {
    const record = mockDb[table].find(r => r.id === id);
    if (!record) return;
    
    const newLiters = prompt("Introduce los nuevos litros:", record.litros_entrada || record.litros_salida || record.litros_recibidos);
    if (newLiters === null) return;
    
    const parsedLiters = Number(newLiters);
    if (isNaN(parsedLiters)) {
        alert("Liters debe ser un número.");
        return;
    }

    if (useMockData) {
        if (table === 'pegaso') {
            if (record.tipo_movimiento === 'Entrada') record.litros_entrada = parsedLiters;
            else record.litros_salida = parsedLiters;
        } else if (table === 'marimba') {
            if (record.tipo_movimiento.startsWith('Entrada')) record.litros_entrada = parsedLiters;
            else record.litros_salida = parsedLiters;
        } else {
            record.litros_recibidos = parsedLiters;
        }
        updateUI();
    } else {
        saveEditSupabase(table, id, parsedLiters);
    }
};

async function saveEditSupabase(table, id, liters) {
    try {
        let updateData = {};
        if (table === 'pegaso') {
            const record = mockDb.pegaso.find(r => r.id === id);
            if (record.tipo_movimiento === 'Entrada') updateData.litros_entrada = liters;
            else updateData.litros_salida = liters;
        } else if (table === 'marimba') {
            const record = mockDb.marimba.find(r => r.id === id);
            if (record.tipo_movimiento.startsWith('Entrada')) updateData.litros_entrada = liters;
            else updateData.litros_salida = liters;
        } else {
            updateData.litros_recibidos = liters;
        }
        
        const dbTable = table === 'pegaso' ? 'fenix_bitacora_pegaso' : table === 'marimba' ? 'fenix_bitacora_marimba' : 'fenix_bitacora_obra';
        await supabaseClient.from(dbTable).update(updateData).eq('id', id);
        syncFromSupabase();
    } catch (e) {
        alert("Error al guardar edición en Supabase.");
    }
}

// --- Render Charts (Chart.js) ---
function renderCharts() {
    const ctxFlow = document.getElementById("chart-flow-comparison").getContext("2d");
    const ctxPerformance = document.getElementById("chart-performance").getContext("2d");
    const ctxDistribution = document.getElementById("chart-obra-distribution").getContext("2d");
    const ctxPeticiones = document.getElementById("chart-peticiones-dia-obra").getContext("2d");
    const ctxMarimba = document.getElementById("chart-marimba-dia-obra").getContext("2d");
    const ctxPegaso = document.getElementById("chart-pegaso-dia-obra").getContext("2d");

    if (chartFlow) chartFlow.destroy();
    if (chartPerformance) chartPerformance.destroy();
    if (chartDistribution) chartDistribution.destroy();
    if (chartPeticionesDiaObra) chartPeticionesDiaObra.destroy();
    if (chartMarimbaDiaObra) chartMarimbaDiaObra.destroy();
    if (chartPegasoDiaObra) chartPegasoDiaObra.destroy();

    const pegasoSalidasMarimba = mockDb.pegaso.filter(r => r.tipo_movimiento === 'Salida a Marimba').reduce((acc, curr) => acc + Number(curr.litros_salida), 0);
    const marimbaEntradasPegaso = mockDb.marimba.filter(r => r.tipo_movimiento === 'Entrada desde Pegaso').reduce((acc, curr) => acc + Number(curr.litros_entrada), 0);
    
    const marimbaSalidasObra = mockDb.marimba.filter(r => r.tipo_movimiento === 'Salida a Obra').reduce((acc, curr) => acc + Number(curr.litros_salida), 0);
    const obraRecibidoMarimba = mockDb.obra.filter(r => r.fuente === 'Marimba M-01').reduce((acc, curr) => acc + Number(curr.litros_recibidos), 0);

    chartFlow = new Chart(ctxFlow, {
        type: 'bar',
        data: {
            labels: ['Pegaso a Mamba (L)', 'Mamba de Pegaso (L)', 'Mamba a Obras (L)', 'Obras de Mamba (L)'],
            datasets: [{
                label: 'Combustible',
                data: [pegasoSalidasMarimba, marimbaEntradasPegaso, marimbaSalidasObra, obraRecibidoMarimba],
                backgroundColor: [
                    'rgba(260, 80, 65, 0.4)', 
                    'rgba(260, 80, 65, 0.8)', 
                    'rgba(190, 90, 50, 0.4)', 
                    'rgba(190, 90, 50, 0.8)'
                ],
                borderColor: [
                    'hsl(260, 80, 65)', 
                    'hsl(260, 80, 65)', 
                    'hsl(190, 90, 50)', 
                    'hsl(190, 90, 50)'
                ],
                borderWidth: 1.5,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#9ca3af' } },
                x: { grid: { display: false }, ticks: { color: '#9ca3af' } }
            }
        }
    });

    let rendData = {};
    mockDb.obra.forEach(r => {
        const equipo = mockDb.equipos.find(e => e.id === r.equipo_id);
        if (!equipo) return;
        
        if (!rendData[equipo.codigo_economico]) {
            rendData[equipo.codigo_economico] = { liters: 0, hours: 0, kms: 0, type: equipo.tipo_rendimiento };
        }
        
        rendData[equipo.codigo_economico].liters += Number(r.litros_recibidos);
        if (equipo.tipo_rendimiento === 'horas' && r.horas_trabajadas) {
            rendData[equipo.codigo_economico].hours += Number(r.horas_trabajadas);
        } else if (equipo.tipo_rendimiento === 'kilometros' && r.kilometraje) {
            rendData[equipo.codigo_economico].kms += Number(r.kilometraje);
        }
    });

    let labels = [];
    let datasetsData = [];
    Object.keys(rendData).forEach(key => {
        const item = rendData[key];
        labels.push(key);
        if (item.type === 'horas' && item.hours > 0) {
            datasetsData.push((item.liters / item.hours).toFixed(1));
        } else if (item.type === 'kilometros' && item.liters > 0) {
            datasetsData.push((item.kms / item.liters).toFixed(1));
        } else {
            datasetsData.push(0);
        }
    });

    chartPerformance = new Chart(ctxPerformance, {
        type: 'bar',
        data: {
            labels: labels.length > 0 ? labels : ['PER-200', 'VOG-03', 'HAMM', 'DINA'],
            datasets: [{
                label: 'Rendimiento Promedio',
                data: datasetsData.length > 0 ? datasetsData : [41.7, 22.2, 0, 0],
                backgroundColor: 'rgba(56, 189, 248, 0.4)',
                borderColor: 'hsl(190, 90, 50)',
                borderWidth: 1.5,
                borderRadius: 4
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#9ca3af' } },
                y: { grid: { display: false }, ticks: { color: '#9ca3af' } }
            }
        }
    });

    let obraLabels = [];
    let obraData = [];
    mockDb.obras.forEach(o => {
        obraLabels.push(o.nombre);
        const lts = mockDb.obra.filter(r => r.obra_id === o.id).reduce((acc, curr) => acc + Number(curr.litros_recibidos), 0);
        obraData.push(lts);
    });

    chartDistribution = new Chart(ctxDistribution, {
        type: 'doughnut',
        data: {
            labels: obraLabels,
            datasets: [{
                data: obraData,
                backgroundColor: [
                    'rgba(56, 189, 248, 0.7)',
                    'rgba(167, 139, 250, 0.7)',
                    'rgba(16, 185, 129, 0.7)',
                    'rgba(251, 191, 36, 0.7)'
                ],
                borderColor: [
                    'hsl(190, 90, 50)',
                    'hsl(260, 80, 65)',
                    'hsl(150, 75, 45)',
                    'hsl(38, 90, 55)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: { color: '#9ca3af', font: { family: 'Inter' } }
                }
            }
        }
    });

    // --- New Charts Logic ---
    // 1. Peticiones (Estimados) por Obra
    let peticionesLabels = mockDb.obras.map(o => o.codigo);
    let peticionesData = mockDb.obras.map(o => {
        return mockDb.estimates.filter(e => e.obra_id === o.id).reduce((acc, curr) => acc + Number(curr.litros_estimados), 0);
    });

    chartPeticionesDiaObra = new Chart(ctxPeticiones, {
        type: 'bar',
        data: {
            labels: peticionesLabels,
            datasets: [{
                label: 'Litros Solicitados',
                data: peticionesData,
                backgroundColor: 'rgba(56, 189, 248, 0.6)',
                borderColor: 'hsl(190, 90, 50)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: { y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#9ca3af' } }, x: { grid: { display: false }, ticks: { color: '#9ca3af' } } }
        }
    });

    // 2. Salidas Marimba por Día y Obra
    let marimbaData = mockDb.obras.map(o => {
        return mockDb.marimba.filter(m => m.origen_obra_id === o.id && m.tipo_movimiento === 'Salida a Obra').reduce((acc, curr) => acc + Number(curr.litros_salida), 0);
    });

    chartMarimbaDiaObra = new Chart(ctxMarimba, {
        type: 'bar',
        data: {
            labels: peticionesLabels,
            datasets: [{
                label: 'Litros Surtidos (Marimba)',
                data: marimbaData,
                backgroundColor: 'rgba(167, 139, 250, 0.6)',
                borderColor: 'hsl(260, 80, 65)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: { y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#9ca3af' } }, x: { grid: { display: false }, ticks: { color: '#9ca3af' } } }
        }
    });

    // 3. Salidas Pegaso por Día y Obra
    let pegasoData = mockDb.obras.map(o => {
        return mockDb.pegaso.filter(p => p.obra_id === o.id && (p.tipo_movimiento === 'Salida a Marimba' || p.tipo_movimiento === 'Salida Directa Máquina')).reduce((acc, curr) => acc + Number(curr.litros_salida), 0);
    });

    chartPegasoDiaObra = new Chart(ctxPegaso, {
        type: 'bar',
        data: {
            labels: peticionesLabels,
            datasets: [{
                label: 'Litros Surtidos (Pegaso)',
                data: pegasoData,
                backgroundColor: 'rgba(16, 185, 129, 0.6)',
                borderColor: 'hsl(150, 75, 45)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: { y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#9ca3af' } }, x: { grid: { display: false }, ticks: { color: '#9ca3af' } } }
        }
    });

}

// --- WhatsApp Simulator Engine ---
function initSimulator() {
    const sender = document.getElementById("sim-sender");
    const message = document.getElementById("sim-message");
    const imgSelect = document.getElementById("sim-image-select");
    const btnSend = document.getElementById("btn-simulate-send");
    
    // Quick templates definitions
    const templates = {
        "tmpl-pegaso-in": "Entrada Pegaso de Gasolinera Huixquilucan: 100 litros a $27.20. Folio ticket 4829",
        "tmpl-pegaso-out": "Salida Pegaso a Marimba M-01 para México-Toluca: 50 litros. Chofer Carlos.",
        "tmpl-mamba-in-gas": "Entrada Marimba M-01 de Gasolinera Huixquilucan: 800 litros a $27.40",
        "tmpl-mamba-out": "Salida Marimba M-01 a Obra México-Toluca para Perfiladora PER-200: 250 litros.",
        "tmpl-obra-rec": "Recepción Obra México-Toluca desde Marimba M-01 para Perfiladora PER-200: 250 litros. Costo $27.20. 6 horas trabajadas.",
        "tmpl-engineer-estimate": "Solicitud de combustible para su revisión y vobo.\n*Lunes 15 de junio 2026*\nObra México-Toluca\n1) Perfiladora wirgent f-200: 250 lts\n2) Vogele-03 (Op Gerardo): 100 lts equipo, 20 lts limpieza\n3) Tándem Hamm: 50 lts\n4) Neumatico Dinapac: 50 lts\n5) Barredora Broce Broom: 40 lts\n6) Retroexcavadora (Op Adolfo): 60 lts\n7) Petrolizadora (Op Elthon): 50 lts\n8) Camión impacto: 30 lts\nTOTAL COMBUSTIBLE: 650 lts",
        "tmpl-ocr-compactador": "Suministro Compactador CP-01 desde Mamba",
        "tmpl-ocr-perfiladora": "Abastecimiento de combustible para Perfiladora"
    };

    const templateSenders = {
        "tmpl-pegaso-in": "operador_pegaso",
        "tmpl-pegaso-out": "operador_pegaso",
        "tmpl-mamba-in-gas": "chofer_mamba",
        "tmpl-mamba-out": "chofer_mamba",
        "tmpl-obra-rec": "ingeniero_obra",
        "tmpl-engineer-estimate": "ingeniero_obra",
        "tmpl-ocr-compactador": "chofer_mamba",
        "tmpl-ocr-perfiladora": "chofer_mamba"
    };

    const templateImages = {
        "tmpl-ocr-compactador": "medidor_pegaso.jpg", // Contains counter "0040"
        "tmpl-ocr-perfiladora": "medidor_pegaso.jpg" // Contains counter "0250"
    };

    Object.keys(templates).forEach(key => {
        document.getElementById(key).addEventListener("click", () => {
            message.value = templates[key];
            sender.value = templateSenders[key];
            if (templateImages[key]) {
                imgSelect.value = templateImages[key];
            } else {
                imgSelect.value = "";
            }
        });
    });

    btnSend.addEventListener("click", async () => {
        const text = message.value.trim();
        const fromRole = sender.value;
        const imgName = imgSelect.value;
        
        if (!text) {
            alert("El mensaje no puede estar vacío.");
            return;
        }

        // Add log entry: Incoming Webhook
        addLogEntry("incoming", `WEBHOOK RECIBIDO desde WhatsApp. Remitente: ${fromRole.toUpperCase()}`);
        addLogEntry("system", `Procesando texto: "${text}"`);
        
        // Simulating Gemini Prompt analysis
        setTimeout(async () => {
            addLogEntry("info", "Invocando modelo Gemini 1.5 Flash para análisis semántico...");
            
            let category = "desconocido";
            let data = {};
            
            const lowerText = text.toLowerCase();
            
            // MOCK OCR READS FROM MEDIDOR FOTO
            let litrosFromOcr = null;
            if (imgName === 'medidor_pegaso.jpg') {
                addLogEntry("info", "[n8n OCR Node] Analizando foto del flujómetro analógico...");
                if (lowerText.includes("compactador") || lowerText.includes("cp-01")) {
                    litrosFromOcr = 40;
                    addLogEntry("success", `[OCR] Lectura visual del contador analógico: 0040 ➡️ 40 Litros extraídos.`);
                } else if (lowerText.includes("perfiladora") || lowerText.includes("per-200")) {
                    litrosFromOcr = 250;
                    addLogEntry("success", `[OCR] Lectura visual del contador analógico: 0250 ➡️ 250 Litros extraídos.`);
                } else {
                    litrosFromOcr = 100;
                    addLogEntry("warning", `[OCR] No se especificó máquina. Lectura genérica: 100 Litros.`);
                }
            }

            // Classification rules
            if (lowerText.includes("solicitud de combustible") || lowerText.includes("estimado semanal")) {
                category = "estimado_semanal";
                addLogEntry("info", "[n8n Parser] Detectada solicitud de estimados semanales. Extrayendo lote...");
                
                // Mock array extraction
                const lines = text.split("\n");
                let parsedCount = 0;
                
                lines.forEach(line => {
                    let equipCode = null;
                    let lts = extractNumber(line, /:\s*([0-9]+)\s*(?:lts|litros|l)/i);
                    
                    if (lts !== null) {
                        if (line.toLowerCase().includes("perfiladora")) equipCode = "PER-200";
                        else if (line.toLowerCase().includes("vogele")) equipCode = "VOG-03";
                        else if (line.toLowerCase().includes("tandem") || line.toLowerCase().includes("hamm")) equipCode = "HAMM";
                        else if (line.toLowerCase().includes("neumatico") || line.toLowerCase().includes("dinapac")) equipCode = "DINA";
                        else if (line.toLowerCase().includes("barredora") || line.toLowerCase().includes("broce")) equipCode = "BAR-01";
                        else if (line.toLowerCase().includes("retroexcavadora")) equipCode = "RET-02";
                        else if (line.toLowerCase().includes("petrolizadora")) equipCode = "PET-02";
                        else if (line.toLowerCase().includes("camion") || line.toLowerCase().includes("impacto")) equipCode = "CAM-02";
                        
                        if (equipCode) {
                            parsedCount++;
                            const eqObj = mockDb.equipos.find(e => e.codigo_economico === equipCode);
                            const obObj = mockDb.obras.find(o => o.codigo === "MT"); // Default MT for this screenshot
                            
                            // Save estimate
                            if (useMockData) {
                                // check if already exists to update or insert
                                const idx = mockDb.estimates.findIndex(est => est.semana_fecha === "2026-06-15" && est.obra_id === obObj.id && est.equipo_id === eqObj.id);
                                if (idx >= 0) mockDb.estimates[idx].litros_estimados = lts;
                                else mockDb.estimates.push({ id: "est_sim_" + Math.random(), semana_fecha: "2026-06-15", obra_id: obObj.id, equipo_id: eqObj.id, litros_estimados: lts });
                            }
                        }
                    }
                });
                
                addLogEntry("success", `[n8n Loader] Se insertaron/actualizaron ${parsedCount} estimados semanales en la base de datos.`);
                updateUI();
                message.value = "";
                return;
            }
            
            // Other standard classifications
            if (lowerText.includes("entrada pegaso") || (lowerText.includes("pegaso") && lowerText.includes("entrada"))) {
                category = "pegaso";
                data = {
                    tipo_movimiento: "Entrada",
                    origen_destino: "Gasolinera Huixquilucan",
                    litros: extractNumber(text, /([0-9,]+)\s*(?:litros|l)/i) || 100,
                    costo_por_litro: extractNumber(text, /(?:\$|costo|precio)\s*([0-9.]+)/i) || 27.20,
                    observaciones: "Simulado: Entrada a Pegaso"
                };
            } else if (lowerText.includes("salida pegaso a marimba") || lowerText.includes("salida pegaso a mamba") || lowerText.includes("salida a marimba")) {
                category = "pegaso";
                data = {
                    tipo_movimiento: "Salida a Marimba",
                    origen_destino: "Tanque Pegaso",
                    litros: extractNumber(text, /([0-9,]+)\s*(?:litros|l)/i) || 50,
                    costo_por_litro: 27.20,
                    obra_codigo: "MT",
                    observaciones: "Simulado: Salida a Marimba"
                };
            } else if (lowerText.includes("salida directa") || lowerText.includes("salida directa máquina") || lowerText.includes("compactadora vogele lt directa")) {
                category = "pegaso";
                data = {
                    tipo_movimiento: "Salida Directa Máquina",
                    origen_destino: "Tanque Pegaso",
                    litros: extractNumber(text, /([0-9,]+)\s*(?:litros|l)/i) || litrosFromOcr || 90,
                    costo_por_litro: 27.20,
                    equipo_codigo: lowerText.includes("vogele") ? "VOG-03" : "CP-01",
                    obra_codigo: lowerText.includes("lt") || lowerText.includes("tenango") ? "LT" : "L3M",
                    observaciones: "Simulado: Salida directa Pegaso a máquina"
                };
            } else if (lowerText.includes("entrada marimba desde pegaso") || lowerText.includes("entrada marimba") && lowerText.includes("pegaso")) {
                category = "marimba";
                data = {
                    tipo_movimiento: "Entrada desde Pegaso",
                    litros: extractNumber(text, /([0-9,]+)\s*(?:litros|l)/i) || 50,
                    costo_por_litro: 27.20,
                    obra_codigo: "MT",
                    observaciones: "Simulado: Carga en Mamba de Pegaso"
                };
            } else if (lowerText.includes("entrada marimba de gasolinera") || lowerText.includes("entrada marimba") && lowerText.includes("gasolinera")) {
                category = "marimba";
                data = {
                    tipo_movimiento: "Entrada desde Gasolinera",
                    litros: extractNumber(text, /([0-9,]+)\s*(?:litros|l)/i) || 800,
                    costo_por_litro: extractNumber(text, /(?:\$|costo|precio)\s*([0-9.]+)/i) || 27.40,
                    obra_codigo: "CL",
                    observaciones: "Simulado: Carga en Mamba directa de Gasolinera"
                };
            } else if (lowerText.includes("salida marimba a obra") || lowerText.includes("salida marimba") || lowerText.includes("suministrado en obra") || lowerText.includes("suministro") && fromRole === 'chofer_mamba') {
                category = "marimba";
                data = {
                    tipo_movimiento: "Salida a Obra",
                    litros: extractNumber(text, /([0-9,]+)\s*(?:litros|l)/i) || litrosFromOcr || 300,
                    costo_por_litro: 27.20,
                    equipo_codigo: lowerText.includes("compactador") ? "CP-01" : lowerText.includes("perfiladora") ? "PER-200" : "EX-01",
                    obra_codigo: "MT",
                    observaciones: "Simulado: Despacho Mamba a obra"
                };
            } else if (lowerText.includes("recepción obra") || lowerText.includes("recepcion en obra") || lowerText.includes("recepcion obra") || fromRole === 'ingeniero_obra') {
                category = "obra";
                data = {
                    fuente: lowerText.includes("pegaso") ? "Pegaso Directo" : "Marimba M-01",
                    litros: extractNumber(text, /([0-9,]+)\s*(?:litros|l)/i) || litrosFromOcr || 300,
                    costo_por_litro: extractNumber(text, /(?:\$|costo|precio)\s*([0-9.]+)/i) || 27.20,
                    equipo_codigo: lowerText.includes("compactador") ? "CP-01" : lowerText.includes("perfiladora") ? "PER-200" : "EX-01",
                    obra_codigo: "MT",
                    horas_trabajadas: extractNumber(text, /([0-9.]+)\s*(?:horas|h|hrs)/i) || 8,
                    observaciones: "Simulado: Reporte de ingeniero"
                };
            }

            addLogEntry("info", `Gemini Extrajo JSON: ${JSON.stringify(data, null, 2)}`);
            
            try {
                if (useMockData) {
                    addRecordToMock(category, data, imgName);
                    addLogEntry("success", `Registro exitoso en Base de Datos (MOCK): Guardado en bitácora ${category.toUpperCase()}`);
                } else {
                    addLogEntry("info", `Conectando con Supabase para insertar en fenix_bitacora_${category}...`);
                    await addRecordToSupabase(category, data, imgName);
                    addLogEntry("success", `Registro exitoso en Base de Datos SUPABASE.`);
                    syncFromSupabase();
                }
            } catch (err) {
                addLogEntry("error", `Error al guardar en BD: ${err.message}`);
            }

            message.value = "";
        }, 1200);
    });
}

// Secure Tool-Calling Responses mock engine (returns secure parameterized HTML/Markdown table outputs)
function getAIResponse(query) {
    const q = query.toLowerCase();
    
    if (q.includes("rendimiento") || q.includes("máquinas") || q.includes("maquinas")) {
        let rowsHtml = "";
        mockDb.equipos.forEach(e => {
            let litros = 0, horas = 0, kms = 0;
            mockDb.obra.filter(r => r.equipo_id === e.id).forEach(r => {
                litros += Number(r.litros_recibidos);
                if (e.tipo_rendimiento === 'horas' && r.horas_trabajadas) horas += Number(r.horas_trabajadas);
                else if (e.tipo_rendimiento === 'kilometros' && r.kilometraje) kms += Number(r.kilometraje);
            });
            
            let rend = "-";
            if (e.tipo_rendimiento === 'horas' && horas > 0) rend = `<strong>${(litros / horas).toFixed(1)} L/h</strong>`;
            else if (e.tipo_rendimiento === 'kilometros' && litros > 0) rend = `<strong>${(kms / litros).toFixed(1)} km/L</strong>`;
            
            rowsHtml += `
                <tr>
                    <td><strong>${e.codigo_economico}</strong></td>
                    <td>${e.tipo_equipo}</td>
                    <td>${litros} L</td>
                    <td>${horas > 0 ? horas + "h" : kms > 0 ? kms + "km" : "-"}</td>
                    <td>${rend}</td>
                </tr>
            `;
        });
        
        return `
            <p><strong>Fénix IA:</strong> He consultado el módulo de maquinaria y calculado el rendimiento para los equipos de la base de datos.</p>
            <br>
            <table class="chat-embedded-table">
                <thead>
                    <tr>
                        <th>Código</th>
                        <th>Equipo</th>
                        <th>L. Consumidos</th>
                        <th>Operado</th>
                        <th>Rendimiento</th>
                    </tr>
                </thead>
                <tbody>
                    ${rowsHtml}
                </tbody>
            </table>
            <br>
            <p><i class="fa-solid fa-circle-info"></i> El rendimiento eficiente para la Perfiladora <strong>PER-200</strong> está verificado en 41.7 L/h.</p>
        `;
    }
    
    if (q.includes("discrepancia") || q.includes("conciliar") || q.includes("diferencia")) {
        const pegasoSalidasMarimba = mockDb.pegaso.filter(r => r.tipo_movimiento === 'Salida a Marimba').reduce((acc, curr) => acc + Number(curr.litros_salida), 0);
        const marimbaEntradasPegaso = mockDb.marimba.filter(r => r.tipo_movimiento === 'Entrada desde Pegaso').reduce((acc, curr) => acc + Number(curr.litros_entrada), 0);
        const diffPegasoMarimba = pegasoSalidasMarimba - marimbaEntradasPegaso;

        const marimbaSalidasObra = mockDb.marimba.filter(r => r.tipo_movimiento === 'Salida a Obra').reduce((acc, curr) => acc + Number(curr.litros_salida), 0);
        const obraFromMarimba = mockDb.obra.filter(r => r.fuente === 'Marimba M-01').reduce((acc, curr) => acc + Number(curr.litros_recibidos), 0);
        const diffMarimbaObra = marimbaSalidasObra - obraFromMarimba;

        if (diffPegasoMarimba === 0 && diffMarimbaObra === 0) {
            return `<p><strong>Fénix IA:</strong> He auditado la trazabilidad del combustible del día de hoy y **no existen discrepancias** en los flujos. Todo cuadra:</p>
            <ul>
                <li>Pegaso ➡️ Mamba: <strong>${pegasoSalidasMarimba} L</strong> reportados y recibidos.</li>
                <li>Mamba ➡️ Obras: <strong>${marimbaSalidasObra} L</strong> entregados y validados.</li>
            </ul>`;
        } else {
            return `
                <p><strong>Fénix IA:</strong> Se han detectado discrepancias en la conciliación física:</p>
                <ul>
                    ${diffPegasoMarimba !== 0 ? `<li><strong class="text-danger">Pegaso a Mamba:</strong> Hay una discrepancia de <strong>${diffPegasoMarimba} L</strong> (Pegaso registró salida de ${pegasoSalidasMarimba}L y Mamba registró entrada de ${marimbaEntradasPegaso}L).</li>` : ""}
                    ${diffMarimbaObra !== 0 ? `<li><strong class="text-danger">Mamba a Obra:</strong> Hay una diferencia de <strong>${diffMarimbaObra} L</strong> (Mamba reporta entrega de ${marimbaSalidasObra}L y en Obra se registraron ${obraFromMarimba}L).</li>` : ""}
                </ul>
                <p>Te sugiero revisar las bitácoras físicas correspondientes de estas fechas.</p>
            `;
        }
    }

    if (q.includes("desviación") || q.includes("estimado") || q.includes("limite")) {
        let rowsHtml = "";
        mockDb.estimates.forEach(est => {
            const obra = mockDb.obras.find(o => o.id === est.obra_id);
            const equipo = mockDb.equipos.find(e => e.id === est.equipo_id);
            const actual = mockDb.obra.filter(r => r.obra_id === est.obra_id && r.equipo_id === est.equipo_id).reduce((a,c)=>a+Number(c.litros_recibidos), 0);
            const diff = actual - est.litros_estimados;
            
            rowsHtml += `
                <tr>
                    <td><strong>${obra.codigo}</strong></td>
                    <td>${equipo.codigo_economico}</td>
                    <td>${est.litros_estimados} L</td>
                    <td>${actual} L</td>
                    <td class="${diff > 10 ? 'text-danger' : ''}">${diff > 0 ? '+' + diff : diff} L</td>
                </tr>
            `;
        });
        
        return `
            <p><strong>Fénix IA:</strong> Reporte de desviación (Estimado vs. Consumo Real):</p>
            <br>
            <table class="chat-embedded-table">
                <thead>
                    <tr>
                        <th>Obra</th>
                        <th>Equipo</th>
                        <th>Est. Semanal</th>
                        <th>Consumo Real</th>
                        <th>Desviación</th>
                    </tr>
                </thead>
                <tbody>
                    ${rowsHtml}
                </tbody>
            </table>
        `;
    }

    if (q.includes("costo") || q.includes("obra") || q.includes("gasto")) {
        let total = 0;
        let rowsHtml = "";
        
        mockDb.obras.forEach(o => {
            const lts = mockDb.obra.filter(r => r.obra_id === o.id).reduce((acc, curr) => acc + Number(curr.litros_recibidos), 0);
            const costo = mockDb.obra.filter(r => r.obra_id === o.id).reduce((acc, curr) => acc + Number(curr.importe), 0);
            total += costo;
            
            rowsHtml += `
                <tr>
                    <td><strong>${o.nombre}</strong></td>
                    <td>${lts.toLocaleString()} L</td>
                    <td>$${costo.toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
                </tr>
            `;
        });
        
        return `
            <p><strong>Fénix IA:</strong> Este es el desglose de diésel consumido y costo acumulado por obra:</p>
            <br>
            <table class="chat-embedded-table">
                <thead>
                    <tr>
                        <th>Obra</th>
                        <th>Litros Recibidos</th>
                        <th>Importe Total</th>
                    </tr>
                </thead>
                <tbody>
                    ${rowsHtml}
                    <tr style="border-top: 2px solid var(--border-color); font-weight: bold;">
                        <td>TOTAL GENERAL</td>
                        <td>${mockDb.obra.reduce((a,c)=>a+Number(c.litros_recibidos),0).toLocaleString()} L</td>
                        <td>$${total.toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
                    </tr>
                </tbody>
            </table>
        `;
    }

    return `
        <p><strong>Fénix IA:</strong> No reconozco esa consulta directa. Intenta pedirme informes sobre <strong>rendimiento</strong>, <strong>discrepancias</strong> de diésel, la <strong>desviación</strong> de estimados, o la <strong>distribución por obra</strong>.</p>
    `;
}

// --- Helper Functions for WhatsApp Simulator & Chat ---

function addLogEntry(type, messageText) {
    const logsContainer = document.getElementById("simulation-logs");
    if (!logsContainer) return;
    
    const timeStr = new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    const logEntry = document.createElement("div");
    logEntry.className = `log-entry ${type}`;
    logEntry.innerHTML = `
        <span class="log-time">[${timeStr}]</span>
        <span class="log-msg">${messageText}</span>
    `;
    logsContainer.appendChild(logEntry);
    logsContainer.scrollTop = logsContainer.scrollHeight;
}

function extractNumber(text, regex) {
    const match = text.match(regex);
    if (match && match[1]) {
        return Number(match[1].replace(/,/g, ''));
    }
    return null;
}

function addRecordToMock(category, data, imgName) {
    const id = "sim_" + Math.random().toString(36).substr(2, 9);
    const fecha = "2026-06-15";
    const image_url = imgName || null;
    const costo_por_litro = Number(data.costo_por_litro) || 27.20;

    let obraObj = null;
    if (data.obra_codigo) {
        obraObj = mockDb.obras.find(o => o.codigo === data.obra_codigo);
    }
    const obra_id = obraObj ? obraObj.id : null;

    let equipoObj = null;
    if (data.equipo_codigo) {
        equipoObj = mockDb.equipos.find(e => e.codigo_economico === data.equipo_codigo);
    }
    const equipo_id = equipoObj ? equipoObj.id : null;

    if (category === 'pegaso') {
        const litros_entrada = data.tipo_movimiento === 'Entrada' ? Number(data.litros) : 0;
        const litros_salida = data.tipo_movimiento !== 'Entrada' ? Number(data.litros) : 0;
        const record = {
            id,
            fecha,
            tipo_movimiento: data.tipo_movimiento,
            origen_destino: data.origen_destino || (data.tipo_movimiento === 'Entrada' ? 'Gasolinera Huixquilucan' : 'Tanque Pegaso'),
            obra_id,
            equipo_id,
            litros_entrada,
            litros_salida,
            costo_por_litro,
            importe: (litros_entrada || litros_salida) * costo_por_litro,
            observaciones: data.observaciones || "",
            image_url
        };
        mockDb.pegaso.push(record);

        // If Salida Directa Máquina, also insert in fenix_bitacora_obra (Pegaso Directo)
        if (data.tipo_movimiento === 'Salida Directa Máquina') {
            const obraRecord = {
                id: "sim_direct_" + Math.random().toString(36).substr(2, 9),
                fecha,
                obra_id,
                fuente: 'Pegaso Directo',
                equipo_id,
                litros_recibidos: Number(data.litros),
                costo_por_litro,
                importe: Number(data.litros) * costo_por_litro,
                actividad_ejecutada: "Suministro directo",
                incidencia: "Ninguna",
                horas_trabajadas: Number(data.horas_trabajadas) || 8,
                kilometraje: Number(data.kilometraje) || null,
                observaciones: "Entrada directa simulada desde Pegaso",
                image_url
            };
            mockDb.obra.push(obraRecord);
        }
    } else if (category === 'marimba') {
        const litros_entrada = data.tipo_movimiento.startsWith('Entrada') ? Number(data.litros) : 0;
        const litros_salida = data.tipo_movimiento === 'Salida a Obra' ? Number(data.litros) : 0;
        const record = {
            id,
            fecha,
            tipo_movimiento: data.tipo_movimiento,
            origen_obra_id: obra_id,
            equipo_id,
            litros_entrada,
            litros_salida,
            costo_por_litro,
            importe: (litros_entrada || litros_salida) * costo_por_litro,
            observaciones: data.observaciones || "",
            image_url
        };
        mockDb.marimba.push(record);
    } else if (category === 'obra') {
        const record = {
            id,
            fecha,
            obra_id,
            fuente: data.fuente || 'Marimba M-01',
            equipo_id,
            litros_recibidos: Number(data.litros),
            costo_por_litro,
            importe: Number(data.litros) * costo_por_litro,
            actividad_ejecutada: data.actividad_ejecutada || "Suministro normal",
            incidencia: data.incidencia || "Ninguna",
            horas_trabajadas: Number(data.horas_trabajadas) || null,
            kilometraje: Number(data.kilometraje) || null,
            observaciones: data.observaciones || "",
            image_url
        };
        mockDb.obra.push(record);
    }
    updateUI();
}

async function addRecordToSupabase(category, data, imgName) {
    if (!supabaseClient) throw new Error("Cliente Supabase no inicializado");

    const fecha = "2026-06-15";
    const image_url = imgName || null;
    const costo_por_litro = Number(data.costo_por_litro) || 27.20;

    // 1. Get Obra ID
    let obra_id = null;
    if (data.obra_codigo) {
        const { data: oData, error: oErr } = await supabaseClient
            .from('fenix_obras')
            .select('id')
            .eq('codigo', data.obra_codigo)
            .maybeSingle();
        if (oErr) console.error("Error fetching obra:", oErr);
        if (oData) obra_id = oData.id;
    }

    // 2. Get Equipo ID
    let equipo_id = null;
    if (data.equipo_codigo) {
        const { data: eData, error: eErr } = await supabaseClient
            .from('fenix_equipos')
            .select('id')
            .eq('codigo_economico', data.equipo_codigo)
            .maybeSingle();
        if (eErr) console.error("Error fetching equipo:", eErr);
        if (eData) equipo_id = eData.id;
    }

    if (category === 'pegaso') {
        const litros_entrada = data.tipo_movimiento === 'Entrada' ? Number(data.litros) : 0;
        const litros_salida = data.tipo_movimiento !== 'Entrada' ? Number(data.litros) : 0;
        
        const { error } = await supabaseClient
            .from('fenix_bitacora_pegaso')
            .insert({
                fecha,
                tipo_movimiento: data.tipo_movimiento,
                origen_destino: data.origen_destino || (data.tipo_movimiento === 'Entrada' ? 'Gasolinera Huixquilucan' : 'Tanque Pegaso'),
                obra_id,
                equipo_id,
                litros_entrada,
                litros_salida,
                costo_por_litro,
                observaciones: data.observaciones || "",
                image_url
            });
        if (error) throw error;

        // If Salida Directa Máquina, also insert in fenix_bitacora_obra (Pegaso Directo)
        if (data.tipo_movimiento === 'Salida Directa Máquina') {
            const { error: errorDirect } = await supabaseClient
                .from('fenix_bitacora_obra')
                .insert({
                    fecha,
                    obra_id,
                    fuente: 'Pegaso Directo',
                    equipo_id,
                    litros_recibidos: Number(data.litros),
                    costo_por_litro,
                    actividad_ejecutada: "Suministro directo",
                    incidencia: "Ninguna",
                    horas_trabajadas: Number(data.horas_trabajadas) || 8,
                    kilometraje: Number(data.kilometraje) || null,
                    observaciones: "Entrada directa simulada desde Pegaso",
                    image_url
                });
            if (errorDirect) throw errorDirect;
        }
    } else if (category === 'marimba') {
        const litros_entrada = data.tipo_movimiento.startsWith('Entrada') ? Number(data.litros) : 0;
        const litros_salida = data.tipo_movimiento === 'Salida a Obra' ? Number(data.litros) : 0;

        const { error } = await supabaseClient
            .from('fenix_bitacora_marimba')
            .insert({
                fecha,
                tipo_movimiento: data.tipo_movimiento,
                origen_obra_id: obra_id,
                equipo_id,
                litros_entrada,
                litros_salida,
                costo_por_litro,
                observaciones: data.observaciones || "",
                image_url
            });
        if (error) throw error;
    } else if (category === 'obra') {
        const { error } = await supabaseClient
            .from('fenix_bitacora_obra')
            .insert({
                fecha,
                obra_id,
                fuente: data.fuente || 'Marimba M-01',
                equipo_id,
                litros_recibidos: Number(data.litros),
                costo_por_litro,
                actividad_ejecutada: data.actividad_ejecutada || "Suministro normal",
                incidencia: data.incidencia || "Ninguna",
                horas_trabajadas: Number(data.horas_trabajadas) || null,
                kilometraje: Number(data.kilometraje) || null,
                observaciones: data.observaciones || "",
                image_url
            });
        if (error) throw error;
    }
}

function initChat() {
    const chatInput = document.getElementById("chat-input-field");
    const sendBtn = document.getElementById("btn-send-chat");
    const container = document.getElementById("chat-messages-container");
    const suggestionBtns = document.querySelectorAll(".suggest-btn");

    if (!chatInput || !sendBtn || !container) return;

    const sendMessage = () => {
        const text = chatInput.value.trim();
        if (!text) return;

        // User message
        const userMsgDiv = document.createElement("div");
        userMsgDiv.className = "message user";
        userMsgDiv.innerHTML = `
            <div class="bubble">
                <p><strong>Tú:</strong> ${text}</p>
            </div>
        `;
        container.appendChild(userMsgDiv);
        chatInput.value = "";
        container.scrollTop = container.scrollHeight;

        // AI message
        setTimeout(() => {
            const aiResponse = getAIResponse(text);
            const systemMsgDiv = document.createElement("div");
            systemMsgDiv.className = "message system";
            systemMsgDiv.innerHTML = `
                <div class="bubble">
                    ${aiResponse}
                </div>
            `;
            container.appendChild(systemMsgDiv);
            container.scrollTop = container.scrollHeight;
        }, 600);
    };

    sendBtn.addEventListener("click", sendMessage);
    chatInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") sendMessage();
    });

    suggestionBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const query = btn.getAttribute("data-query");
            if (query) {
                chatInput.value = query;
                sendMessage();
            }
        });
    });
}
