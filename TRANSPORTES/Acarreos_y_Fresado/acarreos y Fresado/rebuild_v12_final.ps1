$ErrorActionPreference = 'Stop'
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

$baseDir = "c:\Users\JOSE\Desktop\Proyecto fenix\acarreos y Fresado\"
$backupPath = $baseDir + "GC-MAT-1.0_Maestro_Consolidado_V12_backup.xlsx"
$destPath   = $baseDir + "GC-MAT-1.0_Maestro_Consolidado_V12.xlsx"

# Leer desde backup
$wbSrc = $excel.Workbooks.Open($backupPath)
$wsSrc = $wbSrc.Worksheets.Item("Base_Datos")
$lastRow = $wsSrc.UsedRange.Rows.Count
Write-Host "Copiando $lastRow filas"

$wbNew = $excel.Workbooks.Add()
while ($wbNew.Worksheets.Count -gt 1) { $wbNew.Worksheets.Item($wbNew.Worksheets.Count).Delete() }

$wsDashTotal   = $wbNew.Worksheets.Item(1); $wsDashTotal.Name   = "Dash_Total"
$wsDashFresado = $wbNew.Worksheets.Add($wsDashTotal);  $wsDashFresado.Name = "Dash_Fresado"
$wsDashMezcla  = $wbNew.Worksheets.Add($wsDashFresado); $wsDashMezcla.Name = "Dash_Mezcla"
$wsDashAgua    = $wbNew.Worksheets.Add($wsDashMezcla);  $wsDashAgua.Name   = "Dash_Agua"
$wsBase        = $wbNew.Worksheets.Add()
$wsBase.Name   = "Base_Datos"
$wsBase.Move([System.Reflection.Missing]::Value, $wsDashTotal)

$wsSrc.Range("A1:O" + $lastRow).Copy($wsBase.Range("A1")) | Out-Null
Write-Host "Datos copiados"
$wbSrc.Close($false)

foreach ($c in @(11,12,13,14)) { $wsBase.Columns.Item($c).NumberFormat = "`$#,##0.00" }
$wsBase.Range("A1:O1").AutoFilter() | Out-Null

$srcRange = $wsBase.Range("A1:O" + $lastRow)
$pc = $wbNew.PivotCaches().Create(1, $srcRange, 6)

function Add-PT {
    param($pc,$dest,$name,$rows,$filters,$datas,$style)
    $pt = $pc.CreatePivotTable($dest,$name)
    foreach ($r in $rows) { try { $pt.PivotFields($r).Orientation = 1 } catch {} }
    foreach ($kv in $filters.GetEnumerator()) {
        try { $pt.PivotFields($kv.Key).Orientation = 3; if($kv.Value -ne "") { $pt.PivotFields($kv.Key).CurrentPage = $kv.Value } } catch {}
    }
    foreach ($kv in $datas.GetEnumerator()) {
        try {
            $df = $pt.AddDataField($pt.PivotFields($kv.Key),$kv.Value[0],$kv.Value[1])
            if($kv.Value.Count -gt 2) { $df.NumberFormat = $kv.Value[2] }
        } catch {}
    }
    $pt.TableStyle2 = $style; $pt.RowAxisLayout(1); $pt.HasAutoFormat = $false
    return $pt
}

$wsDashMezcla.Cells.Item(1,2)  = "MEZCLA ASFÁLTICA";  $wsDashMezcla.Cells.Item(1,2).Font.Bold  = $true; $wsDashMezcla.Cells.Item(1,2).Font.Size  = 14
$wsDashFresado.Cells.Item(1,2) = "FRESADO";           $wsDashFresado.Cells.Item(1,2).Font.Bold = $true; $wsDashFresado.Cells.Item(1,2).Font.Size = 14
$wsDashTotal.Cells.Item(1,2)   = "TOTAL GENERAL";     $wsDashTotal.Cells.Item(1,2).Font.Bold   = $true; $wsDashTotal.Cells.Item(1,2).Font.Size   = 14
$wsDashAgua.Cells.Item(1,2)    = "PIPAS DE AGUA";     $wsDashAgua.Cells.Item(1,2).Font.Bold    = $true; $wsDashAgua.Cells.Item(1,2).Font.Size    = 14
$wsDashAgua.Cells.Item(3,2)    = "Se llenará al capturar viajes con CATEGORIA=AGUA en la Base de Datos"
$wsDashAgua.Cells.Item(3,2).Font.Italic = $true

Add-PT $pc "Dash_Mezcla!R6C2"  "PT_Mezcla"      @("FECHA","OBRA","SINDICATO","FOLIO") @{"CATEGORIA"="MEZCLA";"SEMANA"=""}  @{"FOLIO"=@("Viajes",-4112);"PU"=@("Costo Surtido",-4157,"`$#,##0.00")} "PivotStyleMedium9" | Out-Null
Add-PT $pc "Dash_Mezcla!R6C10" "PT_Mezcla_Sind" @("SINDICATO")                       @{"CATEGORIA"="MEZCLA";"SEMANA"=""}  @{"FOLIO"=@("Viajes Totales",-4112);"PU"=@("Total a Pagar",-4157,"`$#,##0.00")} "PivotStyleMedium14" | Out-Null
Write-Host "Dash_Mezcla OK"

Add-PT $pc "Dash_Fresado!R6C2"  "PT_Fresado"      @("FECHA","OBRA","SINDICATO","FOLIO") @{"CATEGORIA"="FRESADO";"SEMANA"=""} @{"FOLIO"=@("Viajes ",-4112);"PU"=@(" Costo Surtido",-4157,"`$#,##0.00")} "PivotStyleMedium9" | Out-Null
Add-PT $pc "Dash_Fresado!R6C10" "PT_Fresado_Sind" @("SINDICATO")                       @{"CATEGORIA"="FRESADO";"SEMANA"=""} @{"FOLIO"=@("Viajes Totales ",-4112);"PU"=@("Total a Pagar ",-4157,"`$#,##0.00")} "PivotStyleMedium14" | Out-Null
Write-Host "Dash_Fresado OK"

Add-PT $pc "Dash_Total!R6C2"  "PT_Total"      @("FECHA","OBRA","SINDICATO") @{"SEMANA"=""} @{"FOLIO"=@("Viajes Totales",-4112);"PU"=@("Costo Total",-4157,"`$#,##0.00")} "PivotStyleMedium14" | Out-Null
Add-PT $pc "Dash_Total!R6C10" "PT_Total_Sind" @("SINDICATO")                @{"SEMANA"=""} @{"FOLIO"=@("Viajes Global ",-4112);"PU"=@("Pagar Global ",-4157,"`$#,##0.00")} "PivotStyleMedium9" | Out-Null
Write-Host "Dash_Total OK"

Add-PT $pc "Dash_Agua!R6C2"  "PT_Agua"      @("FECHA","OBRA","SINDICATO") @{"CATEGORIA"="AGUA";"SEMANA"=""} @{"FOLIO"=@("Viajes Agua",-4112)} "PivotStyleMedium14" | Out-Null
Add-PT $pc "Dash_Agua!R6C10" "PT_Agua_Sind" @("SINDICATO")                @{"CATEGORIA"="AGUA";"SEMANA"=""} @{"FOLIO"=@("Viajes Tot Agua",-4112)} "PivotStyleMedium9" | Out-Null
Write-Host "Dash_Agua OK"

$wbNew.SaveAs($destPath)
$wbNew.Close($false)
$excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
Write-Host "COMPLETADO: V12 reconstruido con $lastRow filas y 4 dashboards"
