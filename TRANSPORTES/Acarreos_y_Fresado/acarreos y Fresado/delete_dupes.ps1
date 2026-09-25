$ErrorActionPreference = 'Stop'
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

$targetPath = "c:\Users\JOSE\Desktop\Proyecto fenix\acarreos y Fresado\GC-MAT-1.0_Maestro_Consolidado_V12.xlsx"
$wbTarget = $excel.Workbooks.Open($targetPath)
$wsBase = $wbTarget.Worksheets.Item("Base_Datos")

$lastRow = $wsBase.UsedRange.Rows.Count
Write-Host "Filas antes: $lastRow"

# Eliminar filas 324 a 410 (87 filas de duplicados de L3M Semana 25)
$wsBase.Rows("324:410").Delete() | Out-Null

$newLastRow = $wsBase.UsedRange.Rows.Count
Write-Host "Filas despues: $newLastRow"

# Refrescar tablas dinamicas para que el nuevo caché actualice sus totales
foreach ($sh in $wbTarget.Worksheets) {
    foreach ($pvt in $sh.PivotTables()) {
        try { $pvt.PivotCache().Refresh() } catch {}
    }
}

$wbTarget.Save()
$wbTarget.Close($false)
$excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
Write-Host "Duplicados eliminados exitosamente."
