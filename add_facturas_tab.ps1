$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

$filePath = "c:\Users\JOSE\Desktop\Proyecto fenix\MAESTRO_CONTROL_DIESEL_NUEVO.xlsx"
$workbook = $excel.Workbooks.Open($filePath)

# Verificar si ya existe la hoja, si no, crearla
$sheetExists = $false
foreach ($sheet in $workbook.Worksheets) {
    if ($sheet.Name -eq "BD_FACTURAS") {
        $sheetExists = $true
        break
    }
}

if (-not $sheetExists) {
    # Agregar hoja al final
    $newSheet = $workbook.Worksheets.Add([System.Reflection.Missing]::Value, $workbook.Worksheets.Item($workbook.Worksheets.Count))
    $newSheet.Name = "BD_FACTURAS"
    
    # Encabezados
    $newSheet.Cells.Item(1,1) = "FOLIO_FACTURA"
    $newSheet.Cells.Item(1,2) = "FECHA_FACTURA"
    $newSheet.Cells.Item(1,3) = "SEMANA"
    $newSheet.Cells.Item(1,4) = "PROVEEDOR"
    $newSheet.Cells.Item(1,5) = "PUNTO_DE_CARGA"
    $newSheet.Cells.Item(1,6) = "LITROS_FACTURADOS"
    $newSheet.Cells.Item(1,7) = "PRECIO_UNITARIO"
    $newSheet.Cells.Item(1,8) = "IMPORTE_TOTAL"
    $newSheet.Cells.Item(1,9) = "TIPO_COMBUSTIBLE"
    $newSheet.Cells.Item(1,10) = "ESTATUS_CONCILIACION"

    $range = $newSheet.Range("A1:J1")
    $range.Font.Bold = $true
    $range.Interior.ColorIndex = 15
    $newSheet.UsedRange.Columns.AutoFit() | Out-Null
}

$workbook.Save()
$workbook.Close()
$excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
