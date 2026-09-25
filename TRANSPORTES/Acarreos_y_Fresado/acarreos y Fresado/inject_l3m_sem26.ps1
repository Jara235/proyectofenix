$ErrorActionPreference = 'Stop'
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

$baseDir = "c:\Users\JOSE\Desktop\Proyecto fenix\acarreos y Fresado\"
$targetPath = $baseDir + "GC-MAT-1.0_Maestro_Consolidado_V12.xlsx"

function Format-DateString {
    param($val)
    if ([string]::IsNullOrWhiteSpace($val)) { return "" }
    try { return [DateTime]::ParseExact($val, "dd/MM/yyyy", $null).ToString("dd/MM/yyyy") } catch {}
    return $val
}

$wbTarget = $excel.Workbooks.Open($targetPath)
$wsBase = $wbTarget.Worksheets.Item("Base_Datos")
$lastRow = $wsBase.UsedRange.Rows.Count
$newRow = $lastRow + 1
Write-Host "Iniciando insercion en fila: $newRow"

# FRESADO
$txtF = Get-Content ($baseDir + "l3m_sem26_fresado.txt") -Encoding UTF8
$addedF = 0
foreach ($line in $txtF) {
    $parts = $line -split '\s+'
    if ($parts.Count -lt 11) { continue }
    $sem = $parts[0]
    $folio = $parts[2]
    $fecha = Format-DateString $parts[3]
    $mat = $parts[5]
    $placa = $parts[6]
    $cap = $parts[7]
    
    # El resto es complicado por los espacios en SINDICATO. 
    # Buscamos Sindicato como "EMULSIONES Y ASFALTOS JORGE"
    $sind = "EMULSIONES Y ASFALTOS JORGE"
    
    $cat = "FRESADO"
    if ($mat -match "LIMPIEZA") { $cat = "FRESADO" }
    
    $wsBase.Cells.Item($newRow, 1) = $sem
    $wsBase.Cells.Item($newRow, 2) = $fecha
    $wsBase.Cells.Item($newRow, 3) = $folio
    $wsBase.Cells.Item($newRow, 4) = $sind
    $wsBase.Cells.Item($newRow, 5) = "Lerma - Tres Marías"
    $wsBase.Cells.Item($newRow, 6) = $mat
    $wsBase.Cells.Item($newRow, 7) = $placa
    $wsBase.Cells.Item($newRow, 9) = $cap
    $wsBase.Cells.Item($newRow, 11) = 0
    $wsBase.Cells.Item($newRow, 12) = 0
    $wsBase.Cells.Item($newRow, 13) = 0
    $wsBase.Cells.Item($newRow, 14) = 0
    $wsBase.Cells.Item($newRow, 15) = $cat
    
    $newRow++; $addedF++
}

# MEZCLA
$txtM = Get-Content ($baseDir + "l3m_sem26_mezcla.txt") -Encoding UTF8
$addedM = 0
foreach ($line in $txtM) {
    $parts = $line -split '\s+'
    if ($parts.Count -lt 12) { continue }
    $sem = $parts[0]
    $folio = $parts[2]
    $fecha = Format-DateString $parts[3]
    
    # "1 PROTOCOLO AMAAC III"
    $mat = "PROTOCOLO AMAAC III"
    # Placa is after III
    # Let's find III index
    $idxIII = 0
    for ($i=0; $i -lt $parts.Count; $i++) { if ($parts[$i] -eq "III") { $idxIII = $i; break } }
    
    $placa = $parts[$idxIII + 1]
    $cap = $parts[$idxIII + 2]
    
    $sind = "EMULSIONES Y ASFALTOS JORGE"
    $cat = "MEZCLA"
    
    $wsBase.Cells.Item($newRow, 1) = $sem
    $wsBase.Cells.Item($newRow, 2) = $fecha
    $wsBase.Cells.Item($newRow, 3) = $folio
    $wsBase.Cells.Item($newRow, 4) = $sind
    $wsBase.Cells.Item($newRow, 5) = "Lerma - Tres Marías"
    $wsBase.Cells.Item($newRow, 6) = $mat
    $wsBase.Cells.Item($newRow, 7) = $placa
    $wsBase.Cells.Item($newRow, 9) = $cap
    $wsBase.Cells.Item($newRow, 11) = 0
    $wsBase.Cells.Item($newRow, 12) = 0
    $wsBase.Cells.Item($newRow, 13) = 0
    $wsBase.Cells.Item($newRow, 14) = 0
    $wsBase.Cells.Item($newRow, 15) = $cat
    
    $newRow++; $addedM++
}

# Refrescar
foreach ($sh in $wbTarget.Worksheets) {
    foreach ($pvt in $sh.PivotTables()) {
        try { $pvt.PivotCache().Refresh() } catch {}
    }
}

$wbTarget.Save()
$wbTarget.Close($false)
$excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
Write-Host "Inyectados: Fresado=$addedF, Mezcla=$addedM. Total=$($addedF+$addedM)"
