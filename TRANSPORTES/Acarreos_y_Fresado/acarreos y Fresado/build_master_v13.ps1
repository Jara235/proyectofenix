$ErrorActionPreference = 'Stop'
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

$baseDir = "c:\Users\JOSE\Desktop\Proyecto fenix\acarreos y Fresado\"
$targetPath = $baseDir + "GC-MAT-1.0_Maestro_Consolidado_V13.xlsx"

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
    if ($v -match "MXICO" -or $v -match "MÃ‰XICO" -or $v -match "MEXICO") {
        return "MEXICO-TOLUCA"
    }
    return $val
}

function Calculate-Prices {
    param($sindicato, $categoria, $obraRaw, $viajes, $fallbackPu, $fallbackSub, $fallbackIva, $fallbackTotal)
    $pu = 0
    $obra = $obraRaw.ToUpper()
    $sind = $sindicato.ToUpper()
    
    if ($sind -match "COSUM" -or $sind -match "OBRAS") {
        if ($categoria -eq "MEZCLA") {
            $pu = 2850
        } elseif ($categoria -eq "FRESADO") {
            if ($obra -match "HUIXQUILUCAN") {
                $pu = 2500
            } else {
                $pu = 2000
            }
        }
    }
    
    if ($pu -gt 0) {
        $subtotal = $pu * $viajes
        $iva = $subtotal * 0.16
        $total = $subtotal + $iva
        return @{ PU = $pu; Subtotal = $subtotal; IVA = $iva; Total = $total }
    } else {
        if (-not $fallbackPu) { $fallbackPu = 0 }
        if (-not $fallbackSub) { $fallbackSub = 0 }
        if (-not $fallbackIva) { $fallbackIva = 0 }
        if (-not $fallbackTotal) { $fallbackTotal = 0 }
        return @{ PU = $fallbackPu; Subtotal = $fallbackSub; IVA = $fallbackIva; Total = $fallbackTotal }
    }
}

# --- HOJAS DE DASHBOARD ---
$wsMezcla = $wbTarget.Worksheets.Item(1)
$wsMezcla.Name = "Dash_Mezcla"

$wsFresado = $wbTarget.Worksheets.Add( $wsMezcla )
$wsFresado.Name = "Dash_Fresado"

$wsTotal = $wbTarget.Worksheets.Add( $wsFresado )
$wsTotal.Name = "Dash_Total"

# --- HOJA BASE DE DATOS ---
$wsBase = $wbTarget.Worksheets.Add()
$wsBase.Name = "Base_Datos"

$headersBD = @("SEMANA", "FECHA", "FOLIO", "SINDICATO", "OBRA", "MATERIAL", "PLACA", "OPERADOR", "CAPACIDAD", "OBSERVACIONES", "PU", "SUBTOTAL", "IVA", "TOTAL", "CATEGORIA")
for ($i = 1; $i -le $headersBD.Length; $i++) {
    $wsBase.Cells.Item(1, $i) = $headersBD[$i-1]
    $wsBase.Cells.Item(1, $i).Font.Bold = $true
    $wsBase.Cells.Item(1, $i).Interior.Color = 14277081
}

$global:targetRow = 2

# Extraccion Excel
function Extract-Data {
    param($wbPath, $sheetName, $mapSindicato, $mapFecha, $mapObra, $mapMaterial, $mapFolio, $mapPlaca, $mapOperador, $mapCapacidad, $mapObs, $mapPU, $mapSub, $mapIva, $mapTotal, $startRow, $defaultSemana, $defaultObra)
    $wb = $excel.Workbooks.Open($wbPath)
    $ws = $wb.Worksheets.Item($sheetName)
    $lastRow = $ws.UsedRange.Rows.Count
    
    for ($r = $startRow; $r -le $lastRow; $r++) {
        $folio = $ws.Cells.Item($r, $mapFolio).Text.Trim()
        $sindicato = if($mapSindicato) { $ws.Cells.Item($r, $mapSindicato).Text.Trim().ToUpper() } else { "" }
        $material = if($mapMaterial) { $ws.Cells.Item($r, $mapMaterial).Text.Trim().ToUpper() } else { "" }
        $observaciones = if($mapObs) { $ws.Cells.Item($r, $mapObs).Text.Trim() } else { "" }
        
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
        
        $puRaw = if($mapPU) { $ws.Cells.Item($r, $mapPU).Value2 } else { 0 }
        $subRaw = if($mapSub) { $ws.Cells.Item($r, $mapSub).Value2 } else { 0 }
        $ivaRaw = if($mapIva) { $ws.Cells.Item($r, $mapIva).Value2 } else { 0 }
        $totRaw = if($mapTotal) { $ws.Cells.Item($r, $mapTotal).Value2 } else { 0 }
        
        if ($isCancelled) {
            $sindicato = "CANCELADAS"
            $categoria = "CANCELADAS"
            $material = "CANCELADO"
            if ([string]::IsNullOrWhiteSpace($folio)) { $folio = "N/A" }
            $prices = @{ PU = 0; Subtotal = 0; IVA = 0; Total = 0 }
        } else {
            $categoria = "OTROS"
            if ($material -match "CARPETA" -or $material -match "MEZCLA" -or $material -match "PROTOCOLO" -or $material -match "ASFALTO") {
                $categoria = "MEZCLA"
            } elseif ($material -match "FRESADO" -or $material -match "LIMPIEZA" -or $material -match "RETIRO") {
                $categoria = "FRESADO"
            } else {
                if ($sheetName -match "MEZCLA" -or $sheetName -match "CARPETA") { $categoria = "MEZCLA" }
                else { $categoria = "FRESADO" }
            }
            $prices = Calculate-Prices -sindicato $sindicato -categoria $categoria -obraRaw $obra -viajes 1 -fallbackPu $puRaw -fallbackSub $subRaw -fallbackIva $ivaRaw -fallbackTotal $totRaw
        }
        
        $wsBase.Cells.Item($global:targetRow, 1) = $defaultSemana
        $wsBase.Cells.Item($global:targetRow, 2) = $fecha
        $wsBase.Cells.Item($global:targetRow, 3) = $folio
        $wsBase.Cells.Item($global:targetRow, 4) = $sindicato
        $wsBase.Cells.Item($global:targetRow, 5) = $obra
        $wsBase.Cells.Item($global:targetRow, 6) = $material
        $wsBase.Cells.Item($global:targetRow, 7) = $placa
        $wsBase.Cells.Item($global:targetRow, 8) = $operador
        $wsBase.Cells.Item($global:targetRow, 9) = $capacidad
        $wsBase.Cells.Item($global:targetRow, 10) = $observaciones
        $wsBase.Cells.Item($global:targetRow, 11) = $prices.PU
        $wsBase.Cells.Item($global:targetRow, 12) = $prices.Subtotal
        $wsBase.Cells.Item($global:targetRow, 13) = $prices.IVA
        $wsBase.Cells.Item($global:targetRow, 14) = $prices.Total
        $wsBase.Cells.Item($global:targetRow, 15) = $categoria
        $global:targetRow++
    }
    $wb.Close($false)
}

# Run extractions
Extract-Data -wbPath ($baseDir + "CAPTURA DE NOTAS.xlsx") -sheetName "MEZCLA" -mapSindicato 9 -mapFecha 2 -mapObra 10 -mapMaterial 6 -mapFolio 3 -mapPlaca 4 -mapOperador 5 -mapCapacidad 8 -mapObs 11 -mapPU 12 -mapSub 13 -mapIva 14 -mapTotal 15 -startRow 2 -defaultSemana 25 -defaultObra "MEXICO-TOLUCA"
Extract-Data -wbPath ($baseDir + "CAPTURA DE ACARREOS (SEM # 25) OBRA MEX-TOL.xlsx") -sheetName "FRESADO" -mapSindicato 11 -mapFecha 4 -mapObra 0 -mapMaterial 6 -mapFolio 3 -mapPlaca 7 -mapOperador 10 -mapCapacidad 8 -mapObs 17 -mapPU 18 -mapSub 19 -mapIva 20 -mapTotal 21 -startRow 7 -defaultSemana 25 -defaultObra "MEXICO-TOLUCA"
Extract-Data -wbPath ($baseDir + "CAPTURA DE ACARREOS POR SEMANA L3M.xlsx") -sheetName "MEZCLA" -mapSindicato 11 -mapFecha 4 -mapObra 0 -mapMaterial 6 -mapFolio 3 -mapPlaca 7 -mapOperador 10 -mapCapacidad 8 -mapObs 17 -mapPU 17 -mapSub 18 -mapIva 19 -mapTotal 20 -startRow 7 -defaultSemana 25 -defaultObra "Lerma - Tres Marías"
Extract-Data -wbPath ($baseDir + "CAPTURA DE ACARREOS POR SEMANA L3M.xlsx") -sheetName "FRESADO" -mapSindicato 11 -mapFecha 4 -mapObra 0 -mapMaterial 6 -mapFolio 3 -mapPlaca 7 -mapOperador 10 -mapCapacidad 8 -mapObs 17 -mapPU 18 -mapSub 19 -mapIva 20 -mapTotal 21 -startRow 7 -defaultSemana 25 -defaultObra "Lerma - Tres Marías"

# Extraccion OCR PDFs
function Extract-PdfData {
    param($txtFile)
    if (Test-Path $txtFile) {
        $lines = Get-Content $txtFile -Encoding UTF8
        foreach ($line in $lines) {
            if ([string]::IsNullOrWhiteSpace($line)) { continue }
            if ($line -match "^(?<sem>\d+)\s+(?<no>\d+)\s+(?<folio>\w+)\s+(?<fecha>\d{2}/\d{2}/\d{4})\s+(?<viajes>\d+)\s+(?<material>\w+)\s+(?<placa>[\w\d]+)\s+(?<capacidad>\d+)\s+(?<peso>[\d\.]+)\s+(?<operador>.+?)\s+(?<sindicato>COSUM TOLUCA|OBRAS PUBLICAS)\s*(?<obs>.*)$") {
                $sem = $matches['sem']
                $fecha = $matches['fecha']
                $folio = $matches['folio']
                $sindicato = $matches['sindicato']
                $material = $matches['material']
                $placa = $matches['placa']
                $capacidad = $matches['capacidad']
                $operador = $matches['operador'].Trim()
                $obs = $matches['obs'].Trim()
                $viajes = [int]$matches['viajes']
                $obra = "BACHEO TOLUCA"
                
                $categoria = "OTROS"
                if ($material -match "CARPETA" -or $material -match "MEZCLA" -or $material -match "PROTOCOLO" -or $material -match "ASFALTO") { $categoria = "MEZCLA" }
                elseif ($material -match "FRESADO" -or $material -match "LIMPIEZA") { $categoria = "FRESADO" }
                else { $categoria = "MEZCLA" } # Por defecto los PDF son ASFALTO
                
                $prices = Calculate-Prices -sindicato $sindicato -categoria $categoria -obraRaw $obra -viajes $viajes -fallbackPu 0 -fallbackSub 0 -fallbackIva 0 -fallbackTotal 0
                
                $wsBase.Cells.Item($global:targetRow, 1) = $sem
                $wsBase.Cells.Item($global:targetRow, 2) = $fecha
                $wsBase.Cells.Item($global:targetRow, 3) = $folio
                $wsBase.Cells.Item($global:targetRow, 4) = $sindicato
                $wsBase.Cells.Item($global:targetRow, 5) = $obra
                $wsBase.Cells.Item($global:targetRow, 6) = $material
                $wsBase.Cells.Item($global:targetRow, 7) = $placa
                $wsBase.Cells.Item($global:targetRow, 8) = $operador
                $wsBase.Cells.Item($global:targetRow, 9) = $capacidad
                $wsBase.Cells.Item($global:targetRow, 10) = $obs
                $wsBase.Cells.Item($global:targetRow, 11) = $prices.PU
                $wsBase.Cells.Item($global:targetRow, 12) = $prices.Subtotal
                $wsBase.Cells.Item($global:targetRow, 13) = $prices.IVA
                $wsBase.Cells.Item($global:targetRow, 14) = $prices.Total
                $wsBase.Cells.Item($global:targetRow, 15) = $categoria
                $global:targetRow++
            }
        }
    }
}
Extract-PdfData -txtFile ($baseDir + "pdf_sem25.txt")
Extract-PdfData -txtFile ($baseDir + "pdf_sem26.txt")


# Tablas Dinamicas
$last = $global:targetRow - 1
$dataRange = "Base_Datos!R1C1:R" + $last + "C15"
$pc = $wbTarget.PivotCaches().Create(1, $dataRange, 6)

# == DASH MEZCLA ==
$wsMezcla.Cells.Item(1, 2) = "MEZCLA ASFÁLTICA"
$wsMezcla.Cells.Item(1, 2).Font.Bold = $true
$pt1 = $pc.CreatePivotTable("Dash_Mezcla!R6C2", "PT_Mezcla")
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

$pt1_s = $pc.CreatePivotTable("Dash_Mezcla!R6C10", "PT_Mezcla_Sind")
$pt1_s.PivotFields("SINDICATO").Orientation = 1
$df1_s1 = $pt1_s.AddDataField($pt1_s.PivotFields("FOLIO"), "Viajes Totales", -4112)
$df1_s2 = $pt1_s.AddDataField($pt1_s.PivotFields("PU"), "Total a Pagar", -4157)
$df1_s2.NumberFormat = "$#,##0.00"
$pt1_s.PivotFields("CATEGORIA").Orientation = 3
$pt1_s.PivotFields("CATEGORIA").CurrentPage = "MEZCLA"
$pt1_s.PivotFields("SEMANA").Orientation = 3

# == DASH FRESADO ==
$wsFresado.Cells.Item(1, 2) = "FRESADO"
$wsFresado.Cells.Item(1, 2).Font.Bold = $true
$pt2 = $pc.CreatePivotTable("Dash_Fresado!R6C2", "PT_Fresado")
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

$pt2_s = $pc.CreatePivotTable("Dash_Fresado!R6C10", "PT_Fresado_Sind")
$pt2_s.PivotFields("SINDICATO").Orientation = 1
$df2_s1 = $pt2_s.AddDataField($pt2_s.PivotFields("FOLIO"), "Viajes Totales ", -4112)
$df2_s2 = $pt2_s.AddDataField($pt2_s.PivotFields("PU"), "Total a Pagar ", -4157)
$df2_s2.NumberFormat = "$#,##0.00"
$pt2_s.PivotFields("CATEGORIA").Orientation = 3
$pt2_s.PivotFields("CATEGORIA").CurrentPage = "FRESADO"
$pt2_s.PivotFields("SEMANA").Orientation = 3

# == DASH TOTAL ==
$wsTotal.Cells.Item(1, 2) = "TOTAL GENERAL ACARREOS"
$wsTotal.Cells.Item(1, 2).Font.Bold = $true
$pt3 = $pc.CreatePivotTable("Dash_Total!R6C2", "PT_Total")
$pt3.PivotFields("FECHA").Orientation = 1
$pt3.PivotFields("OBRA").Orientation = 1
$pt3.PivotFields("SINDICATO").Orientation = 1
$df3_1 = $pt3.AddDataField($pt3.PivotFields("FOLIO"), "Viajes Totales", -4112)
$df3_2 = $pt3.AddDataField($pt3.PivotFields("PU"), "Costo Total Obra", -4157)
$df3_2.NumberFormat = "$#,##0.00"
$pt3.PivotFields("SEMANA").Orientation = 3

$pt3_s = $pc.CreatePivotTable("Dash_Total!R6C10", "PT_Total_Sind")
$pt3_s.PivotFields("SINDICATO").Orientation = 1
$df3_s1 = $pt3_s.AddDataField($pt3_s.PivotFields("FOLIO"), "Viajes Global ", -4112)
$df3_s2 = $pt3_s.AddDataField($pt3_s.PivotFields("PU"), "Pagar Global ", -4157)
$df3_s2.NumberFormat = "$#,##0.00"
$pt3_s.PivotFields("SEMANA").Orientation = 3

# Estilos
$pt1.TableStyle2 = "PivotStyleMedium9"; $pt1_s.TableStyle2 = "PivotStyleMedium14"
$pt2.TableStyle2 = "PivotStyleMedium9"; $pt2_s.TableStyle2 = "PivotStyleMedium14"
$pt3.TableStyle2 = "PivotStyleMedium14"; $pt3_s.TableStyle2 = "PivotStyleMedium9"

$pt1.RowAxisLayout(1); $pt1_s.RowAxisLayout(1)
$pt2.RowAxisLayout(1); $pt2_s.RowAxisLayout(1)
$pt3.RowAxisLayout(1); $pt3_s.RowAxisLayout(1)

$pt1.HasAutoFormat = $false; $pt1_s.HasAutoFormat = $false
$pt2.HasAutoFormat = $false; $pt2_s.HasAutoFormat = $false
$pt3.HasAutoFormat = $false; $pt3_s.HasAutoFormat = $false

# Formatos
$wsMezcla.Columns.Item(2).ColumnWidth = 15; $wsMezcla.Columns.Item(3).ColumnWidth = 25; $wsMezcla.Columns.Item(4).ColumnWidth = 20; $wsMezcla.Columns.Item(5).ColumnWidth = 15; $wsMezcla.Columns.Item(10).ColumnWidth = 20; $wsMezcla.Columns.Item(11).ColumnWidth = 15
$wsFresado.Columns.Item(2).ColumnWidth = 15; $wsFresado.Columns.Item(3).ColumnWidth = 25; $wsFresado.Columns.Item(4).ColumnWidth = 20; $wsFresado.Columns.Item(5).ColumnWidth = 15; $wsFresado.Columns.Item(10).ColumnWidth = 20; $wsFresado.Columns.Item(11).ColumnWidth = 15
$wsTotal.Columns.Item(2).ColumnWidth = 15; $wsTotal.Columns.Item(3).ColumnWidth = 25; $wsTotal.Columns.Item(4).ColumnWidth = 20; $wsTotal.Columns.Item(5).ColumnWidth = 15; $wsTotal.Columns.Item(10).ColumnWidth = 20; $wsTotal.Columns.Item(11).ColumnWidth = 15

$wsBase.Columns.Item(11).NumberFormat = "$#,##0.00"
$wsBase.Columns.Item(12).NumberFormat = "$#,##0.00"
$wsBase.Columns.Item(13).NumberFormat = "$#,##0.00"
$wsBase.Columns.Item(14).NumberFormat = "$#,##0.00"
$wsBase.UsedRange.Columns.AutoFit() | Out-Null
$wsBase.Range("A1:O1").AutoFilter() | Out-Null

$wsMezcla.Move($wsBase)
$wsFresado.Move($wsBase)
$wsTotal.Move($wsBase)

$wbTarget.SaveAs($targetPath)
$wbTarget.Close($false)
$excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
Write-Host "Archivo Maestro V13 (PDFs + Precios Motor + Tablas Sindicato) creado."



