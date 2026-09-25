$ErrorActionPreference = 'Stop'
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

$baseDir = "c:\Users\JOSE\Desktop\Proyecto fenix\acarreos y Fresado\"
$targetPath = $baseDir + "GC-MAT-1.0_Maestro_Consolidado_V7.xlsx"

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

function Sanitize-Obra {
    param($val)
    $v = $val.Trim().ToUpper()
    if ($v -match "MXICO" -or $v -match "MEXICO") {
        return "MÉXICO-TOLUCA"
    }
    return $val
}

# --- HOJA 1: DASHBOARD EJECUTIVO ---
$wsResumen = $wbTarget.Worksheets.Item(1)
$wsResumen.Name = "Dashboard_Ejecutivo"

$wsResumen.Cells.Item(1, 2) = "Mezcla Asfáltica por Día y Obra"
$wsResumen.Cells.Item(1, 10) = "Fresado por Día y Obra"
$wsResumen.Cells.Item(1, 18) = "Total Acarreos en Obra"
$wsResumen.Cells.Item(1, 2).Font.Bold = $true
$wsResumen.Cells.Item(1, 10).Font.Bold = $true
$wsResumen.Cells.Item(1, 18).Font.Bold = $true

# --- HOJA 2: BASE DE DATOS ---
$wsBase = $wbTarget.Worksheets.Add()
$wsBase.Name = "Base_Datos"

$headersBD = @("SEMANA", "FECHA", "FOLIO", "SINDICATO", "OBRA", "MATERIAL", "PLACA", "OPERADOR", "CAPACIDAD", "OBSERVACIONES", "PU", "SUBTOTAL", "IVA", "TOTAL", "CATEGORIA")
for ($i = 1; $i -le $headersBD.Length; $i++) {
    $wsBase.Cells.Item(1, $i) = $headersBD[$i-1]
    $wsBase.Cells.Item(1, $i).Font.Bold = $true
    $wsBase.Cells.Item(1, $i).Interior.Color = 14277081
}

$targetRow = 2

function Extract-Data {
    param($wbPath, $sheetName, $mapSindicato, $mapFecha, $mapObra, $mapMaterial, $mapFolio, $mapPlaca, $mapOperador, $mapCapacidad, $mapObs, $mapPU, $mapSub, $mapIva, $mapTotal, $startRow, $defaultSemana, $defaultObra)
    Write-Host "Extrayendo de $sheetName"
    $wb = $excel.Workbooks.Open($wbPath)
    $ws = $wb.Worksheets.Item($sheetName)
    $lastRow = $ws.UsedRange.Rows.Count
    
    for ($r = $startRow; $r -le $lastRow; $r++) {
        $folio = $ws.Cells.Item($r, $mapFolio).Text.Trim()
        $sindicato = if($mapSindicato) { $ws.Cells.Item($r, $mapSindicato).Text.Trim().ToUpper() } else { "" }
        $material = if($mapMaterial) { $ws.Cells.Item($r, $mapMaterial).Text.Trim().ToUpper() } else { "" }
        $observaciones = if($mapObs) { $ws.Cells.Item($r, $mapObs).Text.Trim() } else { "" }
        
        # Check for cancelled notes across multiple fields
        $isCancelled = ($folio -match "CANCELADA") -or ($sindicato -match "CANCELADA") -or ($material -match "CANCELADA") -or ($observaciones -match "CANCELADA")
        
        if (-not $isCancelled) {
            if ([string]::IsNullOrWhiteSpace($folio) -or $folio -match "TOTAL") { continue }
        }
        
        $rawFecha = if($mapFecha) { $ws.Cells.Item($r, $mapFecha).Value2 } else { "" }
        if ($rawFecha -eq $null) { $rawFecha = $ws.Cells.Item($r, $mapFecha).Text }
        $fecha = Format-DateString -val $rawFecha
        
        $obraRaw = if($mapObra) { $ws.Cells.Item($r, $mapObra).Text.Trim() } else { $defaultObra }
        if ($obraRaw -eq "") { $obraRaw = $defaultObra }
        $obra = Sanitize-Obra -val $obraRaw
        
        $placa = if($mapPlaca) { $ws.Cells.Item($r, $mapPlaca).Text.Trim() } else { "" }
        $operador = if($mapOperador) { $ws.Cells.Item($r, $mapOperador).Text.Trim() } else { "" }
        $capacidad = if($mapCapacidad) { $ws.Cells.Item($r, $mapCapacidad).Text.Trim() } else { "" }
        
        $pu = if($mapPU) { $ws.Cells.Item($r, $mapPU).Value2 } else { 0 }
        $subtotal = if($mapSub) { $ws.Cells.Item($r, $mapSub).Value2 } else { 0 }
        $iva = if($mapIva) { $ws.Cells.Item($r, $mapIva).Value2 } else { 0 }
        $total = if($mapTotal) { $ws.Cells.Item($r, $mapTotal).Value2 } else { 0 }
        
        if (-not $pu) { $pu = 0 }
        if (-not $subtotal) { $subtotal = 0 }
        if (-not $iva) { $iva = 0 }
        if (-not $total) { $total = 0 }
        
        if ($isCancelled) {
            $sindicato = "CANCELADAS"
            $categoria = "CANCELADAS"
            $material = "CANCELADA"
            if ([string]::IsNullOrWhiteSpace($folio)) { $folio = "N/A" }
            $pu = 0; $subtotal = 0; $iva = 0; $total = 0
        } else {
            $categoria = "OTROS"
            if ($material -match "CARPETA" -or $material -match "MEZCLA" -or $material -match "PROTOCOLO") {
                $categoria = "MEZCLA"
            } elseif ($material -match "FRESADO" -or $material -match "LIMPIEZA") {
                $categoria = "FRESADO"
            } else {
                if ($sheetName -match "MEZCLA" -or $sheetName -match "CARPETA") { $categoria = "MEZCLA" }
                else { $categoria = "FRESADO" }
            }
        }
        
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
        $wsBase.Cells.Item($targetRow, 15) = $categoria
        
        $global:targetRow++
    }
    $wb.Close($false)
}

Extract-Data -wbPath ($baseDir + "CAPTURA DE NOTAS.xlsx") -sheetName "MEZCLA" -mapSindicato 9 -mapFecha 2 -mapObra 10 -mapMaterial 6 -mapFolio 3 -mapPlaca 4 -mapOperador 5 -mapCapacidad 8 -mapObs 11 -mapPU 12 -mapSub 13 -mapIva 14 -mapTotal 15 -startRow 2 -defaultSemana 25 -defaultObra "MÉXICO-TOLUCA"
Extract-Data -wbPath ($baseDir + "CAPTURA DE ACARREOS (SEM # 25) OBRA MEX-TOL.xlsx") -sheetName "FRESADO" -mapSindicato 11 -mapFecha 4 -mapObra 0 -mapMaterial 6 -mapFolio 3 -mapPlaca 7 -mapOperador 10 -mapCapacidad 8 -mapObs 17 -mapPU 18 -mapSub 19 -mapIva 20 -mapTotal 21 -startRow 7 -defaultSemana 25 -defaultObra "MÉXICO-TOLUCA"
Extract-Data -wbPath ($baseDir + "CAPTURA DE ACARREOS POR SEMANA L3M.xlsx") -sheetName "MEZCLA" -mapSindicato 11 -mapFecha 4 -mapObra 0 -mapMaterial 6 -mapFolio 3 -mapPlaca 7 -mapOperador 10 -mapCapacidad 8 -mapObs 17 -mapPU 17 -mapSub 18 -mapIva 19 -mapTotal 20 -startRow 7 -defaultSemana 25 -defaultObra "Lerma - Tres Marías"
Extract-Data -wbPath ($baseDir + "CAPTURA DE ACARREOS POR SEMANA L3M.xlsx") -sheetName "FRESADO" -mapSindicato 11 -mapFecha 4 -mapObra 0 -mapMaterial 6 -mapFolio 3 -mapPlaca 7 -mapOperador 10 -mapCapacidad 8 -mapObs 17 -mapPU 18 -mapSub 19 -mapIva 20 -mapTotal 21 -startRow 7 -defaultSemana 25 -defaultObra "Lerma - Tres Marías"

# Tablas Dinamicas
$last = $targetRow - 1
$dataRange = "Base_Datos!R1C1:R" + $last + "C15"
$pc = $wbTarget.PivotCaches().Create(1, $dataRange, 6)

# Pivot Table 1: MEZCLA (B4 / R4C2)
$pt1 = $pc.CreatePivotTable("Dashboard_Ejecutivo!R4C2", "PT_Mezcla")
$pt1.PivotFields("FECHA").Orientation = 1
$pt1.PivotFields("OBRA").Orientation = 1
$pt1.PivotFields("SINDICATO").Orientation = 1
$pt1.PivotFields("FOLIO").Orientation = 1

$df1_1 = $pt1.AddDataField($pt1.PivotFields("FOLIO"), "Viajes", -4112)
$df1_2 = $pt1.AddDataField($pt1.PivotFields("PU"), "Costo Surtido", -4157)
$df1_2.NumberFormat = "$#,##0.00"

$pt1.PivotFields("CATEGORIA").Orientation = 3
$pt1.PivotFields("CATEGORIA").CurrentPage = "MEZCLA"
$pt1.PivotFields("SEMANA").Orientation = 3

# Pivot Table 2: FRESADO (J4 / R4C10)
$pt2 = $pc.CreatePivotTable("Dashboard_Ejecutivo!R4C10", "PT_Fresado")
$pt2.PivotFields("FECHA").Orientation = 1
$pt2.PivotFields("OBRA").Orientation = 1
$pt2.PivotFields("SINDICATO").Orientation = 1
$pt2.PivotFields("FOLIO").Orientation = 1

$df2_1 = $pt2.AddDataField($pt2.PivotFields("FOLIO"), "Viajes ", -4112) 
$df2_2 = $pt2.AddDataField($pt2.PivotFields("PU"), " Costo Surtido", -4157) 
$df2_2.NumberFormat = "$#,##0.00"

$pt2.PivotFields("CATEGORIA").Orientation = 3
$pt2.PivotFields("CATEGORIA").CurrentPage = "FRESADO"
$pt2.PivotFields("SEMANA").Orientation = 3

# Pivot Table 3: TOTAL (R4 / R4C18)
$pt3 = $pc.CreatePivotTable("Dashboard_Ejecutivo!R4C18", "PT_Total")
$pt3.PivotFields("FECHA").Orientation = 1
$pt3.PivotFields("OBRA").Orientation = 1
$pt3.PivotFields("SINDICATO").Orientation = 1  # NEW REQUEST: agregar sindicato a la tercer tabla

$df3_1 = $pt3.AddDataField($pt3.PivotFields("FOLIO"), "Viajes Totales", -4112)
$df3_2 = $pt3.AddDataField($pt3.PivotFields("PU"), "Costo Total Obra", -4157)
$df3_2.NumberFormat = "$#,##0.00"
$pt3.PivotFields("SEMANA").Orientation = 3

# Design Pivot tables slightly
$pt1.TableStyle2 = "PivotStyleMedium9"
$pt2.TableStyle2 = "PivotStyleMedium9"
$pt3.TableStyle2 = "PivotStyleMedium14"

$pt1.RowAxisLayout(1)
$pt2.RowAxisLayout(1)
$pt3.RowAxisLayout(1)

# Desactivar Autoajuste en actualizar
$pt1.HasAutoFormat = $false
$pt2.HasAutoFormat = $false
$pt3.HasAutoFormat = $false

# Formato Dashboard
$wsResumen.Columns.Item(2).ColumnWidth = 15
$wsResumen.Columns.Item(3).ColumnWidth = 15
$wsResumen.Columns.Item(4).ColumnWidth = 18
$wsResumen.Columns.Item(5).ColumnWidth = 15
$wsResumen.Columns.Item(6).ColumnWidth = 10
$wsResumen.Columns.Item(7).ColumnWidth = 15

$wsResumen.Columns.Item(10).ColumnWidth = 15
$wsResumen.Columns.Item(11).ColumnWidth = 15
$wsResumen.Columns.Item(12).ColumnWidth = 18
$wsResumen.Columns.Item(13).ColumnWidth = 15
$wsResumen.Columns.Item(14).ColumnWidth = 10
$wsResumen.Columns.Item(15).ColumnWidth = 15

$wsResumen.Columns.Item(18).ColumnWidth = 15
$wsResumen.Columns.Item(19).ColumnWidth = 15
$wsResumen.Columns.Item(20).ColumnWidth = 18
$wsResumen.Columns.Item(21).ColumnWidth = 10
$wsResumen.Columns.Item(22).ColumnWidth = 15

$wsBase.Columns.Item(11).NumberFormat = "$#,##0.00"
$wsBase.Columns.Item(12).NumberFormat = "$#,##0.00"
$wsBase.Columns.Item(13).NumberFormat = "$#,##0.00"
$wsBase.Columns.Item(14).NumberFormat = "$#,##0.00"
$wsBase.UsedRange.Columns.AutoFit() | Out-Null
$wsBase.Range("A1:O1").AutoFilter() | Out-Null

$wsResumen.Move($wsBase)

$wbTarget.SaveAs($targetPath)
$wbTarget.Close($false)
$excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
Write-Host "Archivo Maestro final (Tablas Dinamicas) creado."
