$ErrorActionPreference = 'Stop'
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

$baseDir = "c:\Users\JOSE\Desktop\Proyecto fenix\acarreos y Fresado\"
$targetPath = $baseDir + "GC-MAT-1.0_Maestro_Consolidado_V12.xlsx"

$wbTarget = $excel.Workbooks.Open($targetPath)
$wsBase = $wbTarget.Worksheets.Item("Base_Datos")

# Borrar filas 324 en adelante (las 48 que se inyectaron)
$lastRow = $wsBase.UsedRange.Rows.Count
Write-Host "Filas actuales: $lastRow"

if ($lastRow -gt 323) {
    $wsBase.Rows("324:" + $lastRow).Delete() | Out-Null
    Write-Host "Eliminadas filas 324 a $lastRow"
}

Write-Host "Filas tras deshacer: $($wsBase.UsedRange.Rows.Count)"

# Revisar los 2 archivos nuevos
$files = @(
    "CAPTURA DE ACARREOS POR SEMANA L3M FRESADO.xlsx",
    "CAPTURA DE ACARREOS (SEM # 26) OBRA MEX-TOL.xlsx"
)
foreach ($fn in $files) {
    $path = $baseDir + $fn
    if (Test-Path $path) {
        $wb = $excel.Workbooks.Open($path)
        Write-Host "`n=== $fn ==="
        foreach ($sh in $wb.Worksheets) { Write-Host "  Sheet: $($sh.Name)" }
        $ws = $wb.Worksheets.Item(1)
        Write-Host "  Filas: $($ws.UsedRange.Rows.Count), Cols: $($ws.UsedRange.Columns.Count)"
        for ($r = 1; $r -le [Math]::Min(8, $ws.UsedRange.Rows.Count); $r++) {
            $row = "R$r`: "
            for ($c = 1; $c -le [Math]::Min(22, $ws.UsedRange.Columns.Count); $c++) {
                $val = $ws.Cells.Item($r,$c).Text
                if ($val.Length -gt 0) { $row += "C$c=[$($val.Substring(0,[Math]::Min(14,$val.Length)))] " }
            }
            Write-Host "  $row"
        }
        $wb.Close($false)
    } else {
        Write-Host "$fn NO encontrado"
    }
}

$wbTarget.Save()
$wbTarget.Close($false)
$excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
Write-Host "`nDeshacer completado. Base_Datos restaurada a 323 filas."
