$ErrorActionPreference = 'Stop'
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

$targetPath = "c:\Users\JOSE\Desktop\Proyecto fenix\acarreos y Fresado\GC-MAT-1.0_Maestro_Consolidado_V12.xlsx"
$wbTarget = $excel.Workbooks.Open($targetPath)
$wsBase = $wbTarget.Worksheets.Item("Base_Datos")
$lastRow = $wsBase.UsedRange.Rows.Count
Write-Host "Total filas en Base_Datos: $lastRow"

# Nuevo rango de datos para PivotCache
$newSource = "Base_Datos!R1C1:R" + $lastRow + "C15"
Write-Host "Nuevo source: $newSource"

# Actualizar el PivotCache de TODAS las tablas dinamicas
$cacheUpdated = @{}
foreach ($sh in $wbTarget.Worksheets) {
    foreach ($pvt in $sh.PivotTables()) {
        $cacheId = $pvt.PivotCache().Index
        if (-not $cacheUpdated.ContainsKey($cacheId)) {
            $pvt.PivotCache().SourceData = $newSource
            $cacheUpdated[$cacheId] = $true
            Write-Host "Cache $cacheId actualizado"
        }
        $pvt.PivotCache().Refresh()
        Write-Host "Tabla $($pvt.Name) en $($sh.Name) refrescada"
    }
}

# Agregar pestaña AGUA si no existe
$aguaExists = $false
foreach ($sh in $wbTarget.Worksheets) {
    if ($sh.Name -eq "Dash_Agua") { $aguaExists = $true; break }
}

if (-not $aguaExists) {
    $wsAgua = $wbTarget.Worksheets.Add()
    $wsAgua.Name = "Dash_Agua"
    $wsAgua.Cells.Item(1, 2) = "PIPAS DE AGUA"
    $wsAgua.Cells.Item(1, 2).Font.Bold = $true
    $wsAgua.Cells.Item(1, 2).Font.Size = 14

    # Nota informativa
    $wsAgua.Cells.Item(3, 2) = "Esta pestaña mostrará el concentrado de Pipas de Agua una vez que se capturen los viajes en la Base de Datos."
    $wsAgua.Cells.Item(3, 2).Font.Italic = $true
    $wsAgua.Cells.Item(4, 2) = "Categoría a usar: AGUA | Los viajes se capturan en CAPTURA DE ACARREOS 2026.xlsx"
    $wsAgua.Cells.Item(4, 2).Font.Italic = $true

    # Crear tabla dinamica para AGUA (mostrará vacía hasta que haya datos con CATEGORIA=AGUA)
    # Primero asegurarnos que existe la categoria AGUA en Base_Datos escribiendo un placeholder
    # Solo crear la PT
    try {
        $pc = $wbTarget.PivotCaches().Create(1, $newSource, 6)
        $ptAgua = $pc.CreatePivotTable("Dash_Agua!R6C2", "PT_Agua")
        $ptAgua.PivotFields("FECHA").Orientation = 1
        $ptAgua.PivotFields("OBRA").Orientation = 1
        $ptAgua.PivotFields("SINDICATO").Orientation = 1
        $df = $ptAgua.AddDataField($ptAgua.PivotFields("FOLIO"), "Viajes Agua", -4112)
        $ptAgua.PivotFields("CATEGORIA").Orientation = 3
        $ptAgua.PivotFields("CATEGORIA").CurrentPage = "AGUA"
        $ptAgua.PivotFields("SEMANA").Orientation = 3
        $ptAgua.TableStyle2 = "PivotStyleMedium14"
        $ptAgua.RowAxisLayout(1)
        $ptAgua.HasAutoFormat = $false

        # Tabla por sindicato
        $ptAguaS = $pc.CreatePivotTable("Dash_Agua!R6C10", "PT_Agua_Sind")
        $ptAguaS.PivotFields("SINDICATO").Orientation = 1
        $dfS = $ptAguaS.AddDataField($ptAguaS.PivotFields("FOLIO"), "Viajes Tot Agua", -4112)
        $ptAguaS.PivotFields("CATEGORIA").Orientation = 3
        $ptAguaS.PivotFields("CATEGORIA").CurrentPage = "AGUA"
        $ptAguaS.PivotFields("SEMANA").Orientation = 3
        $ptAguaS.TableStyle2 = "PivotStyleMedium9"
        $ptAguaS.RowAxisLayout(1)
        $ptAguaS.HasAutoFormat = $false

        Write-Host "Pestaña Dash_Agua creada con tablas dinamicas"
    } catch {
        Write-Host "Tabla dinamica Agua: $_"
    }

    # Mover Agua antes de Base_Datos
    $wsBase = $wbTarget.Worksheets.Item("Base_Datos")
    $wsAgua.Move($wsBase)
}

$wbTarget.Save()
$wbTarget.Close($false)
$excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
Write-Host "COMPLETADO: Tablas dinamicas corregidas a $lastRow filas + Dash_Agua agregada"
