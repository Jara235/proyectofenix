$ErrorActionPreference = 'Stop'
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

$targetPath = "c:\Users\JOSE\Desktop\Proyecto fenix\acarreos y Fresado\GC-MAT-1.0_Maestro_Consolidado_V12.xlsx"
$wbTarget = $excel.Workbooks.Open($targetPath)

# Listar todas las hojas
Write-Host "=== Hojas en el archivo ==="
foreach ($sh in $wbTarget.Worksheets) { Write-Host "  $($sh.Name)" }

$wsBase = $wbTarget.Worksheets.Item("Base_Datos")
$lastRow = $wsBase.UsedRange.Rows.Count
Write-Host "Filas: $lastRow"

# Verificar pivot tables en Dash_Mezcla
$wsMezcla = $wbTarget.Worksheets.Item("Dash_Mezcla")
Write-Host "PT en Dash_Mezcla: $($wsMezcla.PivotTables().Count)"
foreach ($pvt in $wsMezcla.PivotTables()) {
    Write-Host "  $($pvt.Name) => source: $($pvt.PivotCache().SourceData)"
}

# Agregar Dash_Agua si no existe
$aguaExists = $false
foreach ($sh in $wbTarget.Worksheets) {
    if ($sh.Name -eq "Dash_Agua") { $aguaExists = $true }
}
if (-not $aguaExists) {
    $wsBaseRef = $wbTarget.Worksheets.Item("Base_Datos")
    $wsAgua = $wbTarget.Worksheets.Add($wsBaseRef)
    $wsAgua.Name = "Dash_Agua"
    $wsAgua.Cells.Item(1,2) = "PIPAS DE AGUA"
    $wsAgua.Cells.Item(1,2).Font.Bold = $true
    $wsAgua.Cells.Item(3,2) = "Se llenará al capturar pipas con CATEGORIA=AGUA en Base_Datos"
    $wsAgua.Cells.Item(3,2).Font.Italic = $true

    $srcRange = $wsBase.Range("A1:O" + $lastRow)
    $pc = $wbTarget.PivotCaches().Create(1, $srcRange, 6)
    $ptA = $pc.CreatePivotTable("Dash_Agua!R6C2","PT_Agua")
    $ptA.PivotFields("FECHA").Orientation = 1
    $ptA.PivotFields("OBRA").Orientation = 1
    $ptA.PivotFields("SINDICATO").Orientation = 1
    $ptA.AddDataField($ptA.PivotFields("FOLIO"),"Viajes Agua",-4112) | Out-Null
    $ptA.PivotFields("CATEGORIA").Orientation = 3
    try { $ptA.PivotFields("CATEGORIA").CurrentPage = "AGUA" } catch {}
    $ptA.PivotFields("SEMANA").Orientation = 3
    $ptA.TableStyle2 = "PivotStyleMedium14"
    $ptA.RowAxisLayout(1); $ptA.HasAutoFormat = $false

    $ptAS = $pc.CreatePivotTable("Dash_Agua!R6C10","PT_Agua_Sind")
    $ptAS.PivotFields("SINDICATO").Orientation = 1
    $ptAS.AddDataField($ptAS.PivotFields("FOLIO"),"Viajes Tot Agua",-4112) | Out-Null
    $ptAS.PivotFields("CATEGORIA").Orientation = 3
    try { $ptAS.PivotFields("CATEGORIA").CurrentPage = "AGUA" } catch {}
    $ptAS.PivotFields("SEMANA").Orientation = 3
    $ptAS.TableStyle2 = "PivotStyleMedium9"
    $ptAS.RowAxisLayout(1); $ptAS.HasAutoFormat = $false
    Write-Host "Dash_Agua creada"
}

# Verificar que Mezcla,Fresado,Total tienen el range correcto
$srcRange = $wsBase.Range("A1:O" + $lastRow)
$newPC = $wbTarget.PivotCaches().Create(1, $srcRange, 6)

foreach ($sname in @("Dash_Mezcla","Dash_Fresado","Dash_Total")) {
    $sh = $wbTarget.Worksheets.Item($sname)
    foreach ($pvt in $sh.PivotTables()) {
        try {
            $pvt.ChangePivotCache($newPC)
            $pvt.PivotCache().Refresh()
            Write-Host "OK: $sname/$($pvt.Name) => $($pvt.PivotCache().SourceData)"
        } catch { Write-Host "ERR $sname/$($pvt.Name): $_" }
    }
}

$wbTarget.Save()
$wbTarget.Close($false)
$excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
Write-Host "COMPLETADO"
