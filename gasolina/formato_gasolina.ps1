$ErrorActionPreference = 'Stop'
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

$baseDir = "C:\Users\JOSE\Desktop\Proyecto fenix\gasolina\"
$targetPath = $baseDir + "Maestro_Conciliacion_Gasolina.xlsx"

if (-not (Test-Path $targetPath)) {
    Write-Host "No se encontró el archivo $targetPath"
    exit 1
}

$wb = $excel.Workbooks.Open($targetPath)

# 1. Eliminar la hoja estática generada por pandas si existe
foreach ($sheet in $wb.Sheets) {
    if ($sheet.Name -eq "tabla de evaluacion") {
        $sheet.Delete()
        break
    }
}

# 2. Formatear las hojas de datos
$dataSheets = @("base de datos consolidada", "catalogos", "autorizaciones por unidad", "gasolineria levet", "gasolineria huixquilucan")
$wsBase = $null

foreach ($sheetName in $dataSheets) {
    $ws = $null
    try { $ws = $wb.Worksheets.Item($sheetName) } catch { }
    if ($ws -ne $null) {
        if ($sheetName -eq "base de datos consolidada") { $wsBase = $ws }
        if ($sheetName -eq "autorizaciones por unidad") { $wsAuth = $ws }
        
        $lastCol = $ws.UsedRange.Columns.Count
        if ($lastCol -gt 0) {
            $headerRange = $ws.Range($ws.Cells.Item(1, 1), $ws.Cells.Item(1, $lastCol))
            $headerRange.Font.Bold = $true
            $headerRange.Interior.Color = 14277081
            
            $ws.UsedRange.Columns.AutoFit() | Out-Null
            $ws.UsedRange.AutoFilter() | Out-Null
        }
    }
}

# Formato de moneda específico para Base Consolidada
if ($wsBase -ne $null) {
    # IMPORTE_DE_CARGA (Col 9) y IMPORTE SEMANAL AUTORIZADO (Col 11)
    $wsBase.Columns.Item(9).NumberFormat = "$#,##0.00"
    $wsBase.Columns.Item(11).NumberFormat = "$#,##0.00"
}

# 3. Crear Dashboard y Tablas Dinámicas
if ($wsBase -ne $null) {
    # Buscar si ya existe el Dash y eliminarlo
    foreach ($sheet in $wb.Sheets) {
        if ($sheet.Name -eq "Dash_Gasolina") { $sheet.Delete(); break }
    }
    
    $wsDash = $wb.Worksheets.Add($wb.Worksheets.Item(1))
    $wsDash.Name = "Dash_Gasolina"
    
    $lastRow = $wsBase.UsedRange.Rows.Count
    $lastCol = $wsBase.UsedRange.Columns.Count
    $dataRangeStr = "base de datos consolidada!R1C1:R" + $lastRow + "C" + $lastCol
    $pc = $wb.PivotCaches().Create(1, $dataRangeStr, 6)
    
    $lastRowAuth = $wsAuth.UsedRange.Rows.Count
    $lastColAuth = $wsAuth.UsedRange.Columns.Count
    $authRangeStr = "'autorizaciones por unidad'!R1C1:R" + $lastRowAuth + "C" + $lastColAuth
    $pcAuth = $wb.PivotCaches().Create(1, $authRangeStr, 6)
    
    # == PT GASOLINERIAS ==
    $wsDash.Cells.Item(1, 2) = "GASTOS TOTALES POR GASOLINERA"
    $wsDash.Cells.Item(1, 2).Font.Bold = $true
    
    $pt1 = $pc.CreatePivotTable("Dash_Gasolina!R4C2", "PT_Gasolinerias")
    $pt1.PivotFields("GASOLINERA_ORIGEN").Orientation = 1
    
    $df1 = $pt1.AddDataField($pt1.PivotFields("IMPORTE_DE_CARGA"), "Total Gasto ", -4157) # -4157 = xlSum
    $df1.NumberFormat = "$#,##0.00"
    $pt1.TableStyle2 = "PivotStyleMedium9"
    $pt1.RowAxisLayout(1)
    $pt1.HasAutoFormat = $false
    
    # == PT SALDOS POR UNIDAD ==
    $wsDash.Cells.Item(1, 6) = "CONSUMOS Y SALDOS POR UNIDAD"
    $wsDash.Cells.Item(1, 6).Font.Bold = $true
    
    $pt2 = $pcAuth.CreatePivotTable("Dash_Gasolina!R4C6", "PT_Saldos_Unidad")
    $pt2.PivotFields("CENTRO DE TRABAJO").Orientation = 1
    $pt2.PivotFields("PLACAS").Orientation = 1
    
    # Sum(Importe Autorizado)
    $df2_1 = $pt2.AddDataField($pt2.PivotFields("IMPORTE SEMANAL AUTORIZADO"), "Monto Autorizado ", -4157) # -4157 = xlSum
    $df2_1.NumberFormat = "$#,##0.00"
    
    # Sum(Consumo Real)
    $df2_2 = $pt2.AddDataField($pt2.PivotFields("CONSUMO_REAL"), "Consumo Real ", -4157)
    $df2_2.NumberFormat = "$#,##0.00"
    
    # Sum(Saldo)
    $df2_3 = $pt2.AddDataField($pt2.PivotFields("SALDO_RESTANTE"), "Saldo ", -4157)
    $df2_3.NumberFormat = "$#,##0.00"
    
    $pt2.TableStyle2 = "PivotStyleMedium14"
    $pt2.RowAxisLayout(1)
    $pt2.HasAutoFormat = $false
    
    # Ajuste de columnas
    $wsDash.Columns.Item(2).ColumnWidth = 20
    $wsDash.Columns.Item(3).ColumnWidth = 15
    $wsDash.Columns.Item(6).ColumnWidth = 15
    $wsDash.Columns.Item(7).ColumnWidth = 18
    $wsDash.Columns.Item(8).ColumnWidth = 18
    $wsDash.Columns.Item(9).ColumnWidth = 18
}

$wb.Save()
$wb.Close($false)
$excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
Write-Host "Formato corporativo y tablas dinámicas aplicados exitosamente a Gasolina."
