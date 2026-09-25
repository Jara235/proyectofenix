# Detectar el problema exacto de las PT que fallan al cambiar cache
$ErrorActionPreference = 'Continue'
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

$targetPath = "c:\Users\JOSE\Desktop\Proyecto fenix\acarreos y Fresado\GC-MAT-1.0_Maestro_Consolidado_V12.xlsx"
$wbTarget = $excel.Workbooks.Open($targetPath)
$wsBase = $wbTarget.Worksheets.Item("Base_Datos")
$lastRow = $wsBase.UsedRange.Rows.Count

# Inspeccionar la PT que falla
$wsMezcla = $wbTarget.Worksheets.Item("Dash_Mezcla")
foreach ($pvt in $wsMezcla.PivotTables()) {
    Write-Host "PT: $($pvt.Name)"
    Write-Host "  Source: $($pvt.PivotCache().SourceData)"
    Write-Host "  TableRange2: $($pvt.TableRange2.Address)"
    Write-Host "  Fields:"
    foreach ($f in $pvt.PivotFields()) {
        Write-Host "    $($f.Name) orient=$($f.Orientation)"
    }
}

# Intentar actualizar manualmente el source del cache compartido
# Todos los PT que comparten el cache 1 deberían actualizarse con una sola línea
$cache1 = $wbTarget.PivotCaches().Item(1)
Write-Host "`nCache 1 source: $($cache1.SourceData)"
$newSrc = "Base_Datos!R1C1:R" + $lastRow + "C15"

# Intentar via el objeto Cache directamente via recordset approach
try {
    $cache1.SourceData = $newSrc
    Write-Host "Cache 1 source actualizado a $newSrc"
} catch {
    Write-Host "Error directo: $_"
}

# Refrescar todas las PT una por una
foreach ($sh in $wbTarget.Worksheets) {
    foreach ($pvt in $sh.PivotTables()) {
        try { $pvt.PivotCache().Refresh(); Write-Host "Refreshed: $($sh.Name)/$($pvt.Name)" }
        catch { Write-Host "Err refresh $($sh.Name)/$($pvt.Name): $_" }
    }
}

$wbTarget.Save()
$wbTarget.Close($false)
$excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
Write-Host "Done"
