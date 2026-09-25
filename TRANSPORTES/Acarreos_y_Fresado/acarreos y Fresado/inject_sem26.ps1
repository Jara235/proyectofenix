$ErrorActionPreference = 'Stop'
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

$baseDir = "c:\Users\JOSE\Desktop\Proyecto fenix\acarreos y Fresado\"
$targetPath = $baseDir + "GC-MAT-1.0_Maestro_Consolidado_V12.xlsx"

function Format-DateString {
    param($val)
    if ([string]::IsNullOrWhiteSpace($val)) { return "" }
    if ($val -match '^\d{5}$') {
        try { return [DateTime]::FromOADate([double]$val).ToString("dd/MM/yyyy") } catch {}
    }
    try { return [DateTime]::Parse($val).ToString("dd/MM/yyyy") } catch {}
    return $val
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
        $sub = $pu * 1
        $iva = $sub * 0.16
        return @{ PU=$pu; Subtotal=$sub; IVA=$iva; Total=($sub+$iva) }
    }
    return @{ PU=[double]$fallbackPU; Subtotal=[double]$fallbackSub; IVA=[double]$fallbackIva; Total=[double]$fallbackTotal }
}

# Abrir archivo destino V12
$wbTarget = $excel.Workbooks.Open($targetPath)
$wsBase = $wbTarget.Worksheets.Item("Base_Datos")

# Encontrar ultima fila en Base_Datos
$lastExistingRow = $wsBase.UsedRange.Rows.Count
Write-Host "Base_Datos ultima fila existente: $lastExistingRow"

$newRow = $lastExistingRow + 1

# === FUENTE 1: L3M FRESADO ===
$wb1 = $excel.Workbooks.Open($baseDir + "CAPTURA DE ACARREOS POR SEMANA L3M.xlsx")
$ws1 = $wb1.Worksheets.Item("FRESADO")
$lastR1 = $ws1.UsedRange.Rows.Count
$added1 = 0

for ($r = 7; $r -le $lastR1; $r++) {
    $sem   = $ws1.Cells.Item($r, 1).Text.Trim()
    $folio = $ws1.Cells.Item($r, 3).Text.Trim()
    $sind  = $ws1.Cells.Item($r, 11).Text.Trim().ToUpper()

    if ([string]::IsNullOrWhiteSpace($folio)) { continue }
    if ($folio -match "FOLIO|TOTAL|SEM") { continue }

    $rawFecha = $ws1.Cells.Item($r, 4).Value2
    if ($null -eq $rawFecha) { $rawFecha = $ws1.Cells.Item($r, 4).Text }
    $fecha    = Format-DateString -val $rawFecha

    $material  = $ws1.Cells.Item($r, 6).Text.Trim().ToUpper()
    $placa     = $ws1.Cells.Item($r, 7).Text.Trim()
    $capacidad = $ws1.Cells.Item($r, 8).Text.Trim()
    $operador  = $ws1.Cells.Item($r, 10).Text.Trim()
    $obs       = $ws1.Cells.Item($r, 17).Text.Trim()
    $puRaw     = $ws1.Cells.Item($r, 18).Value2
    $subRaw    = $ws1.Cells.Item($r, 19).Value2
    $ivaRaw    = $ws1.Cells.Item($r, 20).Value2
    $totRaw    = $ws1.Cells.Item($r, 21).Value2

    # Obra para MEX-TOL = MEXICO-TOLUCA, L3M = Lerma - Tres Marias
    $obra = "LERMA - TRES MARIAS"
    
    # Categoria
    $cat = "FRESADO"
    if ($material -match "CARPETA|MEZCLA|ASFALTO|PROTOCOLO") { $cat = "MEZCLA" }

    # Normalizar sindicato - Mexico-Toluca queda como COSUM TOLUCA para verificar
    if ($sind -match "^COSUM$" -or $sind -match "^COSUM TOLUCA$" -or $sind -match "^COSUM-TOLUCA$") {
        $sind = "COSUM TOLUCA"
    } elseif ($sind -eq "" -or $sind -match "MEXICO|MEX") {
        $sind = "COSUM TOLUCA"
    }

    $prices = Calculate-Prices -sindicato $sind -categoria $cat -obra $obra -fallbackPU $puRaw -fallbackSub $subRaw -fallbackIva $ivaRaw -fallbackTotal $totRaw

    $wsBase.Cells.Item($newRow, 1)  = if($sem -ne "") { $sem } else { 25 }
    $wsBase.Cells.Item($newRow, 2)  = $fecha
    $wsBase.Cells.Item($newRow, 3)  = $folio
    $wsBase.Cells.Item($newRow, 4)  = $sind
    $wsBase.Cells.Item($newRow, 5)  = $obra
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
    $newRow++
    $added1++
}
$wb1.Close($false)
Write-Host "L3M Fresado: $added1 filas agregadas"

# === FUENTE 2: SEM 26 MEX-TOL (si existe) ===
$file26 = $baseDir + "CAPTURA DE ACARREOS (SEM # 26) OBRA MEX-TOL.xlsx"
$added2 = 0
if (Test-Path $file26) {
    $wb2 = $excel.Workbooks.Open($file26)
    Write-Host "Archivo SEM 26 MEX-TOL encontrado"
    foreach ($sh in $wb2.Worksheets) {
        $ws2 = $sh
        $lastR2 = $ws2.UsedRange.Rows.Count
        Write-Host "  Sheet: $($sh.Name), rows: $lastR2"
        for ($r = 7; $r -le $lastR2; $r++) {
            $folio = $ws2.Cells.Item($r, 3).Text.Trim()
            $sind  = $ws2.Cells.Item($r, 11).Text.Trim().ToUpper()
            if ([string]::IsNullOrWhiteSpace($folio)) { continue }
            if ($folio -match "FOLIO|TOTAL|SEM") { continue }

            $rawFecha = $ws2.Cells.Item($r, 4).Value2
            if ($null -eq $rawFecha) { $rawFecha = $ws2.Cells.Item($r, 4).Text }
            $fecha    = Format-DateString -val $rawFecha
            $material  = $ws2.Cells.Item($r, 6).Text.Trim().ToUpper()
            $placa     = $ws2.Cells.Item($r, 7).Text.Trim()
            $capacidad = $ws2.Cells.Item($r, 8).Text.Trim()
            $operador  = $ws2.Cells.Item($r, 10).Text.Trim()
            $obs       = $ws2.Cells.Item($r, 17).Text.Trim()
            $puRaw     = $ws2.Cells.Item($r, 18).Value2
            $subRaw    = $ws2.Cells.Item($r, 19).Value2
            $ivaRaw    = $ws2.Cells.Item($r, 20).Value2
            $totRaw    = $ws2.Cells.Item($r, 21).Value2

            $obra = "MEXICO-TOLUCA"
            $cat = "FRESADO"
            if ($material -match "CARPETA|MEZCLA|ASFALTO|PROTOCOLO") { $cat = "MEZCLA" }

            # Mexico-Toluca queda como COSUM TOLUCA hasta verificar
            if ($sind -match "^COSUM$" -or $sind -match "^COSUM TOLUCA$" -or $sind -match "^COSUM-TOLUCA$" -or $sind -eq "") {
                $sind = "COSUM TOLUCA"
            }

            $prices = Calculate-Prices -sindicato $sind -categoria $cat -obra $obra -fallbackPU $puRaw -fallbackSub $subRaw -fallbackIva $ivaRaw -fallbackTotal $totRaw

            $wsBase.Cells.Item($newRow, 1)  = 26
            $wsBase.Cells.Item($newRow, 2)  = $fecha
            $wsBase.Cells.Item($newRow, 3)  = $folio
            $wsBase.Cells.Item($newRow, 4)  = $sind
            $wsBase.Cells.Item($newRow, 5)  = $obra
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
            $newRow++
            $added2++
        }
    }
    $wb2.Close($false)
    Write-Host "SEM 26 MEX-TOL: $added2 filas agregadas"
} else {
    Write-Host "Archivo SEM 26 MEX-TOL NO encontrado en la carpeta"
}

# Formatear columnas de precio
$wsBase.Columns.Item(11).NumberFormat = "$#,##0.00"
$wsBase.Columns.Item(12).NumberFormat = "$#,##0.00"
$wsBase.Columns.Item(13).NumberFormat = "$#,##0.00"
$wsBase.Columns.Item(14).NumberFormat = "$#,##0.00"

# Actualizar todas las tablas dinamicas
foreach ($pt in $wbTarget.Worksheets) {
    foreach ($pvt in $pt.PivotTables()) {
        $pvt.PivotCache().Refresh()
    }
}

$wbTarget.Save()
$wbTarget.Close($false)
$excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
Write-Host "COMPLETADO: $($added1 + $added2) filas nuevas en Base_Datos V12"
