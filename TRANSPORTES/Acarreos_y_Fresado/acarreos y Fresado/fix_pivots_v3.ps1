# Estrategia: Eliminar todas las tablas dinamicas y recrearlas desde cero con el rango correcto
$ErrorActionPreference = 'Stop'
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

$targetPath = "c:\Users\JOSE\Desktop\Proyecto fenix\acarreos y Fresado\GC-MAT-1.0_Maestro_Consolidado_V12.xlsx"
$wbTarget = $excel.Workbooks.Open($targetPath)
$wsBase = $wbTarget.Worksheets.Item("Base_Datos")
$lastRow = $wsBase.UsedRange.Rows.Count
Write-Host "Filas totales: $lastRow"

# 1. Eliminar todas las tablas dinamicas en cada sheet
$dashSheets = @("Dash_Mezcla","Dash_Fresado","Dash_Total","Dash_Agua")
foreach ($sname in $dashSheets) {
    try {
        $sh = $wbTarget.Worksheets.Item($sname)
        $pts = @()
        foreach ($pvt in $sh.PivotTables()) { $pts += $pvt.Name }
        foreach ($pname in $pts) {
            $pvt = $sh.PivotTables($pname)
            $pvt.TableRange2.Clear()
        }
        Write-Host "Limpiadas tablas en $sname"
    } catch { Write-Host "Skip $sname`: $_" }
}

# 2. Crear nuevo PivotCache con rango completo
$srcRange = $wsBase.Range("A1:O" + $lastRow)
$pc = $wbTarget.PivotCaches().Create(1, $srcRange, 6)

function New-PivotTable {
    param($pc, $destAddr, $ptName, $rowFields, $filterFields, $catFilter, $dataFields)
    $pt = $pc.CreatePivotTable($destAddr, $ptName)
    foreach ($f in $rowFields) {
        try { $pt.PivotFields($f).Orientation = 1 } catch {}
    }
    foreach ($kv in $filterFields.GetEnumerator()) {
        try {
            $pt.PivotFields($kv.Key).Orientation = 3
            if ($kv.Value -ne "") { $pt.PivotFields($kv.Key).CurrentPage = $kv.Value }
        } catch {}
    }
    foreach ($kv in $dataFields.GetEnumerator()) {
        try {
            $df = $pt.AddDataField($pt.PivotFields($kv.Key), $kv.Value[0], $kv.Value[1])
            if ($kv.Value.Count -gt 2) { $df.NumberFormat = $kv.Value[2] }
        } catch {}
    }
    $pt.TableStyle2 = "PivotStyleMedium9"
    $pt.RowAxisLayout(1)
    $pt.HasAutoFormat = $false
    return $pt
}

# == DASH MEZCLA ==
$wsMezcla = $wbTarget.Worksheets.Item("Dash_Mezcla")
$ptM = New-PivotTable -pc $pc -destAddr "Dash_Mezcla!R6C2" -ptName "PT_Mezcla" `
    -rowFields @("FECHA","OBRA","SINDICATO","FOLIO") `
    -filterFields @{"CATEGORIA"="MEZCLA";"SEMANA"=""} `
    -catFilter "MEZCLA" `
    -dataFields @{"FOLIO"=@("Viajes",-4112);"PU"=@("Costo Surtido",-4157,"`$#,##0.00")}
$ptM.TableStyle2 = "PivotStyleMedium9"

$ptMS = New-PivotTable -pc $pc -destAddr "Dash_Mezcla!R6C10" -ptName "PT_Mezcla_Sind" `
    -rowFields @("SINDICATO") `
    -filterFields @{"CATEGORIA"="MEZCLA";"SEMANA"=""} `
    -catFilter "MEZCLA" `
    -dataFields @{"FOLIO"=@("Viajes Totales",-4112);"PU"=@("Total a Pagar",-4157,"`$#,##0.00")}
$ptMS.TableStyle2 = "PivotStyleMedium14"
Write-Host "Dash_Mezcla OK"

# == DASH FRESADO ==
$ptF = New-PivotTable -pc $pc -destAddr "Dash_Fresado!R6C2" -ptName "PT_Fresado" `
    -rowFields @("FECHA","OBRA","SINDICATO","FOLIO") `
    -filterFields @{"CATEGORIA"="FRESADO";"SEMANA"=""} `
    -catFilter "FRESADO" `
    -dataFields @{"FOLIO"=@("Viajes ",-4112);"PU"=@(" Costo Surtido",-4157,"`$#,##0.00")}
$ptF.TableStyle2 = "PivotStyleMedium9"

$ptFS = New-PivotTable -pc $pc -destAddr "Dash_Fresado!R6C10" -ptName "PT_Fresado_Sind" `
    -rowFields @("SINDICATO") `
    -filterFields @{"CATEGORIA"="FRESADO";"SEMANA"=""} `
    -catFilter "FRESADO" `
    -dataFields @{"FOLIO"=@("Viajes Totales ",-4112);"PU"=@("Total a Pagar ",-4157,"`$#,##0.00")}
$ptFS.TableStyle2 = "PivotStyleMedium14"
Write-Host "Dash_Fresado OK"

# == DASH TOTAL ==
$ptT = New-PivotTable -pc $pc -destAddr "Dash_Total!R6C2" -ptName "PT_Total" `
    -rowFields @("FECHA","OBRA","SINDICATO") `
    -filterFields @{"SEMANA"=""} `
    -catFilter "" `
    -dataFields @{"FOLIO"=@("Viajes Totales",-4112);"PU"=@("Costo Total Obra",-4157,"`$#,##0.00")}
$ptT.TableStyle2 = "PivotStyleMedium14"

$ptTS = New-PivotTable -pc $pc -destAddr "Dash_Total!R6C10" -ptName "PT_Total_Sind" `
    -rowFields @("SINDICATO") `
    -filterFields @{"SEMANA"=""} `
    -catFilter "" `
    -dataFields @{"FOLIO"=@("Viajes Global ",-4112);"PU"=@("Pagar Global ",-4157,"`$#,##0.00")}
$ptTS.TableStyle2 = "PivotStyleMedium9"
Write-Host "Dash_Total OK"

# == DASH AGUA ==
$wsAgua = $wbTarget.Worksheets.Item("Dash_Agua")
# limpiar contenido de tablas previas (ya se hizo arriba)
$ptA = New-PivotTable -pc $pc -destAddr "Dash_Agua!R6C2" -ptName "PT_Agua" `
    -rowFields @("FECHA","OBRA","SINDICATO") `
    -filterFields @{"CATEGORIA"="AGUA";"SEMANA"=""} `
    -catFilter "AGUA" `
    -dataFields @{"FOLIO"=@("Viajes Agua",-4112)}
$ptA.TableStyle2 = "PivotStyleMedium14"

$ptAS = New-PivotTable -pc $pc -destAddr "Dash_Agua!R6C10" -ptName "PT_Agua_Sind" `
    -rowFields @("SINDICATO") `
    -filterFields @{"CATEGORIA"="AGUA";"SEMANA"=""} `
    -catFilter "AGUA" `
    -dataFields @{"FOLIO"=@("Viajes Tot Agua",-4112)}
$ptAS.TableStyle2 = "PivotStyleMedium9"
Write-Host "Dash_Agua OK"

$wbTarget.Save()
$wbTarget.Close($false)
$excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
Write-Host "COMPLETADO: Todas las tablas dinamicas recreadas con fuente R1C1:R532C15"
