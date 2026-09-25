$ErrorActionPreference = 'Stop'
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

$baseDir = "c:\Users\JOSE\Desktop\Proyecto fenix\acarreos y Fresado\"
$targetPath = $baseDir + "GC-MAT-1.0_Maestro_Consolidado.xlsx"

if (Test-Path $targetPath) { Remove-Item $targetPath -Force }

$wbTarget = $excel.Workbooks.Add()

function Format-DateString {
    param($val)
    if ([string]::IsNullOrWhiteSpace($val)) { return "" }
    if ($val -match '^\d{5}$') {
        try { return [DateTime]::FromOADate([double]$val).ToString("dd/MM/yyyy") } catch {}
    }
    try {
        $dt = [DateTime]::Parse($val)
        return $dt.ToString("dd/MM/yyyy")
    } catch {
        try { return $val } catch {}
    }
    return $val
}

# --- HOJA 1: DASHBOARD EJECUTIVO ---
$wsResumen = $wbTarget.Worksheets.Item(1)
$wsResumen.Name = "Dashboard_Ejecutivo"

$wsResumen.Cells.Item(1, 2) = "Mezcla Asfaltica por Dia y Obra"
$wsResumen.Cells.Item(1, 9) = "Fresado por Dia y Obra"
$wsResumen.Cells.Item(1, 16) = "Total Acarreos en Obra"
$wsResumen.Cells.Item(1, 2).Font.Bold = $true
$wsResumen.Cells.Item(1, 9).Font.Bold = $true
$wsResumen.Cells.Item(1, 16).Font.Bold = $true

$headers1 = @("Fecha", "Obra", "Sindicato", "Total Viajes", "Folios", "Costo Total ($)")
for ($i=0; $i -lt $headers1.Length; $i++) {
    $wsResumen.Cells.Item(3, 2 + $i) = $headers1[$i]
    $wsResumen.Cells.Item(3, 2 + $i).Font.Bold = $true
    $wsResumen.Cells.Item(3, 2 + $i).Interior.Color = 12632256 
    $wsResumen.Cells.Item(3, 9 + $i) = $headers1[$i]
    $wsResumen.Cells.Item(3, 9 + $i).Font.Bold = $true
    $wsResumen.Cells.Item(3, 9 + $i).Interior.Color = 12632256
    
    if ($i -lt 5) {
        $wsResumen.Cells.Item(3, 16 + $i) = $headers1[$i]
        $wsResumen.Cells.Item(3, 16 + $i).Font.Bold = $true
        $wsResumen.Cells.Item(3, 16 + $i).Interior.Color = 12632256
    }
}
$wsResumen.Cells.Item(3, 16 + 2) = "Viajes Totales" 
$wsResumen.Cells.Item(3, 16 + 3) = "Folios Totales"
$wsResumen.Cells.Item(3, 16 + 4) = "Costo Total ($)"

# --- HOJA 2: BASE DE DATOS ---
$wsBase = $wbTarget.Worksheets.Add()
$wsBase.Name = "Base_Datos"

$headersBD = @("SEMANA", "FECHA", "FOLIO", "SINDICATO", "OBRA", "MATERIAL", "PLACA", "OPERADOR", "CAPACIDAD", "OBSERVACIONES", "PU", "SUBTOTAL", "IVA", "TOTAL")
for ($i = 1; $i -le $headersBD.Length; $i++) {
    $wsBase.Cells.Item(1, $i) = $headersBD[$i-1]
    $wsBase.Cells.Item(1, $i).Font.Bold = $true
    $wsBase.Cells.Item(1, $i).Interior.Color = 14277081
}

$targetRow = 2
$mezclaData = @{}
$fresadoData = @{}
$totalData = @{}

function Extract-Data {
    param($wbPath, $sheetName, $mapSindicato, $mapFecha, $mapObra, $mapMaterial, $mapFolio, $mapPlaca, $mapOperador, $mapCapacidad, $mapObs, $mapPU, $mapSub, $mapIva, $mapTotal, $startRow, $defaultSemana, $defaultObra)
    Write-Host "Extrayendo de $sheetName"
    $wb = $excel.Workbooks.Open($wbPath)
    $ws = $wb.Worksheets.Item($sheetName)
    $lastRow = $ws.UsedRange.Rows.Count
    
    for ($r = $startRow; $r -le $lastRow; $r++) {
        $folio = $ws.Cells.Item($r, $mapFolio).Text.Trim()
        if ([string]::IsNullOrWhiteSpace($folio) -or $folio -match "TOTAL" -or $folio -match "NOTA CANCELADA") { continue }
        
        $rawFecha = if($mapFecha) { $ws.Cells.Item($r, $mapFecha).Value2 } else { "" }
        if ($rawFecha -eq $null) { $rawFecha = $ws.Cells.Item($r, $mapFecha).Text }
        $fecha = Format-DateString -val $rawFecha
        
        $sindicato = if($mapSindicato) { $ws.Cells.Item($r, $mapSindicato).Text.Trim().ToUpper() } else { "" }
        $obra = if($mapObra) { $ws.Cells.Item($r, $mapObra).Text.Trim() } else { $defaultObra }
        if ($obra -eq "") { $obra = $defaultObra }
        $material = if($mapMaterial) { $ws.Cells.Item($r, $mapMaterial).Text.Trim().ToUpper() } else { "" }
        $placa = if($mapPlaca) { $ws.Cells.Item($r, $mapPlaca).Text.Trim() } else { "" }
        $operador = if($mapOperador) { $ws.Cells.Item($r, $mapOperador).Text.Trim() } else { "" }
        $capacidad = if($mapCapacidad) { $ws.Cells.Item($r, $mapCapacidad).Text.Trim() } else { "" }
        $observaciones = if($mapObs) { $ws.Cells.Item($r, $mapObs).Text.Trim() } else { "" }
        
        $pu = if($mapPU) { $ws.Cells.Item($r, $mapPU).Value2 } else { 0 }
        $subtotal = if($mapSub) { $ws.Cells.Item($r, $mapSub).Value2 } else { 0 }
        $iva = if($mapIva) { $ws.Cells.Item($r, $mapIva).Value2 } else { 0 }
        $total = if($mapTotal) { $ws.Cells.Item($r, $mapTotal).Value2 } else { 0 }
        
        if (-not $pu) { $pu = 0 }
        if (-not $subtotal) { $subtotal = 0 }
        if (-not $iva) { $iva = 0 }
        if (-not $total) { $total = 0 }
        
        # Write to Base_Datos
        $wsBase.Cells.Item($targetRow, 1) = $defaultSemana
        $wsBase.Cells.Item($targetRow, 2) = $fecha
        $wsBase.Cells.Item($targetRow, 3) = $folio
        $wsBase.Cells.Item($targetRow, 4) = $sindicato
        $wsBase.Cells.Item($targetRow, 5) = $obra
        $wsBase.Cells.Item($targetRow, 6) = $material
        $wsBase.Cells.Item($targetRow, 7) = $placa
        $wsBase.Cells.Item($targetRow, 8) = $operador
        $wsBase.Cells.Item($targetRow, 9) = $capacidad
        $wsBase.Cells.Item($targetRow, 10) = $observaciones
        $wsBase.Cells.Item($targetRow, 11) = $pu
        $wsBase.Cells.Item($targetRow, 12) = $subtotal
        $wsBase.Cells.Item($targetRow, 13) = $iva
        $wsBase.Cells.Item($targetRow, 14) = $total
        
        $global:targetRow++
        
        # Determine target dict
        $targetDict = $null
        if ($material -match "CARPETA" -or $material -match "MEZCLA" -or $material -match "PROTOCOLO") {
            $targetDict = $global:mezclaData
        } elseif ($material -match "FRESADO" -or $material -match "LIMPIEZA") {
            $targetDict = $global:fresadoData
        } else {
            if ($sheetName -match "MEZCLA" -or $sheetName -match "CARPETA") { $targetDict = $global:mezclaData }
            else { $targetDict = $global:fresadoData }
        }
        
        $key = "$fecha|$obra|$sindicato"
        if (-not $targetDict.ContainsKey($key)) {
            $targetDict[$key] = @{ Fecha = $fecha; Obra = $obra; Sindicato = $sindicato; Viajes = 0; Importe = 0; Folios = @() }
        }
        $targetDict[$key].Viajes += 1
        $targetDict[$key].Importe += $pu
        $targetDict[$key].Folios += $folio
        
        # Total Dict
        $tkey = "$fecha|$obra"
        if (-not $global:totalData.ContainsKey($tkey)) {
            $global:totalData[$tkey] = @{ Fecha = $fecha; Obra = $obra; Viajes = 0; Importe = 0; Folios = @() }
        }
        $global:totalData[$tkey].Viajes += 1
        $global:totalData[$tkey].Importe += $pu
        $global:totalData[$tkey].Folios += $folio
    }
    $wb.Close($false)
}

Extract-Data -wbPath ($baseDir + "CAPTURA DE NOTAS.xlsx") -sheetName "MEZCLA" -mapSindicato 9 -mapFecha 2 -mapObra 10 -mapMaterial 6 -mapFolio 3 -mapPlaca 4 -mapOperador 5 -mapCapacidad 8 -mapObs 11 -mapPU 12 -mapSub 13 -mapIva 14 -mapTotal 15 -startRow 2 -defaultSemana 25 -defaultObra "Mxico-Toluca"
Extract-Data -wbPath ($baseDir + "CAPTURA DE ACARREOS (SEM # 25) OBRA MEX-TOL.xlsx") -sheetName "FRESADO" -mapSindicato 11 -mapFecha 4 -mapObra 0 -mapMaterial 6 -mapFolio 3 -mapPlaca 7 -mapOperador 10 -mapCapacidad 8 -mapObs 17 -mapPU 18 -mapSub 19 -mapIva 20 -mapTotal 21 -startRow 7 -defaultSemana 25 -defaultObra "Mxico-Toluca"
Extract-Data -wbPath ($baseDir + "CAPTURA DE ACARREOS POR SEMANA L3M.xlsx") -sheetName "MEZCLA" -mapSindicato 11 -mapFecha 4 -mapObra 0 -mapMaterial 6 -mapFolio 3 -mapPlaca 7 -mapOperador 10 -mapCapacidad 8 -mapObs 17 -mapPU 17 -mapSub 18 -mapIva 19 -mapTotal 20 -startRow 7 -defaultSemana 25 -defaultObra "Lerma - Tres Maras"
Extract-Data -wbPath ($baseDir + "CAPTURA DE ACARREOS POR SEMANA L3M.xlsx") -sheetName "FRESADO" -mapSindicato 11 -mapFecha 4 -mapObra 0 -mapMaterial 6 -mapFolio 3 -mapPlaca 7 -mapOperador 10 -mapCapacidad 8 -mapObs 17 -mapPU 18 -mapSub 19 -mapIva 20 -mapTotal 21 -startRow 7 -defaultSemana 25 -defaultObra "Lerma - Tres Maras"

# Escribir Resumen - Mezcla
$r = 4
foreach ($k in $mezclaData.Keys | Sort-Object) {
    $d = $mezclaData[$k]
    $wsResumen.Cells.Item($r, 2) = $d.Fecha
    $wsResumen.Cells.Item($r, 3) = $d.Obra
    $wsResumen.Cells.Item($r, 4) = $d.Sindicato
    $wsResumen.Cells.Item($r, 5) = $d.Viajes
    $wsResumen.Cells.Item($r, 6) = ($d.Folios -join ", ")
    $wsResumen.Cells.Item($r, 7) = $d.Importe
    $r++
}

# Escribir Resumen - Fresado
$r = 4
foreach ($k in $fresadoData.Keys | Sort-Object) {
    $d = $fresadoData[$k]
    $wsResumen.Cells.Item($r, 9) = $d.Fecha
    $wsResumen.Cells.Item($r, 10) = $d.Obra
    $wsResumen.Cells.Item($r, 11) = $d.Sindicato
    $wsResumen.Cells.Item($r, 12) = $d.Viajes
    $wsResumen.Cells.Item($r, 13) = ($d.Folios -join ", ")
    $wsResumen.Cells.Item($r, 14) = $d.Importe
    $r++
}

# Escribir Resumen - Total
$r = 4
foreach ($k in $totalData.Keys | Sort-Object) {
    $d = $totalData[$k]
    $wsResumen.Cells.Item($r, 16) = $d.Fecha
    $wsResumen.Cells.Item($r, 17) = $d.Obra
    $wsResumen.Cells.Item($r, 18) = $d.Viajes
    $wsResumen.Cells.Item($r, 19) = ($d.Folios -join ", ")
    $wsResumen.Cells.Item($r, 20) = $d.Importe
    $r++
}

# Auto-filtro
$wsBase.Range("A1:N1").AutoFilter() | Out-Null

# Formato Dashboard
$wsResumen.Columns.Item(2).ColumnWidth = 12
$wsResumen.Columns.Item(3).ColumnWidth = 20
$wsResumen.Columns.Item(4).ColumnWidth = 25
$wsResumen.Columns.Item(5).ColumnWidth = 12
$wsResumen.Columns.Item(6).ColumnWidth = 40
$wsResumen.Columns.Item(7).ColumnWidth = 15
$wsResumen.Columns.Item(7).NumberFormat = "$#,##0.00"

$wsResumen.Columns.Item(9).ColumnWidth = 12
$wsResumen.Columns.Item(10).ColumnWidth = 20
$wsResumen.Columns.Item(11).ColumnWidth = 25
$wsResumen.Columns.Item(12).ColumnWidth = 12
$wsResumen.Columns.Item(13).ColumnWidth = 40
$wsResumen.Columns.Item(14).ColumnWidth = 15
$wsResumen.Columns.Item(14).NumberFormat = "$#,##0.00"

$wsResumen.Columns.Item(16).ColumnWidth = 12
$wsResumen.Columns.Item(17).ColumnWidth = 20
$wsResumen.Columns.Item(18).ColumnWidth = 15
$wsResumen.Columns.Item(19).ColumnWidth = 50
$wsResumen.Columns.Item(20).ColumnWidth = 15
$wsResumen.Columns.Item(20).NumberFormat = "$#,##0.00"

$wsBase.Columns.Item(11).NumberFormat = "$#,##0.00"
$wsBase.Columns.Item(12).NumberFormat = "$#,##0.00"
$wsBase.Columns.Item(13).NumberFormat = "$#,##0.00"
$wsBase.Columns.Item(14).NumberFormat = "$#,##0.00"
$wsBase.UsedRange.Columns.AutoFit() | Out-Null

$wsResumen.Move($wsBase)

$wbTarget.SaveAs($targetPath)
$wbTarget.Close($false)
$excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
Write-Host "Archivo Maestro final creado."
