$ErrorActionPreference = 'Stop'
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

$baseDir = "c:\Users\JOSE\Desktop\Proyecto fenix\acarreos y Fresado\"
$targetPath = $baseDir + "GC-MAT-1.0_Maestro_Consolidado_V12.xlsx"

function Format-DateString {
    param($val)
    if ([string]::IsNullOrWhiteSpace($val)) { return "" }
    if ("$val" -match '^\d{5}$') {
        try { return [DateTime]::FromOADate([double]$val).ToString("dd/MM/yyyy") } catch {}
    }
    try { return [DateTime]::Parse("$val").ToString("dd/MM/yyyy") } catch {}
    return "$val"
}

function Normalize-Sindicato {
    param($s)
    $s = $s.Trim().ToUpper()
    if ($s -match "^COSUM$" -or $s -match "^COSUM TOLUCA$" -or $s -match "^COSUM-TOLUCA$") { return "COSUM TOLUCA" }
    return $s
}

function Calculate-Prices {
    param($sindicato, $categoria, $obra, $fallbackPU, $fallbackSub, $fallbackIva, $fallbackTotal)
    $sind = $sindicato.ToUpper()
    $obraU = $obra.ToUpper()
    $pu = 0
    if ($sind -match "COSUM" -or $sind -match "OBRAS PUBLICAS") {
        if ($categoria -eq "MEZCLA") { $pu = 2850 }
        elseif ($categoria -eq "FRESADO") {
            if ($obraU -match "HUIXQUILUCAN") { $pu = 2500 } else { $pu = 2000 }
        }
    }
    if ($pu -gt 0) {
        $sub = $pu; $iva = $sub * 0.16
        return @{ PU=$pu; Subtotal=$sub; IVA=$iva; Total=($sub+$iva) }
    }
    return @{ PU=[double]$fallbackPU; Subtotal=[double]$fallbackSub; IVA=[double]$fallbackIva; Total=[double]$fallbackTotal }
}

$wbTarget = $excel.Workbooks.Open($targetPath)
$wsBase = $wbTarget.Worksheets.Item("Base_Datos")
$newRow = $wsBase.UsedRange.Rows.Count + 1
Write-Host "Iniciando desde fila: $newRow"

# =====================================================
# ARCHIVO 1: CAPTURA DE ACARREOS POR SEMANA L3M FRESADO.xlsx
# Cols: 1=SEM,2=NO,3=FOLIO,4=FECHA,5=VIAJES,6=MATERIAL,7=PLACAS,8=CAPACIDAD,9=PESO,10=OPERADOR,11=SINDICATO,12=KM INI,13=KM FIN,14=KM ACARREO,15=OBS
# No tiene columnas de precio => usar Motor de Precios
# =====================================================
$wb1 = $excel.Workbooks.Open($baseDir + "CAPTURA DE ACARREOS POR SEMANA L3M FRESADO.xlsx")
$added1 = 0
foreach ($sheetName in @("MEZCLA","FRESADO")) {
    try { $ws1 = $wb1.Worksheets.Item($sheetName) } catch { continue }
    $lastR = $ws1.UsedRange.Rows.Count
    $defaultCat = $sheetName  # MEZCLA o FRESADO
    $obraDefault = "LERMA - TRES MARIAS"

    for ($r = 7; $r -le $lastR; $r++) {
        $sem   = $ws1.Cells.Item($r, 1).Text.Trim()
        $folio = $ws1.Cells.Item($r, 3).Text.Trim()
        if ([string]::IsNullOrWhiteSpace($folio)) { continue }
        if ($folio -match "^FOLIO$|^TOTAL$|^SEM") { continue }
        if ($folio -notmatch "^\d+$") { continue }  # solo folios numericos

        $rawFecha = $ws1.Cells.Item($r, 4).Value2
        if ($null -eq $rawFecha) { $rawFecha = $ws1.Cells.Item($r, 4).Text }
        $fecha     = Format-DateString -val $rawFecha
        $material  = $ws1.Cells.Item($r, 6).Text.Trim().ToUpper()
        $placa     = $ws1.Cells.Item($r, 7).Text.Trim()
        $capacidad = $ws1.Cells.Item($r, 8).Text.Trim()
        $operador  = $ws1.Cells.Item($r, 10).Text.Trim()
        $sind      = Normalize-Sindicato $ws1.Cells.Item($r, 11).Text
        $obs       = $ws1.Cells.Item($r, 15).Text.Trim()

        $cat = $defaultCat
        if ($material -match "CARPETA|MEZCLA|ASFALTO|PROTOCOLO") { $cat = "MEZCLA" }
        elseif ($material -match "FRESADO|LIMPIEZA|RETIRO") { $cat = "FRESADO" }

        $prices = Calculate-Prices -sindicato $sind -categoria $cat -obra $obraDefault -fallbackPU 0 -fallbackSub 0 -fallbackIva 0 -fallbackTotal 0

        $wsBase.Cells.Item($newRow, 1)  = if($sem -ne "") { $sem } else { 25 }
        $wsBase.Cells.Item($newRow, 2)  = $fecha
        $wsBase.Cells.Item($newRow, 3)  = $folio
        $wsBase.Cells.Item($newRow, 4)  = $sind
        $wsBase.Cells.Item($newRow, 5)  = $obraDefault
        $wsBase.Cells.Item($newRow, 6)  = $material
        $wsBase.Cells.Item($newRow, 7)  = $placa
        $wsBase.Cells.Item($newRow, 8)  = $operador
        $wsBase.Cells.Item($newRow, 9)  = $capacidad
        $wsBase.Cells.Item($newRow, 10) = $obs
        $wsBase.Cells.Item($newRow, 11) = $prices.PU
        $wsBase.Cells.Item($newRow, 12) = $prices.Subtotal
        $wsBase.Cells.Item($newRow, 13) = $prices.IVA
        $wsBase.Cells.Item($newRow, 14) = $prices.Total
        $wsBase.Cells.Item($newRow, 15) = $cat
        $newRow++; $added1++
    }
    Write-Host "L3M FRESADO - Hoja $sheetName`: $added1 filas hasta ahora"
}
$wb1.Close($false)
Write-Host "L3M FRESADO TOTAL: $added1 filas"

# =====================================================
# ARCHIVO 2: CAPTURA DE ACARREOS (SEM # 26) OBRA MEX-TOL.xlsx
# Cols (start C2): 2=SEM,3=NO,4=FOLIO,5=FECHA,6=VIAJES,7=MATERIAL,8=PLACAS,9=CAPACIDAD,10=UNIDAD,11=OPERADOR,12=SINDICATO,13=KM INI,14=KM FIN,15=TIRO,16=CPO,17=CARRIL
# Sin columnas de precio => Motor de Precios. SINDICATO=COSUM => COSUM TOLUCA (para verificar)
# OBRA = MEXICO-TOLUCA
# =====================================================
$wb2 = $excel.Workbooks.Open($baseDir + "CAPTURA DE ACARREOS (SEM # 26) OBRA MEX-TOL.xlsx")
$added2 = 0
foreach ($sheetName in @("FRESADO","CARPETA")) {
    try { $ws2 = $wb2.Worksheets.Item($sheetName) } catch { continue }
    $lastR = $ws2.UsedRange.Rows.Count
    $obraDefault = "MEXICO-TOLUCA"
    $cat = if($sheetName -eq "CARPETA") { "MEZCLA" } else { "FRESADO" }

    for ($r = 7; $r -le $lastR; $r++) {
        $sem   = $ws2.Cells.Item($r, 2).Text.Trim()
        $folio = $ws2.Cells.Item($r, 4).Text.Trim()
        if ([string]::IsNullOrWhiteSpace($folio)) { continue }
        if ($folio -match "^FOLIO$|^TOTAL$|^SEM") { continue }
        if ($folio -notmatch "^\d+$") { continue }

        $rawFecha = $ws2.Cells.Item($r, 5).Value2
        if ($null -eq $rawFecha) { $rawFecha = $ws2.Cells.Item($r, 5).Text }
        $fecha     = Format-DateString -val $rawFecha
        $material  = $ws2.Cells.Item($r, 7).Text.Trim().ToUpper()
        $placa     = $ws2.Cells.Item($r, 8).Text.Trim()
        $capacidad = $ws2.Cells.Item($r, 9).Text.Trim()
        $operador  = $ws2.Cells.Item($r, 11).Text.Trim()
        $sindRaw   = $ws2.Cells.Item($r, 12).Text.Trim().ToUpper()

        # MEX-TOL: COSUM sin especificar => queda como COSUM TOLUCA para verificar
        $sind = Normalize-Sindicato $sindRaw

        $catFinal = $cat
        if ($material -match "CARPETA|MEZCLA|ASFALTO|PROTOCOLO") { $catFinal = "MEZCLA" }
        elseif ($material -match "FRESADO|LIMPIEZA|RETIRO") { $catFinal = "FRESADO" }

        $prices = Calculate-Prices -sindicato $sind -categoria $catFinal -obra $obraDefault -fallbackPU 0 -fallbackSub 0 -fallbackIva 0 -fallbackTotal 0

        $wsBase.Cells.Item($newRow, 1)  = if($sem -ne "") { $sem } else { 26 }
        $wsBase.Cells.Item($newRow, 2)  = $fecha
        $wsBase.Cells.Item($newRow, 3)  = $folio
        $wsBase.Cells.Item($newRow, 4)  = $sind
        $wsBase.Cells.Item($newRow, 5)  = $obraDefault
        $wsBase.Cells.Item($newRow, 6)  = $material
        $wsBase.Cells.Item($newRow, 7)  = $placa
        $wsBase.Cells.Item($newRow, 8)  = $operador
        $wsBase.Cells.Item($newRow, 9)  = $capacidad
        $wsBase.Cells.Item($newRow, 10) = ""
        $wsBase.Cells.Item($newRow, 11) = $prices.PU
        $wsBase.Cells.Item($newRow, 12) = $prices.Subtotal
        $wsBase.Cells.Item($newRow, 13) = $prices.IVA
        $wsBase.Cells.Item($newRow, 14) = $prices.Total
        $wsBase.Cells.Item($newRow, 15) = $catFinal
        $newRow++; $added2++
    }
    Write-Host "SEM 26 MEX-TOL - Hoja $sheetName`: $added2 filas hasta ahora"
}
$wb2.Close($false)
Write-Host "SEM 26 MEX-TOL TOTAL: $added2 filas"

# Formato moneda
$wsBase.Columns.Item(11).NumberFormat = "$#,##0.00"
$wsBase.Columns.Item(12).NumberFormat = "$#,##0.00"
$wsBase.Columns.Item(13).NumberFormat = "$#,##0.00"
$wsBase.Columns.Item(14).NumberFormat = "$#,##0.00"

# Actualizar tablas dinamicas
foreach ($sh in $wbTarget.Worksheets) {
    foreach ($pvt in $sh.PivotTables()) {
        try { $pvt.PivotCache().Refresh() } catch {}
    }
}

$wbTarget.Save()
$wbTarget.Close($false)
$excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
Write-Host "`nCOMPLETADO TOTAL: $($added1+$added2) filas nuevas agregadas a Base_Datos V12"
