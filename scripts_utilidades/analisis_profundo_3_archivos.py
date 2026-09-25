import openpyxl

def analyze_file(filepath):
    print("=" * 80)
    print(f"RESUMEN DETALLADO: {filepath}")
    print("=" * 80)
    wb = openpyxl.load_workbook(filepath, data_only=True)
    for sheetname in wb.sheetnames:
        ws = wb[sheetname]
        print(f"\n>>> Hoja: '{sheetname}' | Filas totales: {ws.max_row} | Columnas: {ws.max_column}")
        
        # Encontrar fila de encabezados
        header_row = None
        headers = []
        for r in range(1, min(15, ws.max_row + 1)):
            row_vals = [ws.cell(r, c).value for c in range(1, min(ws.max_column + 1, 30))]
            # Checar si parece encabezado (contiene palabras como SEM, FOLIO, FECHA, MATERIAL, VIAJES, etc.)
            str_vals = [str(v).strip().upper() for v in row_vals if v is not None]
            if any(k in str_vals for k in ['SEM', 'SEMANA', 'FOLIO', 'FECHA', 'MATERIAL', 'PLACAS', 'OPERADOR', 'IMPORTE']):
                header_row = r
                headers = [str(v).strip() if v is not None else f'Col_{c}' for c, v in enumerate(row_vals, 1)]
                break
        
        if header_row:
            print(f"  Fila de Encabezados detectada en fila {header_row}:")
            print("  Columnas:", [h for h in headers if not h.startswith('Col_')][:15])
            
            # Contar registros reales y semanas
            semanas = set()
            fechas = []
            materiales = set()
            placas = set()
            total_m3 = 0.0
            total_kg = 0.0
            total_importe = 0.0
            registros_validos = 0
            
            # Mapear índices
            col_sem = None
            col_fecha = None
            col_mat = None
            col_placas = None
            col_m3 = None
            col_kg = None
            col_imp = None
            
            for idx, h in enumerate(headers):
                hu = h.upper()
                if 'SEM' in hu and col_sem is None: col_sem = idx + 1
                elif 'FECHA' in hu and col_fecha is None: col_fecha = idx + 1
                elif 'MATERIAL' in hu and col_mat is None: col_mat = idx + 1
                elif 'PLACA' in hu and col_placas is None: col_placas = idx + 1
                elif ('M3' in hu or 'CAPACIDAD' in hu) and col_m3 is None: col_m3 = idx + 1
                elif ('PESO' in hu or 'KG' in hu) and col_kg is None: col_kg = idx + 1
                elif 'IMPORTE' in hu and col_imp is None: col_imp = idx + 1
            
            for r in range(header_row + 1, ws.max_row + 1):
                val_sem = ws.cell(r, col_sem).value if col_sem else None
                val_fecha = ws.cell(r, col_fecha).value if col_fecha else None
                val_mat = ws.cell(r, col_mat).value if col_mat else None
                val_placa = ws.cell(r, col_placas).value if col_placas else None
                val_m3 = ws.cell(r, col_m3).value if col_m3 else None
                val_kg = ws.cell(r, col_kg).value if col_kg else None
                val_imp = ws.cell(r, col_imp).value if col_imp else None
                
                if val_sem is not None or val_fecha is not None or val_placa is not None:
                    registros_validos += 1
                    if val_sem:
                        try:
                            s_int = int(float(str(val_sem).replace('SEM', '').replace('#', '').strip()))
                            semanas.add(s_int)
                        except: pass
                    if val_mat: materiales.add(str(val_mat).strip())
                    if val_placa: placas.add(str(val_placa).strip())
                    if val_m3:
                        try: total_m3 += float(val_m3)
                        except: pass
                    if val_kg:
                        try: total_kg += float(val_kg)
                        except: pass
                    if val_imp:
                        try: total_importe += float(val_imp)
                        except: pass
            
            print(f"  --> Total registros válidos: {registros_validos}")
            print(f"  --> Semanas cubiertas: {sorted(list(semanas))}")
            print(f"  --> Materiales: {materiales}")
            print(f"  --> Camiones/Placas únicas: {len(placas)}")
            if total_m3 > 0: print(f"  --> Volumen Total (m³): {total_m3:,.2f} m³")
            if total_kg > 0: print(f"  --> Peso Total (Kg / Ton): {total_kg:,.2f} Kg ({total_kg/1000:,.2f} Ton)")
            if total_importe > 0: print(f"  --> Importe Total: ${total_importe:,.2f} MXN")

analyze_file('acarreos/OBRA MEXICO TOLUCA 2026 (6).xlsx')
analyze_file('acarreos/OBRA LERMA 3 MARIAS 2026 (13).xlsx')
analyze_file('acarreos/OBRA ALFREDO DEL MAZO (9).xlsx')
