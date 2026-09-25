$ErrorActionPreference = 'Stop'
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

$targetPath = "c:\Users\JOSE\Desktop\Proyecto fenix\acarreos y Fresado\GC-MAT-1.0_Maestro_Consolidado_V12.xlsx"
$wbTarget = $excel.Workbooks.Open($targetPath)
$wsBase = $wbTarget.Worksheets.Item("Base_Datos")
$lastRow = $wsBase.UsedRange.Rows.Count
$changed = 0

for ($r = 2; $r -le $lastRow; $r++) {
    $obra  = $wsBase.Cells.Item($r, 5).Text.Trim().ToUpper()
    $sind  = $wsBase.Cells.Item($r, 4).Text.Trim().ToUpper()
    $cat   = $wsBase.Cells.Item($r, 15).Text.Trim().ToUpper()

    if ($obra -eq "MEXICO-TOLUCA" -and $sind -eq "COSUM TOLUCA") {
        # Cambiar sindicato
        $wsBase.Cells.Item($r, 4) = "COSUM-HUIXQUILUCAN"

        # Recalcular precio: Fresado Huixquilucan = $2,500, Mezcla = $2,850
        $pu = 0
        if ($cat -eq "MEZCLA")  { $pu = 2850 }
        elseif ($cat -eq "FRESADO") { $pu = 2500 }

        if ($pu -gt 0) {
            $sub  = $pu
            $iva  = $sub * 0.16
            $tot  = $sub + $iva
            $wsBase.Cells.Item($r, 11) = $pu
            $wsBase.Cells.Item($r, 12) = $sub
            $wsBase.Cells.Item($r, 13) = $iva
            $wsBase.Cells.Item($r, 14) = $tot
        }
        $changed++
    }
}

Write-Host "Registros actualizados: $changed"

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
Write-Host "Listo. Sindicato MEXICO-TOLUCA actualizado a COSUM-HUIXQUILUCAN con precios correctos."
