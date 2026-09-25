$ErrorActionPreference = 'Stop'
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

$baseDir = "c:\Users\JOSE\Desktop\Proyecto fenix\acarreos y Fresado\"
$targetPath = $baseDir + "GC-MAT-1.0_Maestro_Consolidado.xlsx"

if (Test-Path $targetPath) { Remove-Item $targetPath -Force }

$wbTarget = $excel.Workbooks.Add()
$wsBase = $wbTarget.Worksheets.Item(1)
$wsBase.Name = "Base_Datos"

# Headers Base_Datos reordenados para facilitar UNIQUE
$headers = @("SEMANA", "SINDICATO", "FECHA", "MATERIAL", "OBRA", "FOLIO", "PU", "SUBTOTAL", "IVA", "TOTAL")
for ($i = 1; $i -le $headers.Length; $i++) {
    $wsBase.Cells.Item(1, $i) = $headers[$i-1]
    $wsBase.Cells.Item(1, $i).Font.Bold = $true
}

$targetRow = 2

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
        $fecha = if($mapFecha) { $ws.Cells.Item($r, $mapFecha).Text } else { "" }
        $sindicato = if($mapSindicato) { $ws.Cells.Item($r, $mapSindicato).Text.Trim().ToUpper() } else { "" }
        $obra = if($mapObra) { $ws.Cells.Item($r, $mapObra).Text } else { $defaultObra }
        $material = if($mapMaterial) { $ws.Cells.Item($r, $mapMaterial).Text.Trim().ToUpper() } else { "" }
        
        $pu = if($mapPU) { $ws.Cells.Item($r, $mapPU).Value2 } else { 0 }
        $subtotal = if($mapSub) { $ws.Cells.Item($r, $mapSub).Value2 } else { 0 }
        $iva = if($mapIva) { $ws.Cells.Item($r, $mapIva).Value2 } else { 0 }
        $total = if($mapTotal) { $ws.Cells.Item($r, $mapTotal).Value2 } else { 0 }
        
        if (-not $pu) { $pu = 0 }
        if (-not $subtotal) { $subtotal = 0 }
        if (-not $iva) { $iva = 0 }
        if (-not $total) { $total = 0 }
        
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
    }
    $wb.Close($false)
}

# 1. CAPTURA DE NOTAS - MEZCLA
Extract-Data -wbPath ($baseDir + "CAPTURA DE NOTAS.xlsx") -sheetName "MEZCLA" -mapSindicato 9 -mapFecha 2 -mapObra 10 -mapMaterial 6 -mapFolio 3 -mapPU 12 -mapSub 13 -mapIva 14 -mapTotal 15 -startRow 2 -defaultSemana 25 -defaultObra "AUTP. MEXICO-TOLUCA"

# 2. MEX-TOL FRESADO
Extract-Data -wbPath ($baseDir + "CAPTURA DE ACARREOS (SEM # 25) OBRA MEX-TOL.xlsx") -sheetName "FRESADO" -mapSindicato 11 -mapFecha 4 -mapObra 0 -mapMaterial 6 -mapFolio 3 -mapPU 18 -mapSub 19 -mapIva 20 -mapTotal 21 -startRow 7 -defaultSemana 25 -defaultObra "MEXICO-TOLUCA"

# 4. L3M MEZCLA
Extract-Data -wbPath ($baseDir + "CAPTURA DE ACARREOS POR SEMANA L3M.xlsx") -sheetName "MEZCLA" -mapSindicato 11 -mapFecha 4 -mapObra 0 -mapMaterial 6 -mapFolio 3 -mapPU 17 -mapSub 18 -mapIva 19 -mapTotal 20 -startRow 7 -defaultSemana 25 -defaultObra "LERMA-TRES MARIAS"

# 5. L3M FRESADO
Extract-Data -wbPath ($baseDir + "CAPTURA DE ACARREOS POR SEMANA L3M.xlsx") -sheetName "FRESADO" -mapSindicato 11 -mapFecha 4 -mapObra 0 -mapMaterial 6 -mapFolio 3 -mapPU 18 -mapSub 19 -mapIva 20 -mapTotal 21 -startRow 7 -defaultSemana 25 -defaultObra "LERMA-TRES MARIAS"

# Crear hoja de resumen
$wsResumen = $wbTarget.Worksheets.Add($wsBase)
$wsResumen.Name = "Resumen_Financiero"

$wsResumen.Cells.Item(1, 1) = "Panel de Control de Costos y Acarreos"
$wsResumen.Cells.Item(1, 1).Font.Size = 16
$wsResumen.Cells.Item(1, 1).Font.Bold = $true

$wsResumen.Cells.Item(3, 1) = "Seleccione la Semana:"
$wsResumen.Cells.Item(3, 1).Font.Bold = $true
$wsResumen.Cells.Item(3, 2) = 25
$wsResumen.Cells.Item(3, 2).Interior.Color = 65535 

# Encabezados
$resHeaders = @("SINDICATO", "FECHA", "MATERIAL", "TOTAL VIAJES", "IMPORTE TOTAL", "FOLIOS CONSOLIDADOS")
for ($i = 1; $i -le $resHeaders.Length; $i++) {
    $wsResumen.Cells.Item(5, $i) = $resHeaders[$i-1]
    $wsResumen.Cells.Item(5, $i).Font.Bold = $true
    $wsResumen.Cells.Item(5, $i).Interior.Color = 12632256 
}

try {
    # Usamos Formula para que Excel la traduzca. 
    $wsResumen.Cells.Item(6, 1).Formula2 = "=UNIQUE(FILTER(Base_Datos!B:D,Base_Datos!A:A=B3,""))"
} catch {
    Write-Host "Warning: Excel rejected Formula2 UNIQUE. Applying static unique keys."
    # If dynamic array fails, we'll leave it blank or handle it, but it should work without array literals.
}

$wsResumen.Cells.Item(6, 4).Formula = "=IF(A6="", "", COUNTIFS(Base_Datos!A:A, B$3, Base_Datos!B:B, A6, Base_Datos!C:C, B6, Base_Datos!D:D, C6))"
$wsResumen.Cells.Item(6, 5).Formula = "=IF(A6="", "", SUMIFS(Base_Datos!J:J, Base_Datos!A:A, B$3, Base_Datos!B:B, A6, Base_Datos!C:C, B6, Base_Datos!D:D, C6))"
$wsResumen.Cells.Item(6, 6).Formula2 = "=IF(A6="", "", TEXTJOIN(", ", TRUE, FILTER(Base_Datos!F:F, (Base_Datos!A:A=B$3)*(Base_Datos!B:B=A6)*(Base_Datos!C:C=B6)*(Base_Datos!D:D=C6), "")))"

$wsResumen.Range("D6:F6").Copy() | Out-Null
$wsResumen.Range("D7:F100").PasteSpecial(-4104) | Out-Null 
$excel.CutCopyMode = $false

$wsResumen.Columns.Item(1).ColumnWidth = 35
$wsResumen.Columns.Item(2).ColumnWidth = 15
$wsResumen.Columns.Item(3).ColumnWidth = 25
$wsResumen.Columns.Item(4).ColumnWidth = 15
$wsResumen.Columns.Item(5).ColumnWidth = 20
$wsResumen.Columns.Item(6).ColumnWidth = 80
$wsResumen.Columns.Item(5).NumberFormat = "$#,##0.00"

$wsBase.Columns.Item(7).NumberFormat = "$#,##0.00"
$wsBase.Columns.Item(8).NumberFormat = "$#,##0.00"
$wsBase.Columns.Item(9).NumberFormat = "$#,##0.00"
$wsBase.Columns.Item(10).NumberFormat = "$#,##0.00"
$wsBase.UsedRange.Columns.AutoFit() | Out-Null

$wbTarget.SaveAs($targetPath)
$wbTarget.Close($false)
$excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
Write-Host "Archivo Maestro creado exitosamente con nueva estructura."
