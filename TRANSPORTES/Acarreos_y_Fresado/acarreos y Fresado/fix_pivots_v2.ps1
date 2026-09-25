$ErrorActionPreference = 'Stop'
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

$targetPath = "c:\Users\JOSE\Desktop\Proyecto fenix\acarreos y Fresado\GC-MAT-1.0_Maestro_Consolidado_V12.xlsx"
$wbTarget = $excel.Workbooks.Open($targetPath)
$wsBase = $wbTarget.Worksheets.Item("Base_Datos")
$lastRow = $wsBase.UsedRange.Rows.Count
Write-Host "Total filas en Base_Datos: $lastRow"

# Nuevo rango como objeto Range (no string) para el PivotCache
$newRangeObj = $wsBase.Range("A1:O" + $lastRow)

# Reemplazar cada tabla dinamica recreandola con el nuevo cache
$sheetsToPT = @{}
foreach ($sh in $wbTarget.Worksheets) {
    foreach ($pvt in $sh.PivotTables()) {
        if (-not $sheetsToPT.ContainsKey($sh.Name)) { $sheetsToPT[$sh.Name] = @() }
        $sheetsToPT[$sh.Name] += $pvt.Name
    }
}

# Crear un nuevo PivotCache con el rango completo
$newPC = $wbTarget.PivotCaches().Create(1, $newRangeObj, 6)

# Cambiar el cache de todas las tablas dinamicas existentes
foreach ($sh in $wbTarget.Worksheets) {
    foreach ($pvt in $sh.PivotTables()) {
        try {
            $pvt.ChangePivotCache($newPC)
            $pvt.PivotCache().Refresh()
            Write-Host "Actualizada: $($sh.Name)/$($pvt.Name)"
        } catch {
            Write-Host "Error en $($sh.Name)/$($pvt.Name): $_"
        }
    }
}

# Agregar pestaña AGUA si no existe
$aguaExists = $false
foreach ($sh in $wbTarget.Worksheets) {
    if ($sh.Name -eq "Dash_Agua") { $aguaExists = $true; break }
}

if (-not $aguaExists) {
    # Agregar hoja antes de Base_Datos
    $wsBaseRef = $wbTarget.Worksheets.Item("Base_Datos")
    $wsAgua = $wbTarget.Worksheets.Add($wsBaseRef)
    $wsAgua.Name = "Dash_Agua"

    # Titulo
    $wsAgua.Cells.Item(1, 2) = "PIPAS DE AGUA"
    $wsAgua.Cells.Item(1, 2).Font.Bold = $true
    $wsAgua.Cells.Item(1, 2).Font.Size = 14
    $wsAgua.Cells.Item(1, 2).Interior.Color = 15773696  # azul agua

    $wsAgua.Cells.Item(3, 2) = "Se actualizará automáticamente al capturar viajes con CATEGORIA=AGUA en la Base de Datos"
    $wsAgua.Cells.Item(3, 2).Font.Italic = $true

    # Tabla dinamica detalle por fecha
    try {
        $ptAgua = $newPC.CreatePivotTable("Dash_Agua!R6C2", "PT_Agua")
        $ptAgua.PivotFields("FECHA").Orientation = 1
        $ptAgua.PivotFields("OBRA").Orientation = 1
        $ptAgua.PivotFields("SINDICATO").Orientation = 1
        $ptAgua.AddDataField($ptAgua.PivotFields("FOLIO"), "Viajes Agua", -4112) | Out-Null
        $ptAgua.PivotFields("CATEGORIA").Orientation = 3
        try { $ptAgua.PivotFields("CATEGORIA").CurrentPage = "AGUA" } catch {}
        $ptAgua.PivotFields("SEMANA").Orientation = 3
        $ptAgua.TableStyle2 = "PivotStyleMedium14"
        $ptAgua.RowAxisLayout(1)
        $ptAgua.HasAutoFormat = $false

        # Tabla por sindicato
        $ptAguaS = $newPC.CreatePivotTable("Dash_Agua!R6C10", "PT_Agua_Sind")
        $ptAguaS.PivotFields("SINDICATO").Orientation = 1
        $ptAguaS.AddDataField($ptAguaS.PivotFields("FOLIO"), "Viajes Tot Agua", -4112) | Out-Null
        $ptAguaS.PivotFields("CATEGORIA").Orientation = 3
        try { $ptAguaS.PivotFields("CATEGORIA").CurrentPage = "AGUA" } catch {}
        $ptAguaS.PivotFields("SEMANA").Orientation = 3
        $ptAguaS.TableStyle2 = "PivotStyleMedium9"
        $ptAguaS.RowAxisLayout(1)
        $ptAguaS.HasAutoFormat = $false
        Write-Host "Dash_Agua creada OK"
    } catch {
        Write-Host "Error Dash_Agua PT: $_"
    }
}

$wbTarget.Save()
$wbTarget.Close($false)
$excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
Write-Host "COMPLETADO"
