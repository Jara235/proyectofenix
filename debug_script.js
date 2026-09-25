
        // Global Helper for TomSelect with Tab & Enter Selection & Focus Advance
        function initTomSelect(target, userOptions = {}) {
            const el = typeof target === 'string' ? document.querySelector(target) : target;
            if (!el) return null;

            const defaultOpts = {
                create: false,
                selectOnTab: true,
                openOnFocus: true,
                sortField: { field: "text", direction: "asc" }
            };

            const opts = Object.assign({}, defaultOpts, userOptions);
            const ts = new TomSelect(el, opts);

            // Handler for Enter & Tab key on TomSelect instance
            ts.on('keydown', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    e.stopPropagation();

                    if (ts.isOpen) {
                        if (ts.activeOption) {
                            ts.setValue(ts.activeOption.dataset.value);
                        } else {
                            const firstOpt = ts.dropdown_content.querySelector('.option:not(.create)');
                            if (firstOpt && firstOpt.dataset.value) {
                                ts.setValue(firstOpt.dataset.value);
                            }
                        }
                        ts.close();
                    }
                    focusNextInput(ts.control_input);
                } else if (e.key === 'Tab') {
                    if (ts.isOpen) {
                        if (ts.activeOption) {
                            ts.setValue(ts.activeOption.dataset.value);
                        } else {
                            const firstOpt = ts.dropdown_content.querySelector('.option:not(.create)');
                            if (firstOpt && firstOpt.dataset.value) {
                                ts.setValue(firstOpt.dataset.value);
                            }
                        }
                    }
                }
            });

            return ts;
        }

        function focusNextInput(currentEl) {
            if (!currentEl) return;
            const form = currentEl.closest('form') || document.body;
            const focusables = Array.from(form.querySelectorAll('input:not([type="hidden"]):not([disabled]), select:not([disabled]), textarea:not([disabled]), button:not([type="button"]):not([disabled]), .ts-control input'));
            
            const visible = focusables.filter(item => {
                return item.offsetWidth > 0 && item.offsetHeight > 0 && window.getComputedStyle(item).visibility !== 'hidden';
            });

            const index = visible.indexOf(currentEl);
            if (index > -1 && index + 1 < visible.length) {
                const next = visible[index + 1];
                next.focus();
                if (typeof next.select === 'function' && next.type !== 'date') {
                    try { next.select(); } catch(err) {}
                }
            }
        }

        // Keydown listener for standard select & input fields on Enter key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                const target = e.target;
                if (!target) return;

                // Ignore textareas and submit buttons
                if (target.tagName === 'TEXTAREA' || (target.tagName === 'BUTTON' && target.type === 'submit')) {
                    return;
                }

                // Standard select element
                if (target.tagName === 'SELECT' && !target.classList.contains('ts-hidden-accessible')) {
                    e.preventDefault();
                    focusNextInput(target);
                }
            }
        });

        function showToast(message, type='success') {
            Toastify({
                text: message,
                duration: 3000,
                close: true,
                gravity: "bottom",
                position: "right",
                style: {
                    background: type === 'success' ? "#10b981" : "#ef4444",
                    borderRadius: "8px",
                    fontFamily: "'Inter', sans-serif"
                }
            }).showToast();
        }

        document.getElementById('btnSyncExcel').addEventListener('click', async function(e) {
            e.preventDefault();
            const btn = document.getElementById('btnSyncExcel');
            const icon = document.getElementById('syncIcon');
            
            if(btn.style.opacity === '0.5') return; // prevent double click
            
            btn.style.opacity = '0.5';
            icon.innerText = '⏳';
            showToast('Sincronizando con Excel... Por favor espera.', 'success');
            
            try {
                const res = await fetch('/api/sync_excel', { method: 'POST' });
                const data = await res.json();
                if(data.success) {
                    showToast(`¡Sincronización exitosa! Importados: ${data.importados}, Exportados: ${data.exportados}`, 'success');
                    setTimeout(() => window.location.reload(), 2000);
                } else {
                    alert('Error de Sincronización: ' + data.error);
                }
            } catch (err) {
                alert('Ocurrió un error al contactar al servidor.');
            } finally {
                btn.style.opacity = '1';
                icon.innerText = '🔄';
            }
        });
    

    const PLACAS_MAP = {"PAT8298": {"id": 41, "empresa": "TRD", "placa": "PAT8298", "vehiculo": "CHEVROLET / EQUIPO MENOR", "obra": "MINA TABERNILLAS", "responsable": "ARMANDO COLIN MORENO", "importe_semanal": 2000.0}, "LHB188D": {"id": 3, "empresa": "J.D.J.", "placa": "LHB188D", "vehiculo": "RAM 1200", "obra": "MAQUINARIA", "responsable": "ING. ANTONIO IBA\u00d1EZ", "importe_semanal": 2500.0}, "NXP9814": {"id": 5, "empresa": "J.D.J.", "placa": "NXP9814", "vehiculo": "DODGE RAM 700", "obra": "MAQUINARIA", "responsable": "ALBERTO HERNANDEZ DE JESUS", "importe_semanal": 1500.0}, "PCW9238": {"id": 6, "empresa": "J.D.J.", "placa": "PCW9238", "vehiculo": "DODGE RAM 700", "obra": "MAQUINARIA", "responsable": "JUAN CARLOS NAZAR CHAVEZ", "importe_semanal": 1500.0}, "LMH893A": {"id": 8, "empresa": "J.D.J.", "placa": "LMH893A", "vehiculo": "CHANGAN ALSVIN", "obra": "H. COLEGIO MILITAR", "responsable": "ROBERTO CARLOS GARC\u00cdA", "importe_semanal": 700.0}, "MAH844C": {"id": 9, "empresa": "J.D.J.", "placa": "MAH844C", "vehiculo": "NISSAN NP-300", "obra": "EXPLANADA DAMIAN CARMONA", "responsable": "OSCAR ESTRADA LINARES", "importe_semanal": 1500.0}, "NYZ829C": {"id": 10, "empresa": "J.D.J.", "placa": "NYZ829C", "vehiculo": "MITSUBISHI L1200", "obra": "BACHEO TOLUCA Y C. VICENTE LOMBARDO", "responsable": "OSCAR ESTRADA LINARES", "importe_semanal": 1500.0}, "LF05470": {"id": 12, "empresa": "J.D.J.", "placa": "LF05470", "vehiculo": "DODGE RAM 4000 (3/2)", "obra": "BACHEO TOLUCA Y C. VICENTE LOMBARDO", "responsable": "TOMAS ARANDA PROSPERO", "importe_semanal": 1500.0}, "MHL758A": {"id": 13, "empresa": "J.D.J.", "placa": "MHL758A", "vehiculo": "MITSUBISHI 1200", "obra": "OBRA M\u00c9XICO TOLUCA", "responsable": "JAVIER PEREZ D\u00cdAZ", "importe_semanal": 2500.0}, "MHL755A": {"id": 15, "empresa": "J.D.J.", "placa": "MHL755A", "vehiculo": "MITSUBISHI", "obra": "OBRA M\u00c9XICO TOLUCA", "responsable": "JAVIER PEREZ D\u00cdAZ", "importe_semanal": 1500.0}, "PBT1230": {"id": 16, "empresa": "J.D.J.", "placa": "PBT1230", "vehiculo": "TOYOTA HIACE (URBAN)", "obra": "OBRA M\u00c9XICO TOLUCA", "responsable": "ALEXIS SAMUEL RENDON DOMINGUEZ", "importe_semanal": 0.0}, "LH49730": {"id": 17, "empresa": "J.D.J.", "placa": "LH49730", "vehiculo": "DODGE RAM 4000 (3/2)", "obra": "OBRA M\u00c9XICO TOLUCA", "responsable": "CRISTIAN REYES GAMORA", "importe_semanal": 4000.0}, "NYZ971C": {"id": 18, "empresa": "J.D.J.", "placa": "NYZ971C", "vehiculo": "MITSUBISHI 1200", "obra": "OBRA M\u00c9XICO TOLUCA", "responsable": "CRISTIAN REYES GAMORA", "importe_semanal": 2500.0}, "NYZ790C": {"id": 22, "empresa": "J.D.J.", "placa": "NYZ790C", "vehiculo": "MITSUBISHI 1200", "obra": "LERMA TENANGO", "responsable": "LEONCIO MARTINEZ PASCACIO", "importe_semanal": 1500.0}, "LH49746": {"id": 23, "empresa": "J.D.J.", "placa": "LH49746", "vehiculo": "DODGE RAM 4000 (3/2)", "obra": "LERMA TENANGO", "responsable": "CARMELO ALVAREZ ANICETO", "importe_semanal": 3000.0}, "PBT1229": {"id": 24, "empresa": "J.D.J.", "placa": "PBT1229", "vehiculo": "TOYOTA HIACE (URBAN)", "obra": "LERMA TENANGO", "responsable": "DIEGO FERNANDEZ SANTIAGO", "importe_semanal": 2500.0}, "PCU7482": {"id": 25, "empresa": "J.D.J.", "placa": "PCU7482", "vehiculo": "FORD RANGER", "obra": "P. ASFALTO HUIXQUILUCAN", "responsable": "DAMIAN ANTONIO PUINI", "importe_semanal": 2500.0}, "LHB184D": {"id": 27, "empresa": "J.D.J.", "placa": "LHB184D", "vehiculo": "RAM 1200", "obra": "TRANSPORTES FLOTILLA", "responsable": "CLEMENTE SANABRIA", "importe_semanal": 2500.0}, "NUZ948C": {"id": 28, "empresa": "J.D.J.", "placa": "NUZ948C", "vehiculo": "CHEVROLET TORNADO", "obra": "TRANSPORTES FLOTILLA", "responsable": "BRYAN GABRIEL CHAVEZ ALVAREZ", "importe_semanal": 1000.0}, "MNX601B": {"id": 31, "empresa": "J.D.J.", "placa": "MNX601B", "vehiculo": "MNX601B", "obra": "TRANSPORTES FLOTILLA", "responsable": "ROBERTO ORTEGA", "importe_semanal": 800.0}, "LHB176D": {"id": 33, "empresa": "J.D.J.", "placa": "LHB176D", "vehiculo": "RAM 1200", "obra": "ESTIMACIONES / PLANTA PEGASO", "responsable": "JOS\u00c9 CABELLO / JACK", "importe_semanal": 1500.0}, "LHB182D": {"id": 34, "empresa": "J.D.J.", "placa": "LHB182D", "vehiculo": "RAM 1200", "obra": "JALISCO", "responsable": "VICTOR HUGO MARTINEZ VELAZQUEZ", "importe_semanal": 1500.0}, "LLY085A": {"id": 35, "empresa": "J.D.J.", "placa": "LLY085A", "vehiculo": "CHANGAN ALSVIN", "obra": "CORPORATIVO", "responsable": "PAOLA JARAMILLO", "importe_semanal": 700.0}, "NZT266B": {"id": 36, "empresa": "J.D.J.", "placa": "NZT266B", "vehiculo": "MITSUBISHI L200", "obra": "CORPORATIVO", "responsable": "SAMUEL ORTEGA SILVA", "importe_semanal": 3000.0}, "LKV206D": {"id": 37, "empresa": "J.D.J.", "placa": "LKV206D", "vehiculo": "RAM 1200", "obra": "CORPORATIVO", "responsable": "CRISTOBAL SILVA", "importe_semanal": 1500.0}, "NXP4918": {"id": 38, "empresa": "J.D.J.", "placa": "NXP4918", "vehiculo": "CHEVROLET S10", "obra": "LICITACIONES", "responsable": "HENRY PINEDA VALLE", "importe_semanal": 800.0}, "33K849": {"id": 39, "empresa": "TRD", "placa": "33K849", "vehiculo": "TOYOTA TACOMA", "obra": "MINA TABERNILLAS", "responsable": "CARLOS REYES TRUJANO", "importe_semanal": 2500.0}, "MHL757A": {"id": 40, "empresa": "TRD", "placa": "MHL757A", "vehiculo": "MITSUBISHI L200", "obra": "MINA TABERNILLAS", "responsable": "LAZARO PINAL RIOS", "importe_semanal": 1500.0}, "NYZ828C": {"id": 42, "empresa": "TRD", "placa": "NYZ828C", "vehiculo": "MITSUBISHI L200", "obra": "MINA ZUMPAHUACAN", "responsable": "ABNER OSORIO BARTOLO", "importe_semanal": 1500.0}, "NYZ839C": {"id": 43, "empresa": "TRD", "placa": "NYZ839C", "vehiculo": "MITSUBISHI L200", "obra": "MINA ZUMPAHUACAN", "responsable": "ISAAC GONZALEZ GONZALEZ", "importe_semanal": 1500.0}, "PCU8771": {"id": 44, "empresa": "TRD", "placa": "PCU8771", "vehiculo": "CHEVROLET", "obra": "MINA CUAJOMAC", "responsable": "JESUS MARIN GARCIA", "importe_semanal": 2000.0}};
    const EQUIPOS_SIN_PLACA = [{"id": 2, "empresa": "J.D.J.", "placa": "S/P", "vehiculo": "EQUIPO MENOR", "obra": "BACHEO TOLUCA", "responsable": "ING. ARMANDO COLIN", "importe_semanal": 500.0}, {"id": 4, "empresa": "J.D.J.", "placa": "S/P", "vehiculo": "EQUIPO MENOR", "obra": "MAQUINARIA", "responsable": "ING. ANTONIO IBA\u00d1EZ", "importe_semanal": 500.0}, {"id": 7, "empresa": "J.D.J.", "placa": "S/P", "vehiculo": "EQUIPO MENOR / VEHICULO", "obra": "MAQUINARIA", "responsable": "EDGAR VELAZQUEZ ESQUIVEL", "importe_semanal": 1500.0}, {"id": 11, "empresa": "J.D.J.", "placa": "S/P", "vehiculo": "EQUIPO MENOR", "obra": "BACHEO TOLUCA", "responsable": "TOMAS ARANDA PROSPERO", "importe_semanal": 500.0}, {"id": 14, "empresa": "J.D.J.", "placa": "S/P", "vehiculo": "EQUIPO MENOR", "obra": "OBRA M\u00c9XICO TOLUCA", "responsable": "JAVIER PEREZ D\u00cdAZ", "importe_semanal": 300.0}, {"id": 19, "empresa": "J.D.J.", "placa": "S/P", "vehiculo": "CORTADORA DE CONCRETO", "obra": "LERMA TENANGO", "responsable": "APOLINAR REYES BOLAINA", "importe_semanal": 1000.0}, {"id": 20, "empresa": "J.D.J.", "placa": "S/P", "vehiculo": "MOTOR AUXILIAR PETROLIZADORA", "obra": "LERMA TENANGO", "responsable": "APOLINAR REYES BOLAINA", "importe_semanal": 0.0}, {"id": 21, "empresa": "J.D.J.", "placa": "S/P", "vehiculo": "MOTOR AUXILIAR PIPA DE AGUA", "obra": "LERMA TENANGO", "responsable": "APOLINAR REYES BOLAINA", "importe_semanal": 0.0}, {"id": 26, "empresa": "J.D.J.", "placa": "S/P", "vehiculo": "EQUIPO MENOR", "obra": "P. ASFALTO HUIXQUILUCAN", "responsable": "LUIS VALDEZ", "importe_semanal": 1000.0}, {"id": 29, "empresa": "J.D.J.", "placa": "S/P", "vehiculo": "MOTORES LOWBOY", "obra": "TRANSPORTES FLOTILLA", "responsable": "BRYAN GABRIEL CHAVEZ ALVAREZ", "importe_semanal": 500.0}, {"id": 30, "empresa": "J.D.J.", "placa": "S/P", "vehiculo": "MOTORES LOWBOY", "obra": "TRANSPORTES FLOTILLA", "responsable": "BRYAN GABRIEL CHAVEZ ALVAREZ", "importe_semanal": 500.0}, {"id": 32, "empresa": "J.D.J.", "placa": "S/P", "vehiculo": "EQUIPO MENOR", "obra": "TRANSPORTES FLOTILLA", "responsable": "ROBERTO ORTEGA", "importe_semanal": 500.0}];

    let currentSelectedMaestroId = null;

    // Initialize Obra, Gasolineria, Placa y FacturaObra selects
    let tomSelectObraObj = initTomSelect("#obraSelect");
    let tomSelectGasolineriaObj = initTomSelect("#gasolineriaSelect", {
        create: true,
        createFilter: input => input.trim().length > 0
    });
    let tomSelectFacturaObra = initTomSelect("#obraFacturaSelect");
    let tomSelectPlacaObj = initTomSelect("#placaSelect", {
        create: true,
        sortField: false,
        createFilter: input => input.trim().length > 0
    });

    let cargasExtraidas = [];
    let facturaUUID = "";
    let facturaFecha = "";
    let facturaFolioFactura = "";
    let facturaProveedor = "";

    function getPlateInfo(val) {
        if (!val) return null;
        const raw = String(val).trim();
        const upper = raw.toUpperCase();

        // 1. Direct match
        if (PLACAS_MAP[upper]) return PLACAS_MAP[upper];
        if (PLACAS_MAP[raw]) return PLACAS_MAP[raw];

        // 2. Extract before '—' or space
        const plateOnly = upper.split('—')[0].split(' ')[0].trim();
        if (PLACAS_MAP[plateOnly]) return PLACAS_MAP[plateOnly];

        // 3. Search key contained in upper or vice versa
        for (const [k, v] of Object.entries(PLACAS_MAP)) {
            const kUpper = k.toUpperCase();
            if (plateOnly && (upper.includes(kUpper) || kUpper.includes(plateOnly))) {
                return v;
            }
        }

        // 4. Check option element data attributes
        const opt = document.querySelector(`#placaSelect option[value="${raw}"]`);
        if (opt && opt.getAttribute('data-vehiculo')) {
            return {
                vehiculo: opt.getAttribute('data-vehiculo') || '',
                obra: opt.getAttribute('data-obra') || '',
                responsable: opt.getAttribute('data-responsable') || ''
            };
        }

        return null;
    }

    async function autocompletarPorPlaca(val) {
        const sinPlacaBox = document.getElementById('sinPlacaBox');
        const eqSelect = document.getElementById('equipoMenorSelect');

        if (!val) {
            if (sinPlacaBox) sinPlacaBox.style.display = 'none';
            document.getElementById('vehiculoInput').value = '';
            document.getElementById('conductorInput').value = '';
            if (typeof tomSelectObraObj !== 'undefined' && tomSelectObraObj) tomSelectObraObj.setValue('');
            document.getElementById('obraSelect').value = '';
            currentSelectedMaestroId = null;
            if (typeof actualizarTopeStatus === 'function') actualizarTopeStatus();
            return;
        }

        const raw = String(val).trim();
        const upper = raw.toUpperCase();
        const plateOnly = upper.split('—')[0].split(' ')[0].trim();

        if (plateOnly === 'S/P' || upper === 'S/P' || upper.startsWith('S/P') || upper === 'SIN PLACA') {
            if (sinPlacaBox) sinPlacaBox.style.display = 'block';
            if (eqSelect) {
                eqSelect.innerHTML = '<option value="">Selecciona Equipo Menor por Obra...</option>';
                if (typeof EQUIPOS_SIN_PLACA !== 'undefined' && Array.isArray(EQUIPOS_SIN_PLACA)) {
                    EQUIPOS_SIN_PLACA.forEach(eq => {
                        const opt = document.createElement('option');
                        opt.value = eq.id;
                        opt.textContent = `[${eq.obra}] ${eq.vehiculo} — ${eq.responsable} ($${parseFloat(eq.importe_semanal || 0).toFixed(2)})`;
                        eqSelect.appendChild(opt);
                    });
                }
            }
            document.getElementById('vehiculoInput').value = '';
            document.getElementById('conductorInput').value = '';
            if (typeof tomSelectObraObj !== 'undefined' && tomSelectObraObj) tomSelectObraObj.setValue('');
            document.getElementById('obraSelect').value = '';
            currentSelectedMaestroId = null;
            if (typeof actualizarTopeStatus === 'function') actualizarTopeStatus();
            return;
        }

        if (sinPlacaBox) sinPlacaBox.style.display = 'none';

        // 1. Client-side Lookup
        let info = getPlateInfo(val);

        if (info) {
            currentSelectedMaestroId = info.id || null;
            if (info.vehiculo) document.getElementById('vehiculoInput').value = info.vehiculo;
            if (info.responsable) document.getElementById('conductorInput').value = info.responsable;
            if (info.obra) {
                document.getElementById('obraSelect').value = info.obra;
                if (typeof tomSelectObraObj !== 'undefined' && tomSelectObraObj) {
                    if (!tomSelectObraObj.options[info.obra]) tomSelectObraObj.addOption({ value: info.obra, text: info.obra });
                    tomSelectObraObj.setValue(info.obra);
                }
            }
        }

        // 2. Server API Fetch (like Diesel module) for guaranteed accuracy
        try {
            const res = await fetch('/api/gasolina/unidad_info?placa=' + encodeURIComponent(plateOnly));
            const data = await res.json();
            if (data.success) {
                if (data.maestro_id) currentSelectedMaestroId = data.maestro_id;
                if (data.vehiculo) document.getElementById('vehiculoInput').value = data.vehiculo;
                if (data.responsable) document.getElementById('conductorInput').value = data.responsable;
                if (data.obra) {
                    document.getElementById('obraSelect').value = data.obra;
                    if (typeof tomSelectObraObj !== 'undefined' && tomSelectObraObj) {
                        if (!tomSelectObraObj.options[data.obra]) tomSelectObraObj.addOption({ value: data.obra, text: data.obra });
                        tomSelectObraObj.setValue(data.obra);
                    }
                }
            }
        } catch(err) {
            console.log('[API fetch error]', err);
        }

        if (typeof actualizarTopeStatus === 'function') actualizarTopeStatus();
    }

    if (tomSelectPlacaObj) {
        tomSelectPlacaObj.clear();
        tomSelectPlacaObj.on('change', autocompletarPorPlaca);
    }
    const rawPlacaEl = document.getElementById('placaSelect');
    if (rawPlacaEl) {
        rawPlacaEl.addEventListener('change', function(e) {
            autocompletarPorPlaca(e.target.value);
        });
    }

    // Listener para Equipo Menor sin placa
    const equipoMenorSel = document.getElementById('equipoMenorSelect');
    if (equipoMenorSel) {
        equipoMenorSel.addEventListener('change', function() {
            const idVal = parseInt(this.value);
            if (!idVal) {
                document.getElementById('vehiculoInput').value = '';
                document.getElementById('conductorInput').value = '';
                if (tomSelectObraObj) tomSelectObraObj.setValue('');
                currentSelectedMaestroId = null;
                actualizarTopeStatus();
                return;
            }
            const eq = EQUIPOS_SIN_PLACA.find(e => e.id === idVal);
            if (eq) {
                currentSelectedMaestroId = eq.id;
                document.getElementById('vehiculoInput').value = eq.vehiculo || '';
                document.getElementById('conductorInput').value = eq.responsable || '';
                if (eq.obra && tomSelectObraObj) {
                    if (!tomSelectObraObj.options[eq.obra]) {
                        tomSelectObraObj.addOption({ value: eq.obra, text: eq.obra });
                    }
                    tomSelectObraObj.setValue(eq.obra);
                }
            }
            actualizarTopeStatus();
        });
    }

    // Listener para Tipo de Gasolina -> Actualiza Costo por Litro
    document.getElementById('tipoGasolinaSelect').addEventListener('change', function() {
        const tipo = this.value;
        const costoInput = document.getElementById('costoInput');
        if (tipo === 'EXTRA') {
            costoInput.value = '23.90';
        } else if (tipo === 'PREMIUM') {
            if (costoInput.value === '23.90' || !costoInput.value) {
                costoInput.value = '25.90';
            }
        }
        calcularImporte();
    });
    document.getElementById('semanaInputGasolina').addEventListener('input', actualizarTopeStatus);
    document.getElementById('fechaInputGasolina').addEventListener('change', function() {
        if(this.value) {
            const parts = this.value.split('-');
            if(parts.length === 3) {
                const d = new Date(Date.UTC(parts[0], parts[1]-1, parts[2]));
                d.setUTCDate(d.getUTCDate() + 4 - (d.getUTCDay()||7));
                const yearStart = new Date(Date.UTC(d.getUTCFullYear(),0,1));
                const weekNo = Math.ceil((((d - yearStart) / 86400000) + 1)/7);
                document.getElementById('semanaInputGasolina').value = weekNo;
                actualizarTopeStatus();
            }
        }
    });

    async function actualizarTopeStatus() {
        const placa = document.getElementById('placaSelect').value;
        const vehiculo = document.getElementById('vehiculoInput').value || placa;
        const semana = document.getElementById('semanaInputGasolina').value;
        const costo = parseFloat(document.getElementById('costoInput').value) || 23.90;
        const card = document.getElementById('statusTopeCard');
        
        if((!placa && !vehiculo) || !semana) {
            card.style.display = 'none';
            return;
        }

        try {
            let url = `/api/gasolina/tope_status?vehiculo=${encodeURIComponent(vehiculo)}&placa=${encodeURIComponent(placa)}&semana=${encodeURIComponent(semana)}&precio_unitario=${costo}`;
            if (currentSelectedMaestroId) {
                url += `&maestro_id=${currentSelectedMaestroId}`;
            }
            const res = await fetch(url);
            const data = await res.json();
            
            if(data.success) {
                card.style.display = 'block';
                const fmtM = v => '$' + Number(v).toLocaleString('es-MX', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                
                document.getElementById('valTopeSemanal').textContent = `${fmtM(data.monto_autorizado)} (${data.litros_autorizados.toFixed(2)} L)`;
                document.getElementById('valConsumidoSemanal').textContent = `${fmtM(data.consumido_importe)} (${data.consumido_litros.toFixed(2)} L)`;
                document.getElementById('valDisponibleSemanal').textContent = `${fmtM(data.disponible_importe)} (${data.disponible_litros.toFixed(2)} L)`;
                
                window.gasolinaTopeStatus = data;
                evaluarCargaExtraordinaria();
            } else {
                card.style.display = 'none';
            }
        } catch(e) {
            console.log('Error al consultar tope:', e);
        }
    }

    function evaluarCargaExtraordinaria() {
        if(!window.gasolinaTopeStatus) return;
        const data = window.gasolinaTopeStatus;
        const ltsActual = parseFloat(document.getElementById('litrosInput').value) || 0;
        const costoActual = parseFloat(document.getElementById('costoInput').value) || 23.90;
        const importeHoy = Math.round(ltsActual * costoActual * 100) / 100;

        const warnBox = document.getElementById('extraordinarioWarningBox');
        const esExtraInput = document.getElementById('esExtraordinarioInput');
        const msgLbl = document.getElementById('lblExtraordinarioMsg');
        
        if (data.monto_autorizado > 0 && (data.consumido_importe + importeHoy) > data.monto_autorizado) {
            const excesoMonto = (data.consumido_importe + importeHoy) - data.monto_autorizado;
            warnBox.style.display = 'block';
            esExtraInput.value = '1';
            msgLbl.textContent = `La carga actual ($${importeHoy.toFixed(2)}) junto con el acumulado semanal ($${data.consumido_importe.toFixed(2)}) excede el presupuesto autorizado ($${data.monto_autorizado.toFixed(2)}) por $${excesoMonto.toFixed(2)} MXN.`;
        } else {
            warnBox.style.display = 'none';
            esExtraInput.value = '0';
        }
    }

    // Auto-calculate Importe
    function calcularImporte() {
        const litros = parseFloat(document.getElementById('litrosInput').value) || 0;
        const costo = parseFloat(document.getElementById('costoInput').value) || 0;
        const importe = Math.round(litros * costo * 100) / 100;
        document.getElementById('importeInput').value = importe > 0 ? importe : '';
        evaluarCargaExtraordinaria();
    }

    // Tab Switcher
    function switchTab(tab) {
        // Hide all
        document.getElementById('formConsumoContainer').style.display = 'none';
        document.getElementById('formFacturaContainer').style.display = 'none';
        document.getElementById('historyConsumo').style.display = 'none';
        document.getElementById('historyFactura').style.display = 'none';
        document.getElementById('historicoTitle').style.display = 'none';

        // Reset buttons
        document.getElementById('btnTabConsumo').style.background = 'transparent';
        document.getElementById('btnTabConsumo').style.color = 'var(--text-muted)';
        document.getElementById('btnTabFactura').style.background = 'transparent';
        document.getElementById('btnTabFactura').style.color = 'var(--text-muted)';

        if (tab === 'consumo') {
            document.getElementById('formConsumoContainer').style.display = 'block';
            document.getElementById('historyConsumo').style.display = 'block';
            document.getElementById('historicoTitle').style.display = 'block';
            document.getElementById('btnTabConsumo').style.background = 'var(--primary)';
            document.getElementById('btnTabConsumo').style.color = 'white';
        } else if (tab === 'factura') {
            document.getElementById('formFacturaContainer').style.display = 'block';
            document.getElementById('historyFactura').style.display = 'block';
            document.getElementById('historicoTitle').style.display = 'block';
            document.getElementById('btnTabFactura').style.background = 'var(--primary)';
            document.getElementById('btnTabFactura').style.color = 'white';
        }
    }

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
                
                const imgContainer = document.createElement('div');
                imgContainer.style.position = 'relative';
                imgContainer.style.display = 'inline-block';
                imgContainer.style.marginRight = '10px';
                
                const img = document.createElement('img');
                img.src = src;
                img.style.maxHeight = '80px';
                img.style.borderRadius = '8px';
                
                const btnBorrar = document.createElement('button');
                btnBorrar.innerHTML = '&times;';
                btnBorrar.style.position = 'absolute';
                btnBorrar.style.top = '-5px';
                btnBorrar.style.right = '-5px';
                btnBorrar.style.background = 'red';
                btnBorrar.style.color = 'white';
                btnBorrar.style.border = 'none';
                btnBorrar.style.borderRadius = '50%';
                btnBorrar.style.width = '20px';
                btnBorrar.style.height = '20px';
                btnBorrar.style.cursor = 'pointer';
                btnBorrar.style.fontSize = '14px';
                btnBorrar.style.lineHeight = '14px';
                btnBorrar.style.padding = '0';
                
                btnBorrar.onclick = function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    const newDt = new DataTransfer();
                    for(let j=0; j<dtConsumo.files.length; j++) {
                        if(j !== i) newDt.items.add(dtConsumo.files[j]);
                    }
                    dtConsumo = newDt;
                    updatePreviews();
                };
                
                imgContainer.appendChild(img);
                imgContainer.appendChild(btnBorrar);
                previewConsumo.appendChild(imgContainer);
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

            if(data.semana) {
                document.getElementById('semanaFacturaInput').value = data.semana;
            }

            facturaUUID = data.uuid;
            facturaFecha = data.fecha;
            facturaFolioFactura = data.folio_factura || '';
            facturaProveedor = data.proveedor || '';
            cargasExtraidas = data.cargas;

            if(data.obra_sugerida) {
                tomSelectFacturaObra.setValue(data.obra_sugerida);
            }

            const listaDiv = document.getElementById('listaCargas');
            listaDiv.innerHTML = '';

            if(cargasExtraidas.length === 0) {
                listaDiv.innerHTML = '<p style="color:var(--accent)">No se detectaron partidas de Gasolina en el XML. Verifica que el XML contenga conceptos de gasolina/combustible.</p>';
            }

            cargasExtraidas.forEach((c, idx) => {
                listaDiv.innerHTML += `
                    <div style="background: rgba(255,255,255,0.05); padding: 0.5rem 1rem; border-radius: 8px; border-left: 4px solid var(--primary);">
                        <p style="margin:0; font-size:0.9rem"><strong>Carga #${idx+1}</strong> - ${c.descripcion}</p>
                        <p style="margin:0; font-size:0.85rem; color:var(--text-muted)">Litros: ${c.litros} | Precio: $${c.precio} | IVA: $${c.iva} | <strong>Total: $${c.total}</strong></p>
                    </div>
                `;
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
    document.getElementById('gasolinaForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        const btn = document.getElementById('submitBtnConsumo');
        btn.innerHTML = 'Guardando...';
        btn.disabled = true;

        try {
            const formData = new FormData(this);
            // Attach the custom file list
            if(dtConsumo.files.length > 0) {
                formData.delete('foto_evidencia');
                for(let i=0; i<dtConsumo.files.length; i++) {
                    formData.append('foto_evidencia', dtConsumo.files[i]);
                }
            }
            const res = await fetch('/api/gasolina/consumo', { method: 'POST', body: formData });
            const result = await res.json();
            if(result.success) {
                showToast('Consumo guardado: ' + result.folio, 'success');
                setTimeout(() => window.location.reload(), 1500);
            } else {
                showToast(result.error || 'Error al guardar.', 'error');
                btn.innerHTML = 'Guardar Consumo';
                btn.disabled = false;
            }
        } catch(error) {
            showToast('Error de conexión.', 'error');
            btn.innerHTML = 'Guardar Consumo';
            btn.disabled = false;
        }
    });

    // Submit Facturas
    document.getElementById('facturaForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        if(cargasExtraidas.length === 0) {
            alert('No hay cargas de Gasolina para guardar.');
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
            semana: document.getElementById('semanaFacturaInput').value,
            folio_factura: facturaFolioFactura,
            proveedor: facturaProveedor,
            cargas: cargasExtraidas
        };

        try {
            const res = await fetch('/api/gasolina/facturas_batch', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if(data.success) {
                showToast('Factura guardada: ' + data.folio, 'success');
                setTimeout(() => window.location.reload(), 1500);
            } else {
                alert('Error: ' + data.error);
                btn.innerHTML = 'Guardar Todas las Cargas';
                btn.disabled = false;
            }
        } catch(err) {
            alert('Error de conexión al guardar factura.');
            btn.innerHTML = 'Guardar Todas las Cargas';
            btn.disabled = false;
        }
    });
    // ==================== GESTOR DE FOTOGRAFÍAS DE EVIDENCIA (SELECCIÓN, ARRASTRE Y PORTAPAPELES) ====================
    let selectedFilesConsumo = new DataTransfer();

    function updateFileInputAndPreview() {
        const fileInput = document.getElementById('fileInputConsumo');
        const previewArea = document.getElementById('previewConsumo');
        const uploadText = document.getElementById('uploadTextConsumo');
        
        if (fileInput) {
            fileInput.files = selectedFilesConsumo.files;
        }

        if (uploadText) {
            const cant = selectedFilesConsumo.files.length;
            if (cant === 0) {
                uploadText.innerHTML = '📸 Toca para abrir la cámara, selecciona fotos, arrastra o pega desde el portapapeles (Ctrl + V)';
            } else {
                uploadText.innerHTML = `✅ <strong>${cant} fotografía(s) adjuntada(s)</strong> — Toca para agregar más o pega desde el portapapeles (Ctrl + V)`;
            }
        }
        
        if (previewArea) {
            previewArea.innerHTML = '';
            Array.from(selectedFilesConsumo.files).forEach((file, index) => {
                if (!file.type.startsWith('image/')) return;
                
                const reader = new FileReader();
                reader.onload = function(e) {
                    const container = document.createElement('div');
                    container.style.cssText = 'position: relative; width: 90px; height: 90px; border-radius: 8px; overflow: hidden; border: 2px solid var(--primary); box-shadow: 0 4px 12px rgba(0,0,0,0.4); background: #0f172a;';
                    
                    const img = document.createElement('img');
                    img.src = e.target.result;
                    img.style.cssText = 'width: 100%; height: 100%; object-fit: cover;';
                    
                    const removeBtn = document.createElement('button');
                    removeBtn.type = 'button';
                    removeBtn.innerHTML = '✕';
                    removeBtn.title = 'Eliminar imagen';
                    removeBtn.style.cssText = 'position: absolute; top: 3px; right: 3px; background: #ef4444; color: white; border: none; border-radius: 50%; width: 22px; height: 22px; font-size: 12px; font-weight: bold; cursor: pointer; display: flex; align-items: center; justify-content: center; z-index: 10; box-shadow: 0 2px 5px rgba(0,0,0,0.5);';
                    removeBtn.onclick = function(ev) {
                        ev.stopPropagation();
                        ev.preventDefault();
                        removeFileConsumo(index);
                    };
                    
                    container.appendChild(img);
                    container.appendChild(removeBtn);
                    previewArea.appendChild(container);
                };
                reader.readAsDataURL(file);
            });
        }
    }

    function addFilesConsumo(files) {
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            if (file.type.startsWith('image/')) {
                selectedFilesConsumo.items.add(file);
            }
        }
        updateFileInputAndPreview();
    }

    function removeFileConsumo(index) {
        const dt = new DataTransfer();
        Array.from(selectedFilesConsumo.files).forEach((file, i) => {
            if (i !== index) dt.items.add(file);
        });
        selectedFilesConsumo = dt;
        updateFileInputAndPreview();
    }

    // 1. Evento Change en el input file
    const fileInputConsumo = document.getElementById('fileInputConsumo');
    if (fileInputConsumo) {
        fileInputConsumo.addEventListener('change', function(e) {
            if (this.files && this.files.length > 0) {
                addFilesConsumo(this.files);
            }
        });
    }

    // 2. Drag & Drop en la zona de carga
    const dropAreaConsumo = document.getElementById('dropAreaConsumo');
    if (dropAreaConsumo) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropAreaConsumo.addEventListener(eventName, function(e) {
                e.preventDefault();
                e.stopPropagation();
            }, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            dropAreaConsumo.addEventListener(eventName, () => {
                dropAreaConsumo.style.borderColor = 'var(--primary)';
                dropAreaConsumo.style.background = 'rgba(59, 130, 246, 0.15)';
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropAreaConsumo.addEventListener(eventName, () => {
                dropAreaConsumo.style.borderColor = '';
                dropAreaConsumo.style.background = '';
            }, false);
        });

        dropAreaConsumo.addEventListener('drop', function(e) {
            const dt = e.dataTransfer;
            if (dt && dt.files && dt.files.length > 0) {
                addFilesConsumo(dt.files);
            }
        });
    }

    // 3. Pegado directo desde el Portapapeles (Ctrl+V / Win+V)
    document.addEventListener('paste', function(e) {
        const container = document.getElementById('formConsumoContainer');
        if (container && container.style.display === 'none') return;

        const activeEl = document.activeElement;
        const targetTag = activeEl ? activeEl.tagName.toLowerCase() : '';
        if (targetTag === 'textarea') return;
        
        const items = (e.clipboardData || e.originalEvent.clipboardData).items;
        if (!items) return;

        let pastedFiles = [];
        for (let i = 0; i < items.length; i++) {
            if (items[i].type.indexOf('image') !== -1) {
                const blob = items[i].getAsFile();
                if (blob) {
                    const ext = blob.type.split('/')[1] || 'png';
                    const file = new File([blob], `evidencia_pegada_${Date.now()}_${i}.${ext}`, { type: blob.type });
                    pastedFiles.push(file);
                }
            }
        }

        if (pastedFiles.length > 0) {
            addFilesConsumo(pastedFiles);
            if (typeof showToast === 'function') {
                showToast(`📸 ${pastedFiles.length} imagen(es) pegada(s) desde el portapapeles.`, 'success');
            }
        }
    });

    // Auto calcular semana al cambiar fecha
    document.getElementById("fechaInputGasolina").addEventListener("change", function(e) {
        if(!this.value) return;
        const parts = this.value.split('-');
        const d = new Date(parts[0], parts[1]-1, parts[2]);
        const dayNum = d.getDay() || 7;
        d.setDate(d.getDate() + 4 - dayNum);
        const yearStart = new Date(d.getFullYear(),0,1);
        const week = Math.ceil((((d - yearStart) / 86400000) + 1)/7);
        document.getElementById("semanaInputGasolina").value = week;
    });

