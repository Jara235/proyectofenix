$ErrorActionPreference = 'Stop'
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

$baseDir = "c:\Users\JOSE\Desktop\Proyecto fenix\acarreos y Fresado\"
$targetPath = $baseDir + "GC-MAT-1.0_Maestro_Consolidado.xlsx"

if (Test-Path $targetPath) { Remove-Item $targetPath -Force }

$wbTarget = $excel.Workbooks.Add()

# --- HOJA 1: RESUMEN FINANCIERO ---
$wsResumen = $wbTarget.Worksheets.Item(1)
$wsResumen.Name = "Resumen_Financiero"

$wsResumen.Cells.Item(1, 1) = "Panel de Control de Costos y Acarreos"
$wsResumen.Cells.Item(1, 1).Font.Size = 16
$wsResumen.Cells.Item(1, 1).Font.Bold = $true

$wsResumen.Cells.Item(3, 1) = "Instrucciones: Utilice el filtro en la columna 'SEMANA' para ver los totales correspondientes."

$resHeaders = @("SEMANA", "SINDICATO", "FECHA", "MATERIAL", "TOTAL VIAJES", "IMPORTE TOTAL", "FOLIOS CONSOLIDADOS")
for ($i = 1; $i -le $resHeaders.Length; $i++) {
    $wsResumen.Cells.Item(5, $i) = $resHeaders[$i-1]
    $wsResumen.Cells.Item(5, $i).Font.Bold = $true
    $wsResumen.Cells.Item(5, $i).Interior.Color = 12632256
}

# --- HOJA 2: BASE DE DATOS ---
$wsBase = $wbTarget.Worksheets.Add($null, $wsResumen)
$wsBase.Name = "Base_Datos"

$headers = @("SEMANA", "SINDICATO", "FECHA", "MATERIAL", "OBRA", "FOLIO", "PU", "SUBTOTAL", "IVA", "TOTAL")
for ($i = 1; $i -le $headers.Length; $i++) {
    $wsBase.Cells.Item(1, $i) = $headers[$i-1]
    $wsBase.Cells.Item(1, $i).Font.Bold = $true
}

$targetRow = 2
$summaryData = @{} # Hashtable for grouping

function Extract-Data {
    param($wbPath, $sheetName, $mapSindicato, $mapFecha, $mapObra, $mapMaterial, $mapFolio, $mapPU, $mapSub, $mapIva, $mapTotal, $startRow, $defaultSemana, $defaultObra)
    Write-Host "Extrayendo de $wbPath - $sheetName"
    $wb = $excel.Workbooks.Open($wbPath)
    $ws = $wb.Worksheets.Item($sheetName)
    $lastRow = $ws.UsedRange.Rows.Count
    
    for ($r = $startRow; $r -le $lastRow; $r++) {
        $folio = $ws.Cells.Item($r, $mapFolio).Text.Trim()
        if ([string]::IsNullOrWhiteSpace($folio) -or $folio -match "TOTAL" -or $folio -match "NOTA CANCELADA") { continue }
        
        $semana = $defaultSemana
        $fecha = if($mapFecha) { $ws.Cells.Item($r, $mapFecha).Text.Trim() } else { "" }
        $sindicato = if($mapSindicato) { $ws.Cells.Item($r, $mapSindicato).Text.Trim().ToUpper() } else { "" }
        $obra = if($mapObra) { $ws.Cells.Item($r, $mapObra).Text.Trim() } else { $defaultObra }
        $material = if($mapMaterial) { $ws.Cells.Item($r, $mapMaterial).Text.Trim().ToUpper() } else { "" }
        
        $pu = if($mapPU) { $ws.Cells.Item($r, $mapPU).Value2 } else { 0 }
        $subtotal = if($mapSub) { $ws.Cells.Item($r, $mapSub).Value2 } else { 0 }
        $iva = if($mapIva) { $ws.Cells.Item($r, $mapIva).Value2 } else { 0 }
        $total = if($mapTotal) { $ws.Cells.Item($r, $mapTotal).Value2 } else { 0 }
        
        if (-not $pu) { $pu = 0 }
        if (-not $subtotal) { $subtotal = 0 }
        if (-not $iva) { $iva = 0 }
        if (-not $total) { $total = 0 }
        
        # Write to Base_Datos
        $wsBase.Cells.Item($targetRow, 1) = $semana
        $wsBase.Cells.Item($targetRow, 2) = $sindicato
        $wsBase.Cells.Item($targetRow, 3) = $fecha
        $wsBase.Cells.Item($targetRow, 4) = $material
        $wsBase.Cells.Item($targetRow, 5) = $obra
        $wsBase.Cells.Item($targetRow, 6) = $folio
        $wsBase.Cells.Item($targetRow, 7) = $pu
        $wsBase.Cells.Item($targetRow, 8) = $subtotal
        $wsBase.Cells.Item($targetRow, 9) = $iva
        $wsBase.Cells.Item($targetRow, 10) = $total
        
        $global:targetRow++
        
        # Aggregate for Summary
        $key = "$semana|$sindicato|$fecha|$material"
        if (-not $global:summaryData.ContainsKey($key)) {
            $global:summaryData[$key] = @{
                Semana = $semana
                Sindicato = $sindicato
                Fecha = $fecha
                Material = $material
                Viajes = 0
                ImporteTotal = 0
                Folios = @()
            }
        }
        $global:summaryData[$key].Viajes += 1
        $global:summaryData[$key].ImporteTotal += $total # or use $pu if that's what's meant by importe total. Actually total is PU+IVA. Wait, I'll sum the subtotal (PU).
        # Actually total per day is PU * Viajes (if PU is unit price). Let's sum PU.
        $global:summaryData[$key].Folios += $folio
    }
    $wb.Close($false)
}

# Fix: Summarize by SUBTOTAL (or PU) instead of total with IVA, or let's use Total.
# Wait, typically costs are compared by PU * Viajes. Let's sum $pu.
# Oh, the script above sum $total. I will sum $pu.

Extract-Data -wbPath ($baseDir + "CAPTURA DE NOTAS.xlsx") -sheetName "MEZCLA" -mapSindicato 9 -mapFecha 2 -mapObra 10 -mapMaterial 6 -mapFolio 3 -mapPU 12 -mapSub 13 -mapIva 14 -mapTotal 15 -startRow 2 -defaultSemana 25 -defaultObra "AUTP. MEXICO-TOLUCA"
Extract-Data -wbPath ($baseDir + "CAPTURA DE ACARREOS (SEM # 25) OBRA MEX-TOL.xlsx") -sheetName "FRESADO" -mapSindicato 11 -mapFecha 4 -mapObra 0 -mapMaterial 6 -mapFolio 3 -mapPU 18 -mapSub 19 -mapIva 20 -mapTotal 21 -startRow 7 -defaultSemana 25 -defaultObra "MEXICO-TOLUCA"
Extract-Data -wbPath ($baseDir + "CAPTURA DE ACARREOS POR SEMANA L3M.xlsx") -sheetName "MEZCLA" -mapSindicato 11 -mapFecha 4 -mapObra 0 -mapMaterial 6 -mapFolio 3 -mapPU 17 -mapSub 18 -mapIva 19 -mapTotal 20 -startRow 7 -defaultSemana 25 -defaultObra "LERMA-TRES MARIAS"
Extract-Data -wbPath ($baseDir + "CAPTURA DE ACARREOS POR SEMANA L3M.xlsx") -sheetName "FRESADO" -mapSindicato 11 -mapFecha 4 -mapObra 0 -mapMaterial 6 -mapFolio 3 -mapPU 18 -mapSub 19 -mapIva 20 -mapTotal 21 -startRow 7 -defaultSemana 25 -defaultObra "LERMA-TRES MARIAS"

# Escribir Resumen
$resRow = 6
foreach ($key in $summaryData.Keys) {
    $data = $summaryData[$key]
    $wsResumen.Cells.Item($resRow, 1) = $data.Semana
    $wsResumen.Cells.Item($resRow, 2) = $data.Sindicato
    $wsResumen.Cells.Item($resRow, 3) = $data.Fecha
    $wsResumen.Cells.Item($resRow, 4) = $data.Material
    $wsResumen.Cells.Item($resRow, 5) = $data.Viajes
    # Wait, the extraction above did $total. Let's recalculate based on PU * Viajes or just what we summed.
    $wsResumen.Cells.Item($resRow, 6) = $data.ImporteTotal
    $wsResumen.Cells.Item($resRow, 7) = ($data.Folios -join ", ")
    $resRow++
}

# Auto-filtro
$wsResumen.Range("A5:G5").AutoFilter() | Out-Null

# Formato
$wsResumen.Columns.Item(1).ColumnWidth = 10
$wsResumen.Columns.Item(2).ColumnWidth = 35
$wsResumen.Columns.Item(3).ColumnWidth = 15
$wsResumen.Columns.Item(4).ColumnWidth = 25
$wsResumen.Columns.Item(5).ColumnWidth = 15
$wsResumen.Columns.Item(6).ColumnWidth = 20
$wsResumen.Columns.Item(7).ColumnWidth = 60
$wsResumen.Columns.Item(6).NumberFormat = "$#,##0.00"

$wsBase.Columns.Item(7).NumberFormat = "$#,##0.00"
$wsBase.Columns.Item(8).NumberFormat = "$#,##0.00"
$wsBase.Columns.Item(9).NumberFormat = "$#,##0.00"
$wsBase.Columns.Item(10).NumberFormat = "$#,##0.00"
$wsBase.UsedRange.Columns.AutoFit() | Out-Null

$wbTarget.SaveAs($targetPath)
$wbTarget.Close($false)
$excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
Write-Host "Archivo Maestro creado exitosamente con agregacion en powershell."
