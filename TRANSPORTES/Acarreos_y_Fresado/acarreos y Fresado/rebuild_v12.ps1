$ErrorActionPreference = 'Stop'
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

$baseDir = "c:\Users\JOSE\Desktop\Proyecto fenix\acarreos y Fresado\"
$srcPath  = $baseDir + "GC-MAT-1.0_Maestro_Consolidado_V12.xlsx"
$destPath = $baseDir + "GC-MAT-1.0_Maestro_Consolidado_V12.xlsx"

# Abrir fuente para copiar la Base_Datos
$wbSrc = $excel.Workbooks.Open($srcPath)
$wsSrc = $wbSrc.Worksheets.Item("Base_Datos")
$lastRow = $wsSrc.UsedRange.Rows.Count
$lastCol = $wsSrc.UsedRange.Columns.Count
Write-Host "Copiando $lastRow filas x $lastCol cols de Base_Datos"

# Crear nuevo workbook
$wbNew = $excel.Workbooks.Add()
# Eliminar hojas extra dejando solo una
while ($wbNew.Worksheets.Count -gt 1) { $wbNew.Worksheets.Item($wbNew.Worksheets.Count).Delete() }

# Crear hojas Dashboard
$wsDashTotal  = $wbNew.Worksheets.Item(1); $wsDashTotal.Name  = "Dash_Total"
$wsDashFresado = $wbNew.Worksheets.Add($wsDashTotal); $wsDashFresado.Name = "Dash_Fresado"
$wsDashMezcla  = $wbNew.Worksheets.Add($wsDashFresado); $wsDashMezcla.Name  = "Dash_Mezcla"
$wsDashAgua    = $wbNew.Worksheets.Add($wsDashMezcla);  $wsDashAgua.Name   = "Dash_Agua"
$wsBase        = $wbNew.Worksheets.Add(); $wsBase.Name = "Base_Datos"

# Mover Base_Datos al final
$wsBase.Move([System.Reflection.Missing]::Value, $wsDashTotal)

# Copiar datos de Base_Datos
$copyRange = $wsSrc.Range("A1:O" + $lastRow)
$copyRange.Copy($wsBase.Range("A1")) | Out-Null
Write-Host "Datos copiados"

# Formato moneda
foreach ($c in @(11,12,13,14)) {
    $wsBase.Columns.Item($c).NumberFormat = "`$#,##0.00"
}
$wsBase.Range("A1:O1").AutoFilter() | Out-Null
$wsBase.UsedRange.Columns.AutoFit() | Out-Null

$wbSrc.Close($false)

# Crear PivotCache con rango completo
$srcRange = $wsBase.Range("A1:O" + $lastRow)
$pc = $wbNew.PivotCaches().Create(1, $srcRange, 6)
Write-Host "PivotCache creado, source rows: $lastRow"

function Add-PT {
    param($pc, $dest, $name, $rows, $filters, $cats, $datas, $style)
    $pt = $pc.CreatePivotTable($dest, $name)
    foreach ($r in $rows) { try { $pt.PivotFields($r).Orientation = 1 } catch {} }
    foreach ($kv in $filters.GetEnumerator()) {
        try { $pt.PivotFields($kv.Key).Orientation = 3; if($kv.Value -ne "") { $pt.PivotFields($kv.Key).CurrentPage = $kv.Value } } catch {}
    }
    foreach ($kv in $datas.GetEnumerator()) {
        try {
            $df = $pt.AddDataField($pt.PivotFields($kv.Key), $kv.Value[0], $kv.Value[1])
            if ($kv.Value.Count -gt 2) { $df.NumberFormat = $kv.Value[2] }
        } catch {}
    }
    $pt.TableStyle2 = $style
    $pt.RowAxisLayout(1)
    $pt.HasAutoFormat = $false
    return $pt
}

# Titulos
$wsDashMezcla.Cells.Item(1,2) = "MEZCLA ASFÁLTICA"; $wsDashMezcla.Cells.Item(1,2).Font.Bold = $true; $wsDashMezcla.Cells.Item(1,2).Font.Size = 14
$wsDashFresado.Cells.Item(1,2) = "FRESADO"; $wsDashFresado.Cells.Item(1,2).Font.Bold = $true; $wsDashFresado.Cells.Item(1,2).Font.Size = 14
$wsDashTotal.Cells.Item(1,2)   = "TOTAL GENERAL ACARREOS"; $wsDashTotal.Cells.Item(1,2).Font.Bold = $true; $wsDashTotal.Cells.Item(1,2).Font.Size = 14
$wsDashAgua.Cells.Item(1,2)    = "PIPAS DE AGUA"; $wsDashAgua.Cells.Item(1,2).Font.Bold = $true; $wsDashAgua.Cells.Item(1,2).Font.Size = 14
$wsDashAgua.Cells.Item(3,2)    = "Se llenará al capturar viajes con CATEGORIA=AGUA en la Base de Datos"
$wsDashAgua.Cells.Item(3,2).Font.Italic = $true

# == MEZCLA ==
Add-PT -pc $pc -dest "Dash_Mezcla!R6C2" -name "PT_Mezcla" -rows @("FECHA","OBRA","SINDICATO","FOLIO") -filters @{"CATEGORIA"="MEZCLA";"SEMANA"=""} -cats "MEZCLA" -datas @{"FOLIO"=@("Viajes",-4112);"PU"=@("Costo Surtido",-4157,"`$#,##0.00")} -style "PivotStyleMedium9" | Out-Null
Add-PT -pc $pc -dest "Dash_Mezcla!R6C10" -name "PT_Mezcla_Sind" -rows @("SINDICATO") -filters @{"CATEGORIA"="MEZCLA";"SEMANA"=""} -cats "MEZCLA" -datas @{"FOLIO"=@("Viajes Totales",-4112);"PU"=@("Total a Pagar",-4157,"`$#,##0.00")} -style "PivotStyleMedium14" | Out-Null
Write-Host "Dash_Mezcla OK"

# == FRESADO ==
Add-PT -pc $pc -dest "Dash_Fresado!R6C2" -name "PT_Fresado" -rows @("FECHA","OBRA","SINDICATO","FOLIO") -filters @{"CATEGORIA"="FRESADO";"SEMANA"=""} -cats "FRESADO" -datas @{"FOLIO"=@("Viajes ",-4112);"PU"=@(" Costo Surtido",-4157,"`$#,##0.00")} -style "PivotStyleMedium9" | Out-Null
Add-PT -pc $pc -dest "Dash_Fresado!R6C10" -name "PT_Fresado_Sind" -rows @("SINDICATO") -filters @{"CATEGORIA"="FRESADO";"SEMANA"=""} -cats "FRESADO" -datas @{"FOLIO"=@("Viajes Totales ",-4112);"PU"=@("Total a Pagar ",-4157,"`$#,##0.00")} -style "PivotStyleMedium14" | Out-Null
Write-Host "Dash_Fresado OK"

# == TOTAL ==
Add-PT -pc $pc -dest "Dash_Total!R6C2" -name "PT_Total" -rows @("FECHA","OBRA","SINDICATO") -filters @{"SEMANA"=""} -cats "" -datas @{"FOLIO"=@("Viajes Totales",-4112);"PU"=@("Costo Total Obra",-4157,"`$#,##0.00")} -style "PivotStyleMedium14" | Out-Null
Add-PT -pc $pc -dest "Dash_Total!R6C10" -name "PT_Total_Sind" -rows @("SINDICATO") -filters @{"SEMANA"=""} -cats "" -datas @{"FOLIO"=@("Viajes Global ",-4112);"PU"=@("Pagar Global ",-4157,"`$#,##0.00")} -style "PivotStyleMedium9" | Out-Null
Write-Host "Dash_Total OK"

# == AGUA ==
Add-PT -pc $pc -dest "Dash_Agua!R6C2" -name "PT_Agua" -rows @("FECHA","OBRA","SINDICATO") -filters @{"CATEGORIA"="AGUA";"SEMANA"=""} -cats "AGUA" -datas @{"FOLIO"=@("Viajes Agua",-4112)} -style "PivotStyleMedium14" | Out-Null
Add-PT -pc $pc -dest "Dash_Agua!R6C10" -name "PT_Agua_Sind" -rows @("SINDICATO") -filters @{"CATEGORIA"="AGUA";"SEMANA"=""} -cats "AGUA" -datas @{"FOLIO"=@("Viajes Tot Agua",-4112)} -style "PivotStyleMedium9" | Out-Null
Write-Host "Dash_Agua OK"

if (Test-Path $destPath) { Remove-Item $destPath -Force }
$wbNew.SaveAs($destPath)
$wbNew.Close($false)
$excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
Write-Host "COMPLETADO: GC-MAT-1.0_Maestro_Consolidado_V12.xlsx generado con $lastRow filas y 4 dashboards"
